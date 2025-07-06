# Anatema2 - Sistema di Etichettatura Centralizzato

## 📋 Panoramica del Progetto

Anatema2 è un sistema avanzato per la gestione centralizzata delle etichette con funzionalità di machine learning e intelligenza artificiale.

## 🚀 Stato del Progetto

### ✅ Funzionalità Completate
- Sistema di autenticazione e autorizzazione
- Dashboard amministrativo completo
- Gestione progetti e file Excel
- Sistema di etichettatura base
- API REST complete per tutte le operazioni
- Integrazione database con SQLAlchemy
- Sistema di migrazioni Alembic

### 🔧 Task Correnti

#### Task 2.4 - Store Etichette Centralizzato (IN CORSO)
**Stato**: Sviluppo completato, debugging UI in corso

**Obiettivo**: Implementare un sistema centralizzato per la gestione delle etichette con operazioni CRUD complete.

**Progresso**:
- ✅ Backend API completamente funzionanti
- ✅ Template HTML e UI implementati
- ✅ JavaScript per interazioni frontend
- ⚠️ Problemi di integrazione frontend-backend identificati
- 🔧 Soluzioni CORS e Materialize CSS implementate

**File Principali**:
- `app/views/labels.py` - Blueprint Flask per le etichette
- `app/views/api.py` - API endpoints per operazioni CRUD
- `app/templates/labels/store.html` - Template UI
- `app/static/js/materialize_integration.js` - JavaScript integrazione
- `app/models_labeling.py` - Modelli database per etichette

**Problemi Identificati e Soluzioni**:

1. **Conflitto Materialize CSS**:
   - Problema: JavaScript personalizzato conflittava con modal-trigger di Materialize
   - Soluzione: Riscritta integrazione per lavorare CON Materialize invece che contro

2. **Errori CORS (OpaqueResponseBlocking)**:
   - Problema: Browser bloccava richieste per politiche cross-origin
   - Soluzione: Configurazione CORS specifica e funzione safeFetch()

3. **Event Listeners non funzionanti**:
   - Problema: Pulsanti non rispondevano ai click
   - Soluzione: Callback Materialize onOpenStart per popolamento automatico modal

**Test e Diagnostica**:
- `test_label_api.py` - Test API backend
- `test_mac_label_store.py` - Test ottimizzato per Mac
- `test_final_cors_fix.py` - Test post-correzione CORS
- Script diagnostici multiple per isolamento problemi

## 🛠️ Stack Tecnologico

### Backend
- **Framework**: Flask 2.x
- **Database**: SQLAlchemy + SQLite
- **Migrazioni**: Alembic
- **Autenticazione**: Flask-Login + JWT
- **API**: Flask-RESTful
- **CORS**: Flask-CORS

### Frontend
- **UI Framework**: Materialize CSS
- **JavaScript**: Vanilla ES6+
- **Icons**: Material Icons
- **Template Engine**: Jinja2

### ML/AI
- **Analisi**: Custom ML modules
- **Sentiment Analysis**: Integrazione NLP
- **Clustering**: Algoritmi di raggruppamento automatico

## 📁 Struttura del Progetto

```
anatema2/
├── app/
│   ├── __init__.py          # Configurazione Flask app
│   ├── models.py            # Modelli database principali
│   ├── models_labeling.py   # Modelli per sistema etichettatura
│   ├── views/               # Blueprint Flask
│   │   ├── labels.py        # Gestione etichette
│   │   ├── api.py           # API endpoints
│   │   └── ...
│   ├── templates/           # Template Jinja2
│   │   └── labels/
│   │       └── store.html   # Store etichette UI
│   ├── static/             # Asset statici
│   │   ├── css/
│   │   └── js/
│   │       └── materialize_integration.js
│   └── ml/                 # Moduli machine learning
├── migrations/             # Migrazioni database
├── tests/                 # Test suite
├── config/                # Configurazioni
└── requirements.txt       # Dipendenze Python
```

## 🚧 Problemi Noti

### Store Etichette (Task 2.4)
- **Frontend UI**: I pulsanti modal necessitano di ulteriore debugging
- **Integrazione CORS**: Soluzioni implementate ma richiedono test approfonditi
- **Materialize CSS**: Integrazione completata ma comportamenti inconsistenti

### Raccomandazioni per Continuo Sviluppo
1. **Test End-to-End**: Implementare test automatizzati browser
2. **Refactoring JavaScript**: Considerare framework moderno (Vue.js/React)
3. **Monitoring**: Aggiungere logging dettagliato per debugging
4. **Performance**: Ottimizzazione query database e caching

## 🎯 Prossimi Passi

1. **Completare debugging Store Etichette**
   - Test approfonditi su diversi browser
   - Risoluzione finale problemi modal
   - Validazione operazioni CRUD

2. **Task 2.5**: Sistema di suggerimenti AI
3. **Task 2.6**: Validazione e testing completo
4. **Deploy**: Preparazione per ambiente produzione

## 📝 Note di Sviluppo

**Data ultimo aggiornamento**: 6 Luglio 2025

**Stato generale**: Sistema core funzionante, UI in fase di refinement

**Team focus**: Debugging frontend, integrazione seamless user experience

---

## 🔧 Setup Sviluppo

```bash
# Installazione dipendenze
pip install -r requirements.txt

# Configurazione database
flask db init
flask db migrate
flask db upgrade

# Avvio server sviluppo
python run.py
```

## 📊 Metriche del Progetto

- **Linee di codice**: ~5000+ (backend + frontend)
- **File template**: 20+ template Jinja2
- **API endpoints**: 30+ endpoints RESTful
- **Test scripts**: 10+ script di testing e diagnostica
- **Database tables**: 15+ tabelle con relazioni complesse
