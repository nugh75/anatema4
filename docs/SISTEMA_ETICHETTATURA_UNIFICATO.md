# Sistema Etichettatura Unificato - Dettagli Implementazione

**Documento**: Dettagli tecnici per implementazione Task 2.0  
**Riferimento**: MASTER_REFACTORING.md - Task 2.0  
**Aggiornato**: 30 giugno 2025

---

## 🎯 WORKFLOW ETICHETTATURA DEFINITO

### 📋 Pipeline Umano
1. **Selezione Celle**: Singola colonna o multiple celle nelle view colonne/righe
2. **Scelta Etichetta**: Dropdown con etichette esistenti del progetto
3. **Applicazione**: Immediata, senza autorizzazione
4. **Storage**: Salvato in `label_applications` con `application_type='manual'`

### 🤖 Pipeline AI  
1. **Selezione Celle**: Singola colonna o multiple celle nelle view colonne/righe
2. **Richiesta AI**: Sistema analizza celle e suggerisce etichette esistenti
3. **Autorizzazione**: **OBBLIGATORIA** - umano deve approvare ogni suggerimento
4. **Applicazione**: Solo dopo approvazione umana
5. **Storage**: Salvato in `label_applications` con `application_type='ai_approved'`

### 🏪 Store Etichette Centralizzato
1. **Creazione Manuale**: Umano crea etichetta (nome + descrizione) → Immediata
2. **Suggerimenti AI**: AI analizza colonna e suggerisce nuove etichette per lo store
3. **Approvazione**: Umano approva/rifiuta suggerimenti AI per nuove etichette
4. **Storage**: Etichette in `labels`, suggerimenti in `label_suggestions`

---

## 🗄️ SCHEMA DATABASE DETTAGLIATO

### Tabelle Esistenti da Modificare

#### 1. `labels` (Store Etichette) - MODIFICHE NECESSARIE
```sql
-- Struttura attuale (OK)
id: INTEGER (PK)
project_id: UUID (FK projects.id)
name: VARCHAR(100)
description: TEXT  
color: VARCHAR(7) DEFAULT '#1976d2'
categories: ARRAY[VARCHAR]
created_at: DATETIME

-- CAMPI DA AGGIUNGERE
created_by: UUID (FK users.id)        -- Chi ha creato l'etichetta
usage_count: INTEGER DEFAULT 0        -- Numero volte utilizzata
is_ai_suggested: BOOLEAN DEFAULT FALSE -- Se creata da suggerimento AI
```

#### 2. `label_applications` (Applicazioni) - MODIFICHE NECESSARIE  
```sql
-- Struttura attuale (OK)
id: UUID (PK)
project_id: UUID (FK projects.id)
sheet_id: UUID (FK excel_sheets.id)
label_id: INTEGER (FK labels.id)
applied_by: UUID (FK users.id)
row_index: INTEGER
column_name: VARCHAR(1000)
cell_value: TEXT
application_type: VARCHAR(20)  -- 'manual', 'ai_batch', 'ai_single'
confidence_score: FLOAT
ai_reasoning: TEXT
is_active: BOOLEAN DEFAULT TRUE
applied_at: DATETIME

-- CAMPI DA AGGIUNGERE  
authorized_by: UUID (FK users.id)     -- Chi ha autorizzato (per AI)
authorized_at: DATETIME               -- Quando autorizzato (per AI)
suggestion_id: UUID (FK label_suggestions.id) -- Link al suggerimento originale
```

#### 3. `label_suggestions` (Suggerimenti AI) - MODIFICHE NECESSARIE
```sql
-- Struttura attuale (parziale)
id: UUID (PK)
suggested_name: VARCHAR(200)
suggested_description: TEXT
suggested_category: VARCHAR(100)
suggested_color: VARCHAR(7) DEFAULT '#1976d2'
ai_confidence: FLOAT
ai_reasoning: TEXT
status: VARCHAR(20) DEFAULT 'pending'
reviewed_by: UUID (FK users.id)
reviewed_at: DATETIME
created_at: DATETIME

-- CAMPI DA AGGIUNGERE/MODIFICARE
project_id: UUID (FK projects.id)                    -- Progetto di riferimento
suggestion_type: VARCHAR(20) DEFAULT 'store_label'   -- 'store_label', 'cell_application'
target_cells: JSON                                   -- Celle da etichettare (per cell_application)
suggested_label_id: INTEGER (FK labels.id)          -- Se suggerisce etichetta esistente
created_by: UUID (FK users.id)                      -- Chi ha richiesto il suggerimento
ai_provider: VARCHAR(50)                            -- Provider AI utilizzato
ai_model: VARCHAR(100)                              -- Modello AI utilizzato
```

### Nuove Tabelle (Se Necessarie)

#### `authorization_requests` (Richieste Autorizzazione)
```sql
id: UUID (PK)
project_id: UUID (FK projects.id)
request_type: VARCHAR(20)              -- 'label_application', 'store_suggestion'
target_suggestion_id: UUID (FK label_suggestions.id)
requested_by: UUID (FK users.id)       -- Chi ha fatto la richiesta
status: VARCHAR(20) DEFAULT 'pending'  -- 'pending', 'approved', 'rejected'
reviewed_by: UUID (FK users.id)
reviewed_at: DATETIME
created_at: DATETIME
notes: TEXT                            -- Note dell'approvatore
```

---

## 🔌 API ENDPOINTS DETTAGLIATI

### Store Etichette
```
GET    /api/projects/{id}/labels
       → Lista tutte le etichette del progetto con statistiche

POST   /api/projects/{id}/labels  
       → Crea nuova etichetta manuale
       Body: {name, description, color?, category?}

PUT    /api/projects/{id}/labels/{label_id}
       → Modifica etichetta esistente (solo se creata dall'utente)

DELETE /api/projects/{id}/labels/{label_id}  
       → Elimina etichetta (solo se non utilizzata)

POST   /api/projects/{id}/labels/ai-suggest
       → AI analizza colonna e suggerisce nuove etichette per store
       Body: {column_name, sample_data[], ai_provider?, ai_model?}
```

### Applicazione Etichette
```
POST   /api/projects/{id}/labels/apply-manual
       → Applicazione etichetta manuale (immediata)
       Body: {label_id, cells: [{row_index, column_name, cell_value}]}

POST   /api/projects/{id}/labels/apply-ai
       → Richiesta applicazione AI (crea suggerimento)
       Body: {cells: [{row_index, column_name, cell_value}], ai_provider?, ai_model?}

GET    /api/projects/{id}/labels/applications
       → Lista applicazioni etichette con filtri
       Query: ?type=manual|ai&status=all|pending|approved
```

### Autorizzazioni e Suggerimenti  
```
GET    /api/projects/{id}/suggestions
       → Lista suggerimenti pendenti (store + applicazioni)
       Query: ?type=store_label|cell_application&status=pending|all

PUT    /api/projects/{id}/suggestions/{suggestion_id}/approve
       → Approva suggerimento (crea etichetta o applica celle)
       Body: {notes?, modifications?}

PUT    /api/projects/{id}/suggestions/{suggestion_id}/reject  
       → Rifiuta suggerimento
       Body: {notes}

GET    /api/projects/{id}/authorization-queue
       → Coda richieste autorizzazione per dashboard
```

---

## 🎨 COMPONENTI FRONTEND DETTAGLIATI

### 1. LabelingPanel (Componente Principale)
**File**: `app/static/js/components/LabelingPanel.js`
**Posizione**: Integrato nelle view colonne/righe

```javascript
class LabelingPanel {
    constructor(containerId, options) {
        this.container = document.getElementById(containerId);
        this.projectId = options.projectId;
        this.selectedCells = [];
        this.availableLabels = [];
    }
    
    // Metodi principali
    updateSelection(cells)           // Aggiorna celle selezionate
    loadAvailableLabels()           // Carica etichette progetto
    showLabelSelector()             // Mostra dropdown etichette
    createNewLabel()                // Modal nuova etichetta  
    applyManualLabel(labelId)       // Applicazione immediata
    requestAILabeling()             // Richiesta AI con autorizzazione
}
```

### 2. LabelCreationModal
**File**: `app/static/js/components/LabelCreationModal.js`

```javascript
class LabelCreationModal {
    constructor() {
        this.modal = null;
        this.form = null;
    }
    
    show(callback)                  // Mostra modal creazione
    validate()                      // Validazione form
    save()                         // Salva nuova etichetta
    hide()                         // Chiudi modal
}
```

### 3. AuthorizationModal  
**File**: `app/static/js/components/AuthorizationModal.js`

```javascript
class AuthorizationModal {
    constructor() {
        this.suggestions = [];
        this.currentSuggestion = 0;
    }
    
    show(suggestions)               // Mostra suggerimenti AI
    renderSuggestion(suggestion)    // Render singolo suggerimento
    approve(suggestionId, notes)    // Approva suggerimento
    reject(suggestionId, notes)     // Rifiuta suggerimento
    batchApprove(suggestions)       // Approvazione batch
}
```

### 4. AuthorizationQueue (Header Component)
**File**: `app/static/js/components/AuthorizationQueue.js`

```javascript
class AuthorizationQueue {
    constructor() {
        this.badge = document.getElementById('auth-queue-badge');
        this.dropdown = document.getElementById('auth-queue-dropdown');
    }
    
    updateCount()                   // Aggiorna numero badge
    loadPendingRequests()          // Carica richieste pendenti
    showDropdown()                 // Lista richieste in dropdown
}
```

---

## 🧪 STRATEGIA TESTING

### Backend Tests
```
tests/test_labeling_system.py
├── test_create_manual_label()
├── test_apply_manual_labeling()  
├── test_ai_suggestion_workflow()
├── test_authorization_process()
└── test_store_management()
```

### Frontend Tests  
```
tests/test_labeling_components.js
├── test_labeling_panel_integration()
├── test_label_creation_modal()
├── test_authorization_workflow()  
└── test_queue_notifications()
```

### Integration Tests
```
tests/test_labeling_integration.py
├── test_full_manual_workflow()
├── test_full_ai_workflow()
├── test_authorization_end_to_end()
└── test_store_sync_with_applications()
```

---

## 📊 METRICHE DI SUCCESSO

### Funzionalità
- ✅ Etichettatura manuale funziona in <2 click
- ✅ AI richiede sempre autorizzazione (0 applicazioni automatiche)
- ✅ Store centralizzato sincronizzato con applicazioni
- ✅ Suggerimenti AI con confidence score visibile

### UX
- ✅ Workflow intuitivo senza training
- ✅ Tempo medio autorizzazione AI <30 secondi
- ✅ Zero perdita dati durante workflow
- ✅ Notifiche real-time per richieste pendenti

### Performance  
- ✅ Caricamento etichette progetto <1 secondo
- ✅ Applicazione manuale etichetta <500ms
- ✅ Suggerimenti AI <5 secondi
- ✅ Sincronizzazione store <1 secondo

---

**Prossimo Step**: Iniziare con Task 2.1 - Database Schema  
**Tempo stimato Task 2.1**: 4-6 ore  
**Deliverable**: Migrazione database + test schema completo
