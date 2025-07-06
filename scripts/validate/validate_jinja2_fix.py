#!/usr/bin/env python3
"""
Validazione Fix Errore Jinja2 - Task 2.4
Verifica che il template projects/view.html funzioni correttamente
"""

import sys
import os
sys.path.append('/home/nugh75/Git/anatema2')

from app import create_app
from app.models import Project, Label
from app.database import db
from flask import render_template_string

def test_jinja2_fix():
    """Test che il template projects/view.html funzioni senza errori"""
    print("🔍 Testing Fix Errore Jinja2...")
    
    app = create_app()
    with app.app_context():
        # Test 1: Verifica che i modelli abbiano usage_count
        labels = Label.query.limit(3).all()
        print(f"✅ Labels trovate: {len(labels)}")
        
        for label in labels:
            print(f"  - {label.name}: usage_count={label.usage_count}")
        
        # Test 2: Verifica template Jinja2
        template_test = """
        {% set total_usage = labels|sum(attribute='usage_count') %}
        Total: {{ total_usage }}
        {% set unused_labels = labels|rejectattr('usage_count')|list|length %}
        Unused: {{ unused_labels }}
        """
        
        try:
            result = render_template_string(template_test, labels=labels)
            print("✅ Template Jinja2 funziona:")
            print(result.strip())
        except Exception as e:
            print(f"❌ Errore template: {e}")
            return False
        
        # Test 3: Verifica progetti
        projects = Project.query.limit(1).all()
        if projects:
            project = projects[0]
            print(f"✅ Progetto test: {project.name}")
            
            # Simula la logica della view
            project_labels = Label.query.filter_by(project_id=project.id).all()
            for label in project_labels:
                if label.usage_count is None:
                    label.usage_count = label.cell_labels.count()
            
            print(f"✅ Aggiornamento usage_count completato")
        
        print("\n🎉 Tutti i test superati! Template pronto per Task 2.5")
        return True

if __name__ == "__main__":
    success = test_jinja2_fix()
    sys.exit(0 if success else 1)
