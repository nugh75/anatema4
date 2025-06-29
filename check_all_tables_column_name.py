#!/usr/bin/env python3
"""
Script per verificare tutte le tabelle esistenti nel database
e quali hanno la colonna column_name
"""

from app import create_app
from app.database import db
from sqlalchemy import text

def main():
    app = create_app()
    
    with app.app_context():
        try:
            # Lista tutte le tabelle
            query_tables = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            
            result = db.session.execute(query_tables)
            tables = [row[0] for row in result.fetchall()]
            
            print("=== TABELLE ESISTENTI NEL DATABASE ===")
            for table in tables:
                print(f"  - {table}")
            
            print(f"\nTotale tabelle: {len(tables)}")
            
            # Verifichiamo quali di queste hanno column_name
            print("\n=== VERIFICA COLONNA 'column_name' ===")
            tables_with_column_name = []
            
            for table in tables:
                query_columns = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'column_name';
                """)
                
                result = db.session.execute(query_columns)
                if result.fetchone():
                    tables_with_column_name.append(table)
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table}")
            
            print(f"\n=== TABELLE CON column_name ===")
            if tables_with_column_name:
                for table in tables_with_column_name:
                    print(f"  - {table}")
            else:
                print("  NESSUNA TABELLA ha la colonna 'column_name'")
            
            # Verifichiamo specificamente le tabelle nella migrazione
            target_tables = ['auto_label_applications', 'auto_labels', 'cell_labels', 'column_analysis']
            print(f"\n=== VERIFICA TABELLE TARGET MIGRAZIONE ===")
            for table in target_tables:
                exists = table in tables
                has_column = table in tables_with_column_name
                status = "✅" if exists else "❌"
                column_status = "✅" if has_column else "❌"
                print(f"  {status} Tabella '{table}' {'esiste' if exists else 'NON esiste'}")
                if exists:
                    print(f"    {column_status} Colonna 'column_name' {'presente' if has_column else 'NON presente'}")
                    
        except Exception as e:
            print(f"❌ Errore durante verifica: {e}")
            return False
    
    return True

if __name__ == "__main__":
    main()
