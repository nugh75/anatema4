#!/usr/bin/env python3
"""
Script per verificare lo schema della tabella cell_labels
Parte del Task 2.4 - Risoluzione multiple heads Alembic
"""

from app import create_app
from app.database import db
from sqlalchemy import text

def main():
    app = create_app()
    
    with app.app_context():
        try:
            # Query per verificare schema tabella cell_labels
            query = text("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'cell_labels' 
                ORDER BY ordinal_position;
            """)
            
            result = db.session.execute(query)
            rows = result.fetchall()
            
            print("=== SCHEMA TABELLA cell_labels ===")
            if not rows:
                print("❌ Tabella 'cell_labels' NON TROVATA nel database")
                return
            
            print("Colonne presenti:")
            for row in rows:
                column_name, data_type, max_length, nullable = row
                length_info = f"({max_length})" if max_length else ""
                nullable_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  - {column_name}: {data_type}{length_info} {nullable_info}")
            
            # Verifichiamo specificamente se esiste column_name
            column_names = [row[0] for row in rows]
            print(f"\n=== ANALISI ===")
            print(f"Numero colonne totali: {len(column_names)}")
            
            if 'column_name' in column_names:
                print("✅ Colonna 'column_name' TROVATA")
            else:
                print("❌ Colonna 'column_name' NON TROVATA")
                
            if 'column_index' in column_names:
                print("✅ Colonna 'column_index' TROVATA")
            else:
                print("❌ Colonna 'column_index' NON TROVATA")
            
            print(f"\nTutte le colonne: {', '.join(column_names)}")
            
        except Exception as e:
            print(f"❌ Errore durante verifica schema: {e}")
            return False
    
    return True

if __name__ == "__main__":
    main()
