# Task 2.7 - Completamento Store Etichette

**Obiettivo**: Completare le funzionalità mancanti del sistema store etichette

## 🚧 Problemi Identificati

1. **Modifica Etichette**: Frontend JS corretto ma problemi di validazione
2. **Eliminazione Etichette**: Controlli di sicurezza mancanti nel frontend
3. **Visualizzazione Celle**: Manca completamente la visualizzazione dei valori delle celle etichettate
4. **API Usage**: Manca endpoint per ottenere i valori delle celle per etichetta

## 🔧 Implementazione

### 1. Nuovo Endpoint API - Valori Celle Etichettate
Aggiungere a `app/views/api.py`:

```python
@api_bp.route('/projects/<uuid:project_id>/labels/<int:label_id>/cell-values')
@jwt_or_login_required
def api_label_cell_values(project_id, label_id):
    """Get all cell values for a specific label"""
```

### 2. Modifica Template Store
Aggiungere sezione "Valori Celle" per ogni etichetta

### 3. Fix JavaScript
Migliorare gestione errori e validazione

### 4. Test Implementazione
Validare tutte le funzionalità CRUD

## 📋 Piano di Implementazione

1. **Nuovo Endpoint API** (5 min)
2. **Modifica Template** (10 min) 
3. **Fix JavaScript** (10 min)
4. **Test Completo** (5 min)

**Tempo stimato totale**: 30 minuti
