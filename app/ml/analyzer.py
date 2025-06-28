"""
Main Data Analyzer that coordinates all ML modules
"""

import time
import logging
from typing import Dict, List, Any, Optional
from flask import current_app
from app.database import db
from app.models import (
    ExcelSheet, ExcelColumn, ExcelRow, MLAnalysis, ColumnAnalysis, 
    AutoLabel, AutoLabelApplication, Project, File
)
from .api_client import MLAPIClient
from .column_detector import ColumnTypeDetector
from .clustering import SemanticClustering
from .sentiment import SentimentAnalyzer

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Analizzatore principale che coordina tutti i moduli ML"""
    
    def __init__(self, ml_config: Optional[Dict[str, Any]] = None):
        self.ml_config = ml_config or self._get_default_config()
        self.api_client = MLAPIClient(
            provider=self.ml_config.get('ml_provider'),
            api_key=self.ml_config.get('api_key'),
            api_url=self.ml_config.get('api_url'),
            model=self.ml_config.get('ml_model')
        )
        self.column_detector = ColumnTypeDetector()
        self.clustering = SemanticClustering(
            min_cluster_size=self.ml_config.get('clustering_min_samples', 5),
            max_clusters=self.ml_config.get('max_clusters', 10)
        )
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_sheet(self, sheet_id: str, project_id: str, analysis_types: List[str] = None) -> Dict[str, Any]:
        """Analizza un foglio Excel completo"""
        
        if analysis_types is None:
            analysis_types = ['column_detection', 'auto_labeling', 'sentiment']
        
        start_time = time.time()
        
        try:
            # Recupera il foglio e i dati
            sheet = ExcelSheet.query.filter_by(id=sheet_id).first()
            if not sheet:
                return {'error': 'Foglio non trovato', 'success': False}
            
            # Crea record di analisi ML
            ml_analysis = MLAnalysis(
                project_id=project_id,
                file_id=sheet.file_id,
                sheet_id=sheet_id,
                ml_provider=self.ml_config['ml_provider'],
                ml_model=self.ml_config['ml_model'],
                analysis_type='comprehensive',
                status='processing'
            )
            db.session.add(ml_analysis)
            db.session.flush()
            
            results = {
                'ml_analysis_id': str(ml_analysis.id),
                'sheet_info': sheet.to_dict(),
                'analysis_types': analysis_types,
                'results': {}
            }
            
            # 1. Analisi delle colonne
            if 'column_detection' in analysis_types:
                logger.info(f"Avvio analisi colonne per foglio {sheet_id}")
                column_results = self._analyze_columns(sheet, ml_analysis.id)
                results['results']['column_analysis'] = column_results
            
            # 2. Auto-etichettatura per domande aperte
            if 'auto_labeling' in analysis_types:
                logger.info(f"Avvio auto-etichettatura per foglio {sheet_id}")
                labeling_results = self._perform_auto_labeling(sheet, ml_analysis.id)
                results['results']['auto_labeling'] = labeling_results
            
            # 3. Analisi del sentiment
            if 'sentiment' in analysis_types:
                logger.info(f"Avvio analisi sentiment per foglio {sheet_id}")
                sentiment_results = self._analyze_sentiment(sheet, ml_analysis.id)
                results['results']['sentiment_analysis'] = sentiment_results
            
            # Aggiorna il record di analisi
            processing_time = time.time() - start_time
            ml_analysis.status = 'completed'
            ml_analysis.results = results['results']
            ml_analysis.processing_time = processing_time
            
            db.session.commit()
            
            results['success'] = True
            results['processing_time'] = processing_time
            
            logger.info(f"Analisi completata per foglio {sheet_id} in {processing_time:.2f} secondi")
            
            return results
            
        except Exception as e:
            # Aggiorna il record con l'errore
            if 'ml_analysis' in locals():
                ml_analysis.status = 'error'
                ml_analysis.error_message = str(e)
                ml_analysis.processing_time = time.time() - start_time
                db.session.commit()
            
            logger.error(f"Errore nell'analisi del foglio {sheet_id}: {str(e)}")
            return {
                'error': str(e),
                'success': False,
                'processing_time': time.time() - start_time
            }
    
    def _analyze_columns(self, sheet: ExcelSheet, ml_analysis_id: str) -> Dict[str, Any]:
        """Analizza le colonne del foglio per determinare i tipi di dati"""
        
        columns = ExcelColumn.query.filter_by(sheet_id=sheet.id).order_by(ExcelColumn.column_index).all()
        rows = ExcelRow.query.filter_by(sheet_id=sheet.id).limit(100).all()  # Primi 100 righe per analisi
        
        column_results = {}
        open_question_columns = []
        
        for column in columns:
            try:
                # Estrai i valori della colonna
                column_values = []
                for row in rows:
                    if row.data and column.name in row.data:
                        value = row.data[column.name]
                        if value is not None and str(value).strip():
                            column_values.append(str(value))
                
                if not column_values:
                    continue
                
                # Analisi locale con ColumnTypeDetector
                local_analysis = self.column_detector.analyze_column(column_values, column.name)
                
                # Analisi avanzata con AI se configurata
                ai_analysis = None
                if self.ml_config.get('use_ai_analysis', True) and len(column_values) >= 5:
                    try:
                        ai_analysis = self.api_client.analyze_column_samples(
                            column_values[:20], column.name
                        )
                    except Exception as e:
                        logger.warning(f"Analisi AI fallita per colonna {column.name}: {str(e)}")
                
                # Combina i risultati
                combined_analysis = self._combine_column_analysis(local_analysis, ai_analysis)
                
                # Salva l'analisi nel database
                column_analysis = ColumnAnalysis(
                    ml_analysis_id=ml_analysis_id,
                    column_id=column.id,
                    detected_type=combined_analysis['detected_type'],
                    confidence_score=combined_analysis['confidence'],
                    unique_values_count=combined_analysis.get('unique_values_count', 0),
                    null_values_count=combined_analysis.get('null_values_count', 0),
                    avg_text_length=combined_analysis.get('avg_text_length', 0),
                    text_variability=combined_analysis.get('text_variability', 0),
                    is_open_question=combined_analysis.get('is_open_question', False),
                    question_complexity=combined_analysis.get('complexity')
                )
                
                db.session.add(column_analysis)
                
                column_results[column.name] = {
                    'column_id': str(column.id),
                    'analysis': combined_analysis,
                    'sample_values': column_values[:5]
                }
                
                # Traccia le colonne con domande aperte
                if combined_analysis.get('is_open_question', False):
                    open_question_columns.append({
                        'column': column,
                        'analysis': column_analysis,
                        'values': column_values
                    })
                
            except Exception as e:
                logger.error(f"Errore nell'analisi della colonna {column.name}: {str(e)}")
                continue
        
        return {
            'columns_analyzed': len(column_results),
            'open_question_columns': len(open_question_columns),
            'column_details': column_results,
            'open_questions': [col['column'].name for col in open_question_columns]
        }
    
    def _perform_auto_labeling(self, sheet: ExcelSheet, ml_analysis_id: str) -> Dict[str, Any]:
        """Esegue l'auto-etichettatura per le domande aperte"""
        
        # Trova le colonne identificate come domande aperte
        open_question_analyses = ColumnAnalysis.query.filter_by(
            ml_analysis_id=ml_analysis_id,
            is_open_question=True
        ).all()
        
        if not open_question_analyses:
            return {
                'message': 'Nessuna domanda aperta trovata',
                'labels_generated': 0
            }
        
        labeling_results = {}
        total_labels = 0
        
        for column_analysis in open_question_analyses:
            try:
                column = column_analysis.column
                
                # Recupera i valori della colonna
                rows = ExcelRow.query.filter_by(sheet_id=sheet.id).all()
                column_values = []
                
                for row in rows:
                    if row.data and column.name in row.data:
                        value = row.data[column.name]
                        if value is not None and str(value).strip():
                            column_values.append(str(value))
                
                if len(column_values) < self.ml_config.get('clustering_min_samples', 5):
                    continue
                
                # Clustering semantico
                clustering_result = self.clustering.analyze_and_cluster(column_values)
                
                if not clustering_result.get('success', False):
                    continue
                
                # Genera etichette automatiche per ogni cluster
                column_labels = []
                
                for cluster_id, cluster_info in clustering_result['generated_labels'].items():
                    # Crea AutoLabel
                    auto_label = AutoLabel(
                        ml_analysis_id=ml_analysis_id,
                        column_analysis_id=column_analysis.id,
                        label_name=cluster_info['name'],
                        label_description=cluster_info['description'],
                        category=cluster_info.get('theme', 'generale'),
                        theme=cluster_info.get('theme', 'generale'),
                        cluster_id=cluster_id,
                        cluster_size=cluster_info['size'],
                        representative_texts=cluster_info.get('keywords', []),
                        confidence_score=cluster_info['confidence'],
                        manual_validation='pending'
                    )
                    
                    db.session.add(auto_label)
                    db.session.flush()
                    
                    column_labels.append(auto_label)
                    total_labels += 1
                
                # Applica le etichette ai dati (come suggerimenti)
                self._apply_cluster_labels_to_data(
                    column_labels, column_values, clustering_result['cluster_labels'], rows, column
                )
                
                labeling_results[column.name] = {
                    'labels_generated': len(column_labels),
                    'clustering_info': {
                        'num_clusters': clustering_result['num_clusters'],
                        'silhouette_score': clustering_result['silhouette_score']
                    },
                    'labels': [label.to_dict() for label in column_labels]
                }
                
            except Exception as e:
                logger.error(f"Errore nell'auto-etichettatura per colonna {column_analysis.column.name}: {str(e)}")
                continue
        
        return {
            'columns_processed': len(labeling_results),
            'labels_generated': total_labels,
            'column_details': labeling_results
        }
    
    def _analyze_sentiment(self, sheet: ExcelSheet, ml_analysis_id: str) -> Dict[str, Any]:
        """Analizza il sentiment delle risposte testuali"""
        
        # Trova le colonne di testo (domande aperte e testo lungo)
        text_columns = ColumnAnalysis.query.filter_by(ml_analysis_id=ml_analysis_id).filter(
            ColumnAnalysis.detected_type.in_(['open_question', 'long_text'])
        ).all()
        
        if not text_columns:
            return {
                'message': 'Nessuna colonna di testo trovata per l\'analisi del sentiment',
                'columns_analyzed': 0
            }
        
        sentiment_results = {}
        
        for column_analysis in text_columns:
            try:
                column = column_analysis.column
                
                # Recupera i valori della colonna
                rows = ExcelRow.query.filter_by(sheet_id=sheet.id).all()
                column_values = []
                
                for row in rows:
                    if row.data and column.name in row.data:
                        value = row.data[column.name]
                        if value is not None and str(value).strip():
                            column_values.append(str(value))
                
                if not column_values:
                    continue
                
                # Analisi del sentiment
                sentiment_result = self.sentiment_analyzer.analyze_texts_batch(column_values)
                
                # Aggiorna le AutoLabel esistenti con informazioni di sentiment
                auto_labels = AutoLabel.query.filter_by(column_analysis_id=column_analysis.id).all()
                
                for auto_label in auto_labels:
                    # Trova i testi del cluster per analisi specifica
                    cluster_texts = []
                    # Qui dovresti recuperare i testi specifici del cluster
                    # Per semplicità, usiamo il sentiment generale
                    
                    auto_label.sentiment_label = sentiment_result['overall_sentiment']
                    auto_label.sentiment_score = sentiment_result['overall_score']
                    auto_label.emotion_tags = sentiment_result['common_emotions']
                
                sentiment_results[column.name] = {
                    'overall_sentiment': sentiment_result['overall_sentiment'],
                    'overall_score': sentiment_result['overall_score'],
                    'sentiment_distribution': sentiment_result['sentiment_distribution'],
                    'common_emotions': sentiment_result['common_emotions'],
                    'statistics': sentiment_result['statistics']
                }
                
            except Exception as e:
                logger.error(f"Errore nell'analisi del sentiment per colonna {column_analysis.column.name}: {str(e)}")
                continue
        
        return {
            'columns_analyzed': len(sentiment_results),
            'column_details': sentiment_results
        }
    
    def _combine_column_analysis(self, local_analysis: Dict[str, Any], ai_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Combina i risultati dell'analisi locale e AI"""
        
        if not ai_analysis:
            return local_analysis
        
        # Se l'AI ha alta confidenza, usa i suoi risultati
        ai_confidence = ai_analysis.get('confidence', 0.0)
        local_confidence = local_analysis.get('confidence', 0.0)
        
        if ai_confidence > 0.8 and ai_confidence > local_confidence:
            return {
                'detected_type': ai_analysis.get('detected_type', local_analysis['detected_type']),
                'confidence': ai_confidence,
                'is_open_question': ai_analysis.get('is_open_question', False),
                'complexity': ai_analysis.get('complexity'),
                'reasoning': f"AI Analysis: {ai_analysis.get('reasoning', '')}",
                **local_analysis  # Mantieni le statistiche locali
            }
        
        # Altrimenti, usa l'analisi locale ma arricchisci con info AI
        result = local_analysis.copy()
        if ai_analysis.get('suggested_categories'):
            result['suggested_categories'] = ai_analysis['suggested_categories']
        
        return result
    
    def _apply_cluster_labels_to_data(self, auto_labels: List[AutoLabel], column_values: List[str], 
                                    cluster_labels: List[int], rows: List[ExcelRow], column: ExcelColumn):
        """Applica le etichette dei cluster ai dati come suggerimenti"""
        
        # Crea un mapping cluster_id -> auto_label
        cluster_to_label = {label.cluster_id: label for label in auto_labels}
        
        value_index = 0
        for row in rows:
            if row.data and column.name in row.data:
                value = row.data[column.name]
                if value is not None and str(value).strip():
                    if value_index < len(cluster_labels):
                        cluster_id = cluster_labels[value_index]
                        
                        if cluster_id in cluster_to_label:
                            auto_label = cluster_to_label[cluster_id]
                            
                            # Crea AutoLabelApplication come suggerimento
                            application = AutoLabelApplication(
                                auto_label_id=auto_label.id,
                                row_id=row.id,
                                column_index=column.column_index,
                                cell_value=str(value),
                                confidence_score=auto_label.confidence_score,
                                status='suggested'
                            )
                            
                            db.session.add(application)
                    
                    value_index += 1
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Restituisce la configurazione di default"""
        return {
            'ml_provider': current_app.config.get('ML_PROVIDER', 'openrouter'),
            'ml_model': current_app.config.get('ML_MODEL', 'anthropic/claude-3-haiku'),
            'api_key': current_app.config.get('OPENROUTER_API_KEY'),
            'api_url': current_app.config.get('OPENROUTER_API_URL'),
            'use_ai_analysis': True,
            'clustering_min_samples': current_app.config.get('CLUSTERING_MIN_SAMPLES', 5),
            'max_clusters': 10,
            'min_unique_values': current_app.config.get('MIN_UNIQUE_VALUES', 3),
            'max_text_length': current_app.config.get('MAX_TEXT_LENGTH', 1000)
        }
    
    def test_configuration(self) -> Dict[str, Any]:
        """Testa la configurazione ML"""
        try:
            # Test connessione API
            api_test = self.api_client.test_connection()
            
            # Test moduli locali
            local_tests = {
                'column_detector': self._test_column_detector(),
                'clustering': self._test_clustering(),
                'sentiment_analyzer': self._test_sentiment_analyzer()
            }
            
            return {
                'api_connection': api_test,
                'local_modules': local_tests,
                'configuration': self.ml_config,
                'overall_status': 'ok' if api_test['status'] == 'success' else 'warning'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'overall_status': 'error'
            }
    
    def _test_column_detector(self) -> Dict[str, Any]:
        """Testa il rilevatore di colonne"""
        try:
            test_values = ['Mario Rossi', 'Luigi Bianchi', 'Anna Verdi']
            result = self.column_detector.analyze_column(test_values, 'Nome')
            return {'status': 'ok', 'detected_type': result['detected_type']}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _test_clustering(self) -> Dict[str, Any]:
        """Testa il clustering"""
        try:
            test_texts = [
                'Molto soddisfatto del servizio',
                'Esperienza positiva',
                'Servizio scadente',
                'Non sono contento',
                'Ottima qualità'
            ]
            result = self.clustering.analyze_and_cluster(test_texts)
            return {'status': 'ok', 'clusters_found': result.get('num_clusters', 0)}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _test_sentiment_analyzer(self) -> Dict[str, Any]:
        """Testa l'analizzatore di sentiment"""
        try:
            test_text = 'Sono molto soddisfatto del servizio ricevuto'
            result = self.sentiment_analyzer.analyze_text(test_text)
            return {'status': 'ok', 'sentiment': result['sentiment']}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}