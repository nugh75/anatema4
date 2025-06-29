# Struttura Database - Sistema Anatema2

**Ultima analisi**: 30 giugno 2025

## 📊 Schema Database Completo

### 🔍 Organizzazione dei Modelli

Il sistema è organizzato in 3 file principali di modelli:

1. **`app/models.py`** - Modelli core dell'applicazione
2. **`app/models_admin.py`** - Sistema amministrazione e configurazioni globali  
3. **`app/models_labeling.py`** - Sistema etichettatura separato dal ML

---

## 📋 TABELLE PRINCIPALI (models.py)

### 🧑‍💼 Sistema Utenti e Progetti

#### `users` - Utenti del sistema
```sql
- id: UUID (PK)
- username: VARCHAR(80) UNIQUE
- email: VARCHAR(120) UNIQUE  
- password_hash: VARCHAR(255)
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- role: VARCHAR(20) DEFAULT 'user'
- is_active: BOOLEAN DEFAULT TRUE
- admin_flag: BOOLEAN DEFAULT FALSE
- is_superuser: BOOLEAN DEFAULT FALSE
- last_login: DATETIME
- login_attempts: INTEGER DEFAULT 0
- locked_until: DATETIME
- email_verified: BOOLEAN DEFAULT FALSE
- email_verification_token: VARCHAR(100)
- created_at, updated_at: DATETIME
```

#### `projects` - Progetti degli utenti
```sql
- id: UUID (PK)
- owner_id: UUID (FK users.id)
- name: VARCHAR(200)
- description: TEXT
- is_public: BOOLEAN DEFAULT FALSE
- created_at, updated_at: DATETIME
```

### 📁 Sistema File e Dati

#### `files` - File caricati
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- uploader_id: UUID (FK users.id)
- filename: VARCHAR(255)
- original_name: VARCHAR(255)
- file_type: VARCHAR(50)
- file_size: INTEGER
- file_path: VARCHAR(500)
- processing_status: VARCHAR(20) DEFAULT 'pending'
- uploaded_at: DATETIME
```

#### `excel_sheets` - Fogli Excel
```sql
- id: UUID (PK)
- file_id: UUID (FK files.id)
- sheet_index: INTEGER
- name: VARCHAR(255)
- row_count: INTEGER DEFAULT 0
- column_count: INTEGER DEFAULT 0
```

#### `excel_columns` - Colonne Excel
```sql
- id: UUID (PK)
- sheet_id: UUID (FK excel_sheets.id)
- column_index: INTEGER
- name: VARCHAR(1000)  -- ⚡ AUMENTATO DA 255
- data_type: VARCHAR(50) DEFAULT 'text'
```

#### `excel_rows` - Righe Excel
```sql
- id: UUID (PK)
- sheet_id: UUID (FK excel_sheets.id)
- row_index: INTEGER
- data: JSON  -- Dati della riga
```

### 🏷️ Sistema Etichette Base

#### `labels` - Etichette progetto
```sql
- id: INTEGER (PK)
- project_id: UUID (FK projects.id)
- name: VARCHAR(100)
- description: TEXT
- color: VARCHAR(7) DEFAULT '#1976d2'
- categories: ARRAY[VARCHAR]
- created_at: DATETIME
```

#### `cell_labels` - Etichette applicate alle celle
```sql
- id: UUID (PK)
- row_id: UUID (FK excel_rows.id)
- label_id: INTEGER (FK labels.id)
- column_index: INTEGER
- cell_value: TEXT
- created_at: DATETIME
- created_by: UUID (FK users.id)
```

### 🤖 Sistema Machine Learning

#### `ml_analyses` - Analisi ML
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- file_id: UUID (FK files.id)
- sheet_id: UUID (FK excel_sheets.id)
- ml_provider: VARCHAR(50)  -- 'openrouter', 'ollama'
- ml_model: VARCHAR(100)
- analysis_type: VARCHAR(50)  -- 'auto_labeling', 'column_detection'
- status: VARCHAR(20) DEFAULT 'pending'
- results: JSON
- error_message: TEXT
- processing_time: FLOAT
- created_at, updated_at: DATETIME
```

#### `column_analyses` - Analisi colonne
```sql
- id: UUID (PK)
- ml_analysis_id: UUID (FK ml_analyses.id)
- column_id: UUID (FK excel_columns.id)
- detected_type: VARCHAR(50)
- confidence_score: FLOAT
- unique_values_count: INTEGER
- null_values_count: INTEGER
- avg_text_length: FLOAT
- text_variability: FLOAT
- is_open_question: BOOLEAN DEFAULT FALSE
- question_complexity: VARCHAR(20)
```

#### `auto_labels` - Etichette generate automaticamente
```sql
- id: UUID (PK)
- ml_analysis_id: UUID (FK ml_analyses.id)
- column_analysis_id: UUID (FK column_analyses.id)
- column_name: VARCHAR(1000)  -- ⚡ AUMENTATO DA 255
- label_name: VARCHAR(200)
- label_description: TEXT
- label_type: VARCHAR(50) DEFAULT 'auto'
- category: VARCHAR(100)
- theme: VARCHAR(100)
- cluster_id: INTEGER
- cluster_size: INTEGER
- representative_texts: ARRAY[TEXT]
- sentiment_label: VARCHAR(20)
- sentiment_score: FLOAT
- emotion_tags: ARRAY[VARCHAR]
- confidence_score: FLOAT
- manual_validation: VARCHAR(20)
- validated_by: UUID (FK users.id)
- validated_at: DATETIME
- applied_count: INTEGER DEFAULT 0
- created_at: DATETIME
- created_by: UUID (FK users.id)
```

#### `auto_label_applications` - Applicazioni etichette auto
```sql
- id: UUID (PK)
- auto_label_id: UUID (FK auto_labels.id)
- row_id: UUID (FK excel_rows.id) -- NULLABLE
- row_index: INTEGER
- column_name: VARCHAR(1000)  -- ⚡ AUMENTATO DA 255
- cell_value: TEXT
- confidence_score: FLOAT
- applied_at: DATETIME
- applied_by: UUID (FK users.id)
- status: VARCHAR(20) DEFAULT 'suggested'
```

#### `ml_configurations` - Configurazioni ML per progetto
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- created_by: UUID (FK users.id)
- name: VARCHAR(200)
- description: TEXT
- ml_provider: VARCHAR(50)
- ml_model: VARCHAR(100)
- api_key_encrypted: TEXT
- api_url: VARCHAR(500)
- auto_detect_columns: BOOLEAN DEFAULT TRUE
- min_unique_values: INTEGER DEFAULT 3
- max_text_length: INTEGER DEFAULT 1000
- clustering_min_samples: INTEGER DEFAULT 5
- sentiment_analysis_enabled: BOOLEAN DEFAULT TRUE
- is_active: BOOLEAN DEFAULT FALSE
- created_at, updated_at: DATETIME
```

---

## 🛡️ TABELLE AMMINISTRAZIONE (models_admin.py)

### 🔧 Configurazioni Globali

#### `global_llm_configurations` - Configurazioni LLM globali
```sql
- id: UUID (PK)
- name: VARCHAR(100)
- description: TEXT
- is_active: BOOLEAN DEFAULT FALSE
- is_default: BOOLEAN DEFAULT FALSE
- provider: VARCHAR(50)  -- 'openai', 'anthropic', etc.
- model_name: VARCHAR(100)
- api_url: VARCHAR(255)
- api_key_encrypted: TEXT
- additional_headers: JSON
- max_tokens: INTEGER DEFAULT 4000
- temperature: FLOAT DEFAULT 0.7
- max_requests_per_minute: INTEGER DEFAULT 60
- max_requests_per_day: INTEGER DEFAULT 1000
- cost_per_token: FLOAT DEFAULT 0.0
- total_requests: INTEGER DEFAULT 0
- total_tokens_used: INTEGER DEFAULT 0
- total_cost: FLOAT DEFAULT 0.0
- last_used_at: DATETIME
- created_at, updated_at: DATETIME
- created_by: UUID (FK users.id)
```

### 👥 Sistema Ruoli

#### `user_roles` - Ruoli utente
```sql
- id: INTEGER (PK)
- name: VARCHAR(50) UNIQUE
- description: TEXT
- permissions: JSON  -- Lista permessi
- created_at, updated_at: DATETIME
```

#### `user_role_assignments` - Assegnazioni ruoli
```sql
- id: INTEGER (PK)
- user_id: UUID (FK users.id)
- role_id: INTEGER (FK user_roles.id)
- assigned_at: DATETIME
- assigned_by: UUID (FK users.id)
```

### ⚙️ Impostazioni Sistema

#### `system_settings` - Configurazioni sistema
```sql
- id: INTEGER (PK)
- app_name: VARCHAR(100) DEFAULT 'Anatema'
- app_version: VARCHAR(20) DEFAULT '2.0.0'
- app_description: TEXT
- theme: VARCHAR(20) DEFAULT 'light'
- primary_color: VARCHAR(7) DEFAULT '#1976d2'
- secondary_color: VARCHAR(7) DEFAULT '#dc004e'
- max_projects_per_user: INTEGER DEFAULT 10
- max_file_size_mb: INTEGER DEFAULT 100
- max_files_per_project: INTEGER DEFAULT 50
- session_timeout_minutes: INTEGER DEFAULT 120
- password_min_length: INTEGER DEFAULT 8
- require_email_verification: BOOLEAN DEFAULT FALSE
- max_login_attempts: INTEGER DEFAULT 5
- maintenance_mode: BOOLEAN DEFAULT FALSE
- maintenance_message: TEXT
- enable_email_notifications: BOOLEAN DEFAULT FALSE
- enable_system_logs: BOOLEAN DEFAULT TRUE
- log_level: VARCHAR(20) DEFAULT 'INFO'
- created_at, updated_at: DATETIME
- updated_by: UUID (FK users.id)
```

### 📋 Audit e Logging

#### `audit_logs` - Log delle attività
```sql
- id: INTEGER (PK)
- user_id: UUID (FK users.id)
- action: VARCHAR(100)
- resource_type: VARCHAR(50)  -- 'user', 'project', 'llm_config'
- resource_id: VARCHAR(100)
- description: TEXT
- old_values: JSON
- new_values: JSON
- ip_address: VARCHAR(45)
- user_agent: TEXT
- timestamp: DATETIME
```

---

## 🏷️ SISTEMA ETICHETTATURA AVANZATO (models_labeling.py)

### 📝 Template e Generazione

#### `label_templates` - Template prompt AI
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- created_by: UUID (FK users.id)
- name: VARCHAR(200)
- description: TEXT
- category: VARCHAR(100)  -- 'sentiment', 'emotion', 'behavior'
- system_prompt: TEXT
- user_prompt_template: TEXT
- preferred_model: VARCHAR(100)
- temperature: FLOAT DEFAULT 0.7
- max_tokens: INTEGER DEFAULT 1000
- expected_labels_count: INTEGER DEFAULT 5
- output_format: VARCHAR(50) DEFAULT 'json'
- is_active: BOOLEAN DEFAULT TRUE
- usage_count: INTEGER DEFAULT 0
- created_at, updated_at: DATETIME
```

#### `label_generations` - Sessioni generazione AI
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- sheet_id: UUID (FK excel_sheets.id)
- template_id: UUID (FK label_templates.id)
- created_by: UUID (FK users.id)
- column_name: VARCHAR(1000)  -- ⚡ CAMPO LUNGO
- sample_data: JSON
- ai_provider: VARCHAR(50)
- ai_model: VARCHAR(100)
- raw_ai_response: TEXT
- processing_time: FLOAT
- status: VARCHAR(20) DEFAULT 'pending'
- error_message: TEXT
- total_suggestions: INTEGER DEFAULT 0
- approved_suggestions: INTEGER DEFAULT 0
- rejected_suggestions: INTEGER DEFAULT 0
- created_at: DATETIME
```

### 💡 Suggerimenti e Approvazioni

#### `label_suggestions` - Suggerimenti AI
```sql
- id: UUID (PK)
- generation_id: UUID (FK label_generations.id)
- suggested_name: VARCHAR(200)
- suggested_description: TEXT
- suggested_category: VARCHAR(100)
- suggested_color: VARCHAR(7) DEFAULT '#1976d2'
- ai_confidence: FLOAT
- ai_reasoning: TEXT
- sample_values: JSON
- status: VARCHAR(20) DEFAULT 'pending'  -- 'approved', 'rejected', 'modified'
- reviewed_by: UUID (FK users.id)
- reviewed_at: DATETIME
- review_notes: TEXT
- final_name: VARCHAR(200)
- final_description: TEXT
- final_category: VARCHAR(100)
- final_color: VARCHAR(7)
- created_label_id: INTEGER (FK labels.id)
- created_at: DATETIME
```

### 🎯 Applicazioni Etichette

#### `label_applications` - Applicazioni etichette
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- sheet_id: UUID (FK excel_sheets.id)
- label_id: INTEGER (FK labels.id)
- applied_by: UUID (FK users.id)
- row_index: INTEGER
- column_name: VARCHAR(1000)  -- ⚡ CAMPO LUNGO
- cell_value: TEXT
- application_type: VARCHAR(20)  -- 'manual', 'ai_batch', 'ai_single'
- confidence_score: FLOAT
- ai_session_id: UUID
- ai_reasoning: TEXT
- is_active: BOOLEAN DEFAULT TRUE
- applied_at: DATETIME
```

#### `ai_labeling_sessions` - Sessioni etichettatura AI
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- sheet_id: UUID (FK excel_sheets.id)
- created_by: UUID (FK users.id)
- target_type: VARCHAR(20)  -- 'column', 'row', 'range'
- target_name: VARCHAR(255)
- available_labels: JSON
- ai_provider: VARCHAR(50)
- ai_model: VARCHAR(100)
- custom_prompt: TEXT
- status: VARCHAR(20) DEFAULT 'pending'
- error_message: TEXT
- processing_time: FLOAT
- total_cells_processed: INTEGER DEFAULT 0
- successful_applications: INTEGER DEFAULT 0
- failed_applications: INTEGER DEFAULT 0
- created_at: DATETIME
```

### 📊 Analytics

#### `label_analytics` - Statistiche etichette
```sql
- id: UUID (PK)
- project_id: UUID (FK projects.id)
- label_id: INTEGER (FK labels.id)
- total_applications: INTEGER DEFAULT 0
- manual_applications: INTEGER DEFAULT 0
- ai_applications: INTEGER DEFAULT 0
- sheet_distribution: JSON
- column_distribution: JSON
- first_used: DATETIME
- last_used: DATETIME
- usage_frequency: FLOAT
- avg_ai_confidence: FLOAT
- human_override_rate: FLOAT
- calculated_at: DATETIME
```

---

## 🔗 RELAZIONI PRINCIPALI

### User Relationships
```
User (1) -> (N) Projects
User (1) -> (N) Files
User (1) -> (N) CellLabels
User (1) -> (N) MLAnalyses
User (1) -> (N) AutoLabels
User (1) -> (N) LabelApplications
```

### Project Hierarchy
```
Project (1) -> (N) Files
File (1) -> (N) ExcelSheets
ExcelSheet (1) -> (N) ExcelColumns
ExcelSheet (1) -> (N) ExcelRows
ExcelRow (1) -> (N) CellLabels
```

### ML/AI Flow
```
MLAnalysis (1) -> (N) ColumnAnalysis
ColumnAnalysis (1) -> (N) AutoLabels
AutoLabel (1) -> (N) AutoLabelApplication
```

### Labeling System Flow
```
LabelTemplate (1) -> (N) LabelGeneration
LabelGeneration (1) -> (N) LabelSuggestion
LabelSuggestion (1) -> (1) Label
Label (1) -> (N) LabelApplication
```

---

## 🔧 INDICI DATABASE

### Performance Indexes
```sql
-- Users
idx_users_username, idx_users_email, idx_users_is_active
idx_users_admin_flag, idx_users_email_verified, idx_users_role

-- Projects & Files
idx_projects_owner, idx_files_project, idx_excel_sheets_file
idx_excel_rows_sheet, idx_excel_columns_sheet

-- Labels
idx_labels_project, idx_cell_labels_row, idx_cell_labels_label

-- ML System
idx_ml_analyses_project, idx_ml_analyses_file, idx_ml_analyses_sheet
idx_column_analyses_ml_analysis, idx_auto_labels_ml_analysis

-- Advanced Labeling
idx_label_templates_project, idx_label_generations_project
idx_label_applications_project, idx_label_applications_sheet
```

---

## ✅ STATO ATTUALE DATABASE (30 Giugno 2025)

### 📊 Verifica Database
**Connessione verificata**: ✅ Successo  
**Versione migrazione corrente**: `1b3e32d81e77`  
**Tabelle totali presenti**: **25 tabelle**

### 🏗️ Tabelle Implementate e Attive

#### ✅ TABELLE CORE (8/8) - 100% Implementate
```
users                   ✅ Utenti del sistema
projects               ✅ Progetti utenti  
files                  ✅ File caricati
excel_sheets           ✅ Fogli Excel
excel_columns          ✅ Colonne Excel (campo name: 1000 char)
excel_rows             ✅ Righe Excel
labels                 ✅ Etichette progetto
cell_labels            ✅ Etichette applicate celle
```

#### ✅ TABELLE ML (5/5) - 100% Implementate
```
ml_analyses            ✅ Analisi ML
ml_configurations      ✅ Configurazioni ML progetto
column_analyses        ✅ Analisi colonne
auto_labels            ✅ Etichette auto-generate (campo column_name: 1000 char)
auto_label_applications ✅ Applicazioni etichette auto (campo column_name: 1000 char)
```

#### ✅ TABELLE LABELING (6/6) - 100% Implementate
```
label_templates        ✅ Template prompt AI
label_generations      ✅ Sessioni generazione AI (campo column_name: 1000 char)
label_suggestions      ✅ Suggerimenti AI
label_applications     ✅ Applicazioni etichette (campo column_name: 1000 char)
ai_labeling_sessions   ✅ Sessioni etichettatura AI
label_analytics        ✅ Statistiche etichette
```

#### ✅ TABELLE ADMIN (5/5) - 100% Implementate
```
global_llm_configurations ✅ Configurazioni LLM globali
user_roles             ✅ Ruoli utente
user_role_assignments  ✅ Assegnazioni ruoli
system_settings        ✅ Configurazioni sistema
audit_logs             ✅ Log attività
```

#### 📋 TABELLE SISTEMA (1)
```
alembic_version        ✅ Versioni migrazioni Alembic
```

### 🎯 Risultato Analisi
**✅ SCHEMA COMPLETAMENTE IMPLEMENTATO**
- **Tutte le 24 tabelle** del sistema sono presenti e attive
- **Tutti i fix applicati** (campo column_name esteso a 1000 caratteri)
- **Sistema modulare completo**: Core + ML + Labeling + Admin
- **Migrazioni aggiornate** alla versione più recente

---

## ⚡ MODIFICHE RECENTI

### Fix Database (29-30/06/2025)
1. **Campo `column_name` esteso a 1000 caratteri** in:
   - `excel_columns.name`
   - `auto_labels.column_name`
   - `auto_label_applications.column_name`
   - `label_generations.column_name`
   - `label_applications.column_name`

2. **Implementazione completa sistema labeling** separato dal ML

3. **Sistema admin robusto** con configurazioni globali LLM

---

## 📂 Implementazione File

```
app/
├── models.py              # Modelli core (13 tabelle) ✅ IMPLEMENTATO
├── models_admin.py        # Sistema admin (5 tabelle) ✅ IMPLEMENTATO  
├── models_labeling.py     # Sistema labeling (6 tabelle) ✅ IMPLEMENTATO
└── database.py           # Configurazione SQLAlchemy ✅ ATTIVO
```

### 🔄 Migrazioni Database
```
migrations/versions/
├── f78cf5b68592_*.py     # Aumento excel_columns.name
├── 31a1010edf92_*.py     # Aggiunta tabelle ML
├── d9a7149d6ee7_*.py     # Fix colonne auto_labels  
├── 55b5e6ecb2a3_*.py     # Sistema labeling avanzato
├── 5661a6768144_*.py     # Colonna is_active users
└── 1b3e32d81e77_*.py     # Fix finale column_name 1000 char ⚡ ATTUALE
```

**Totale Tabelle Database**: 25 tabelle (24 funzionali + 1 sistema)  
**Database**: PostgreSQL con supporto UUID, JSON, ARRAY  
**ORM**: SQLAlchemy con Flask-SQLAlchemy  
**Stato**: ✅ **COMPLETAMENTE IMPLEMENTATO E ATTIVO**
