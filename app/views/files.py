from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.database import db
from app.models import Project, File, ExcelSheet, ExcelColumn, ExcelRow
import os
import uuid
import pandas as pd
from datetime import datetime
import json
import numpy as np

files_bp = Blueprint('files', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def make_json_serializable(obj):
    """Convert pandas/numpy objects to JSON serializable types"""
    if pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, np.datetime64)):
        return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (pd.Timedelta, np.timedelta64)):
        return str(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        # Handle potential infinity and NaN values
        if np.isinf(obj) or np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.ndarray, list)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    else:
        # Convert any remaining object to string as fallback
        return str(obj) if obj is not None else None

def process_excel_file(file_path, file_record):
    """Process uploaded Excel file and store data in database"""
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_index, sheet_name in enumerate(excel_file.sheet_names):
            # Read sheet data
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Create ExcelSheet record
            excel_sheet = ExcelSheet(
                file_id=file_record.id,
                sheet_index=sheet_index,
                name=sheet_name,
                row_count=len(df),
                column_count=len(df.columns)
            )
            db.session.add(excel_sheet)
            db.session.flush()  # Get the sheet ID
            
            # Create column records
            for col_index, col_name in enumerate(df.columns):
                excel_column = ExcelColumn(
                    sheet_id=excel_sheet.id,
                    column_index=col_index,
                    name=str(col_name),
                    data_type='text'  # Could be enhanced to detect data types
                )
                db.session.add(excel_column)
            
            # Create row records (limit to first 1000 rows for performance)
            max_rows = min(len(df), 1000)
            for row_index in range(max_rows):
                row_data = df.iloc[row_index].to_dict()
                # Convert all data to JSON serializable format
                row_data = {k: make_json_serializable(v) for k, v in row_data.items()}
                
                excel_row = ExcelRow(
                    sheet_id=excel_sheet.id,
                    row_index=row_index,
                    data=row_data
                )
                db.session.add(excel_row)
        
        file_record.processing_status = 'completed'
        db.session.commit()
        return True
        
    except Exception as e:
        # Rollback the transaction first
        db.session.rollback()
        try:
            file_record.processing_status = 'error'
            db.session.commit()
        except Exception:
            db.session.rollback()
        print(f"Error processing Excel file: {str(e)}")
        return False

@files_bp.route('/upload/<uuid:project_id>', methods=['GET', 'POST'])
@login_required
def upload_file(project_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            if request.is_json:
                return jsonify({'error': 'Nessun file selezionato'}), 400
            flash('Nessun file selezionato', 'error')
            return render_template('files/upload.html', project=project)
        
        file = request.files['file']
        
        if file.filename == '':
            if request.is_json:
                return jsonify({'error': 'Nessun file selezionato'}), 400
            flash('Nessun file selezionato', 'error')
            return render_template('files/upload.html', project=project)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = file.filename.rsplit('.', 1)[1].lower()
            
            # Create file record
            file_record = File(
                project_id=project.id,
                uploader_id=current_user.id,
                filename=filename,
                original_name=file.filename,
                file_type=file_type,
                file_size=file_size,
                file_path=file_path,
                processing_status='processing'
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            # Process Excel file if applicable
            if file_type in ['xlsx', 'xls']:
                success = process_excel_file(file_path, file_record)
                if not success:
                    if request.is_json:
                        return jsonify({'error': 'Errore durante l\'elaborazione del file'}), 500
                    flash('Errore durante l\'elaborazione del file', 'error')
            else:
                file_record.processing_status = 'completed'
                db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'message': 'File caricato con successo',
                    'file': file_record.to_dict()
                }), 201
            else:
                flash('File caricato con successo!', 'success')
                return redirect(url_for('projects.view_project', project_id=project.id))
        else:
            if request.is_json:
                return jsonify({'error': 'Tipo di file non supportato'}), 400
            flash('Tipo di file non supportato', 'error')
    
    return render_template('files/upload.html', project=project)

@files_bp.route('/<uuid:file_id>')
@login_required
def view_file(file_id):
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    # Get Excel sheets if applicable
    sheets = []
    if file.file_type in ['xlsx', 'xls']:
        sheets = ExcelSheet.query.filter_by(file_id=file.id).all()
    
    if request.is_json:
        return jsonify({
            'file': file.to_dict(),
            'sheets': [s.to_dict() for s in sheets]
        })
    
    return render_template('files/view.html', file=file, sheets=sheets)

@files_bp.route('/<uuid:file_id>/sheet/<uuid:sheet_id>')
@login_required
def view_sheet(file_id, sheet_id):
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    sheet = ExcelSheet.query.filter_by(id=sheet_id, file_id=file.id).first_or_404()
    
    # Get sheet data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    rows = ExcelRow.query.filter_by(sheet_id=sheet.id)\
        .order_by(ExcelRow.row_index)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    columns = ExcelColumn.query.filter_by(sheet_id=sheet.id)\
        .order_by(ExcelColumn.column_index).all()
    
    if request.is_json:
        return jsonify({
            'file': file.to_dict(),
            'sheet': sheet.to_dict(),
            'columns': [c.to_dict() for c in columns],
            'rows': [r.to_dict() for r in rows.items],
            'pagination': {
                'page': rows.page,
                'pages': rows.pages,
                'per_page': rows.per_page,
                'total': rows.total,
                'has_next': rows.has_next,
                'has_prev': rows.has_prev
            }
        })
    
    return render_template('files/sheet.html', 
                         file=file, 
                         sheet=sheet, 
                         columns=columns, 
                         rows=rows)

@files_bp.route('/<uuid:file_id>/download')
@login_required
def download_file(file_id):
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    if os.path.exists(file.file_path):
        return send_file(file.file_path, 
                        as_attachment=True, 
                        download_name=file.original_name)
    else:
        if request.is_json:
            return jsonify({'error': 'File non trovato'}), 404
        flash('File non trovato', 'error')
        return redirect(url_for('files.view_file', file_id=file.id))

@files_bp.route('/<uuid:file_id>/delete', methods=['POST'])
@login_required
def delete_file(file_id):
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    # Delete physical file
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    file_name = file.original_name
    project_id = file.project_id
    
    db.session.delete(file)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': f'File "{file_name}" eliminato con successo'})
    else:
        flash(f'File "{file_name}" eliminato con successo', 'success')
        return redirect(url_for('projects.view_project', project_id=project_id))

@files_bp.route('/<uuid:file_id>/reprocess', methods=['POST'])
@login_required
def reprocess_file(file_id):
    file = File.query.join(Project).filter(
        File.id == file_id,
        Project.owner_id == current_user.id
    ).first_or_404()
    
    if file.file_type not in ['xlsx', 'xls']:
        if request.is_json:
            return jsonify({'error': 'File non supporta la rielaborazione'}), 400
        flash('File non supporta la rielaborazione', 'error')
        return redirect(url_for('files.view_file', file_id=file.id))
    
    # Delete existing sheets and data
    ExcelSheet.query.filter_by(file_id=file.id).delete()
    db.session.commit()
    
    # Reprocess file
    file.processing_status = 'processing'
    db.session.commit()
    
    success = process_excel_file(file.file_path, file)
    
    if request.is_json:
        if success:
            return jsonify({'message': 'File rielaborato con successo'})
        else:
            return jsonify({'error': 'Errore durante la rielaborazione'}), 500
    else:
        if success:
            flash('File rielaborato con successo!', 'success')
        else:
            flash('Errore durante la rielaborazione', 'error')
        return redirect(url_for('files.view_file', file_id=file.id))