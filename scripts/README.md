# Scripts Directory

Questa cartella contiene tutti gli script di supporto al progetto, organizzati per categoria.

## 📁 Struttura

### `analyze/`
Script per analisi e investigazione:
- `analyze_*.py` - Script di analisi generale
- Utilizzati per esplorare dati, schema database, codice esistente
- Output: Report, JSON, file di log

### `fix/`
Script per correzioni e fix:
- `fix_*.py` - Script di riparazione
- Utilizzati per correggere problemi specifici (database, migrazioni, codice)
- Output: Modifiche dirette ai file o database

### `validate/`
Script per validazione e verifica:
- `validate_*.py` - Script di validazione
- `verify_*.py` - Script di verifica
- Utilizzati per confermare che le modifiche siano corrette
- Output: Report di validazione, success/failure

### `task/`
Script specifici per task del progetto:
- `task_*.py` - Script per task specifici
- `final_*.py` - Script di finalizzazione
- `resolve_*.py` - Script di risoluzione problemi
- Utilizzati per implementare feature specifiche o risolvere task complessi

### `utils/`
Utility generiche:
- `check_*.py` - Script di controllo
- `find_*.py` - Script di ricerca
- `create_*.py` - Script di creazione
- `monitor_*.py` - Script di monitoraggio
- Utilizzati per operazioni di supporto generale

## 🔧 Utilizzo

Tutti gli script devono essere eseguiti dalla radice del progetto:

```bash
cd /home/nugh75/Git/anatema2
python scripts/analyze/analyze_schema_task_2_1.py
python scripts/fix/fix_migration_issue.py
python scripts/validate/validate_schema_task_2_1.py
```

## 📋 Nomenclatura

- **Analisi**: `analyze_[descrizione]_task_[numero].py`
- **Fix**: `fix_[descrizione].py`
- **Validazione**: `validate_[descrizione].py`
- **Task**: `task_[numero]_[descrizione].py`
- **Utility**: `[azione]_[descrizione].py`

## 📊 Stato Attuale

- **analyze/**: 9 script
- **fix/**: 5 script
- **validate/**: File spostati
- **task/**: File spostati
- **utils/**: File spostati

Tutti i script sono stati migrati dalle cartelle precedenti mantenendo la funzionalità.
