# Master Plan: Refactoring Sistema Etichettatura Umano/Macchina

**Documento Master - Contiene tutto il piano, stato attuale e roadmap**  
**Aggiornato**: 6 luglio 2025, ore 23:45  
**Versione**: 2.9 - Task 2.5 Completato - AI con Autorizzazioni  
**Stato**: Fase 1 Completata (100%) - Fase 2 Completata (100%) - Task 2.6 prossimo

**🗂️ DOCUMENTAZIONE RISTRUTTURATA**: File obsoleti rimossi, task reports integrati, incongruenze risolte

---

## 📋 INDICE RAPIDO

- [**STATO ATTUALE PROGETTO**](#-stato-attuale-progetto) - Dove siamo ora
- [**COSE DA FARE SUBITO**](#-cose-da-fare-subito) - Prossimi task
- [**PIANO COMPLETO**](#-piano-completo) - Roadmap completa delle 7 fasi
- [**ARCHITETTURA TARGET**](#-architettura-target) - Obiettivo finale
- [**PROBLEMI RISOLTI**](#-problemi-risolti) - Fix applicati e loro dettagli
- [**FILES E TESTING**](#-files-e-testing) - Stato modifiche e test

---

## 🎯 STATO ATTUALE PROGETTO

### Progresso Generale
- **Fase 1 (Pulizia Base)**: 100% completato (6/6 task) ✅ **COMPLETATA**
- **Fase 2 (Sistema Unificato)**: 83% completato (5/6 task) ✅ 
- **Task 2.5**: SBLOCCATO e pronto per implementazione 🚀
- **Tempo stimato completamento Task 2.5**: 1-2 giorni lavorativi

### Task Completati ✅
1. **Task 1.1** - Rinomina "Machine Learning" → "Etichettatura Umano/Macchina"
2. **Task 1.2** - Nuovo dashboard principale semplificato  
3. **Task 1.3** - Eliminazione "Pannello Etichettatura" dalle view
4. **Task 1.4** - Rimozione template e route obsoleti del sistema ML ✅ **COMPLETATO**
5. **Task 1.5** - Aggiornamento routing e navigazione
6. **Task 1.6** - Test navigazione e accesso view principali
7. **Task 2.1** - Database Schema per autorizzazioni ✅ **COMPLETATO**
8. **Task 2.2** - Backend API per sistema etichettatura unificato ✅ **COMPLETATO**
9. **Task 2.3** - Frontend Components - Integrazione UI etichettatura unificata ✅ **COMPLETATO**
10. **Task 2.4** - Store Etichette Centralizzato ✅ **COMPLETATO AL 100%**

### Task In Corso 🔄
- **Task 2.5** - Integrazione AI con Autorizzazioni (PRIORITÀ MASSIMA - PROSSIMO)

## 🚀 COSE DA FARE SUBITO

### 🔥 Task 2.5 - Integrazione AI con Autorizzazioni (PRIORITÀ MASSIMA - PROSSIMO)
**Obiettivo**: Implementare sistema AI che richiede sempre autorizzazione umana

**Componenti da implementare**:
1. **AI Suggestions Engine**: Sistema AI per analisi celle e suggerimenti etichette
2. **Authorization Workflow**: Interfaccia approvazione/rifiuto suggerimenti AI
3. **Batch Processing**: Gestione suggerimenti multipli con batch approval
4. **Confidence Scoring**: Visualizzazione score di confidenza AI
5. **Reasoning Display**: Mostra il ragionamento AI per ogni suggerimento
6. **Notification System**: Badge e notifiche per richieste pendenti

**Integrazione**:
- Collegare con pannello etichettatura unificato (Task 2.3)
- Utilizzare store etichette centralizzato (Task 2.4)
- API backend già implementate (Task 2.2)

**Tempo stimato**: 1-2 giorni  
**Dipendenze**: ✅ Task 2.1-2.4 (DB, API, Frontend, Store) - **TUTTE COMPLETATE**

### 3. Unificazione Tabella Etichette (Priorità CRITICA)
**Problema**: Sistema etichette frammentato su 3 tabelle diverse:
- `cell_labels` (sistema originale) 
- `auto_label_applications` (AI legacy)
- `label_applications` (nuovo sistema)

**Soluzione**: Migrare tutto su `label_applications` (schema più completo)

**Documenti di riferimento**:
- [`docs/ANALISI_FRAMMENTAZIONE_ETICHETTE.md`](docs/ANALISI_FRAMMENTAZIONE_ETICHETTE.md) - Analisi dettagliata del problema
- [`docs/MULTIPLE_LABELS_IMPLEMENTATION.md`](docs/MULTIPLE_LABELS_IMPLEMENTATION.md) - Piano implementazione tecnica

### 4. Fase 2 - Sistema Etichette Unificato (Priorità ALTA)
- Progettare componente condiviso per gestione etichette
- Implementare autocomplete e suggerimenti
- Integrare con sistema etichette progetto esistente

---

## 🎯 ARCHITETTURA TARGET

### Struttura View Finale
```
Etichettatura Umano/Macchina/
├── Dashboard Principale (✅ Completato)
├── View Colonne (🔄 Da refactorare in Fase 3)
└── View Righe (🔄 Da refactorare in Fase 4)
```

### Comportamenti Standardizzati

#### View Colonne
- **Target**: Etichettatura di celle della stessa colonna (stesso tema)
- **Selezione**: Singola cella o multiple celle
- **Etichettatura**: Manuale, AI singola, AI batch
- **Etichette multiple**: Supportate per cella

#### View Righe  
- **Target**: Etichettatura di celle sparse (temi diversi)
- **Contesto**: Visualizzazione di tutte le celle della riga
- **Selezione**: Solo cella singola per volta
- **Etichettatura**: Manuale, AI singola
- **Etichette multiple**: Supportate per cella

### Sistema Etichette Unificato (Target Fase 2)
- **Tabella unica**: `label_applications` per tutte le etichette
- **Creazione rapida**: Box integrato in entrambe le view
- **Riutilizzo**: Dropdown con etichette esistenti del progetto
- **AI Integration**: Suggerimenti automatici e confidence scoring

---

## 📋 PIANO COMPLETO (7 FASI)

### Fase 1: Pulizia e Ristrutturazione Base (100% ✅ COMPLETATA)
- [x] **1.1** Rinomina "Machine Learning" → "Etichettatura Umano/Macchina" ✅
- [x] **1.2** Nuovo dashboard principale semplificato ✅
- [x] **1.3** Rimozione "Pannello Etichettatura" dalle view ✅
- [x] **1.4** Identificare e rimuovere view obsolete ✅ **COMPLETATO**
- [x] **1.5** Aggiornamento routing e navigazione ✅
- [x] **1.6** Test navigazione e accesso view principali ✅

### 🔥 FASE 2 ACCELERATA: Sistema Etichette Unificato (83% COMPLETATA)
- [x] **2.1** Database Schema - Supporto workflow autorizzazioni ✅ **COMPLETATO**
- [x] **2.2** Backend API - Endpoint etichettatura e autorizzazioni ✅ **COMPLETATO**
- [x] **2.3** Frontend Components - Pannelli etichettatura integrati ✅ **COMPLETATO**
- [x] **2.4** Store Etichette Centralizzato - Gestione etichette progetto ✅ **COMPLETATO**
- [ ] **2.5** Integrazione AI con Autorizzazioni - Sistema approvazione 🔄 **PROSSIMO**
- [ ] **2.6** Testing e Validazione - Test workflow completo

### Fase 3: Refactor View Colonne
- [ ] **3.1** Semplificare interfaccia rimuovendo elementi non necessari
- [ ] **3.2** Migliorare selezione multipla celle
- [ ] **3.3** Integrare sistema etichette unificato
- [ ] **3.4** Ottimizzare AI batch processing
- [ ] **3.5** Implementare etichettatura multipla per cella
- [ ] **3.6** Test: Tutti i flussi di etichettatura colonne

### Fase 4: Refactor View Righe
- [ ] **4.1** Ridisegnare per focus su cella singola con contesto riga
- [ ] **4.2** Integrare sistema etichette unificato
- [ ] **4.3** Implementare visualizzazione contesto altre celle
- [ ] **4.4** Implementare etichettatura multipla per cella
- [ ] **4.5** Aggiungere suggerimenti AI per cella singola
- [ ] **4.6** Test: Tutti i flussi di etichettatura righe

### Fase 5: Integrazione AI Migliorata
- [ ] **5.1** Unificare system prompt AI tra view
- [ ] **5.2** Implementare suggerimenti contestuali
- [ ] **5.3** Aggiungere feedback loop per migliorare AI
- [ ] **5.4** Implementare confidence scoring visivo
- [ ] **5.5** Test: Funzionalità AI e accuratezza suggerimenti

### Fase 6: UX e Performance
- [ ] **6.1** Ottimizzare loading e responsività
- [ ] **6.2** Aggiungere indicatori di progresso
- [ ] **6.3** Implementare shortcuts da tastiera
- [ ] **6.4** Aggiungere tooltips e guide utente
- [ ] **6.5** Test: Performance e usabilità

### Fase 7: Testing e Documentazione
- [ ] **7.1** Test end-to-end completi
- [ ] **7.2** Test di stress e performance
- [ ] **7.3** Documentazione utente
- [ ] **7.4** Training materiali
- [ ] **7.5** Test: Acceptance testing completo

---

## ✅ PROBLEMI RISOLTI

### 1. Fix Database - Campo column_name (29/06/2025)
**Problema**: `StringDataRightTruncation` - nomi colonne lunghi (>255 char) causavano errori  
**Soluzione**: Migrazione database per aumentare `column_name` da 255 a 1000 caratteri  
**File modificati**: 
- `migrations/versions/f78cf5b68592_increase_excel_columns_name_field_.py`
- `app/models.py` (AutoLabel, AutoLabelApplication)
- `app/models_labeling.py` (LabelGeneration, LabelApplication)

### 2. Fix Etichettatura AI Batch - Salvataggio (29/06/2025)
**Problema**: La funzione `batch_ai_label` generava etichette ma non le salvava  
**Soluzione**: Implementato salvataggio nel database  
**Funzionalità aggiunte**:
- Creazione/riutilizzo AutoLabel per ogni etichetta generata
- Salvataggio AutoLabelApplication per ogni cella etichettata
- Reporting del numero di etichette effettivamente salvate
**File modificati**: `app/views/ml.py` (funzione `batch_ai_label`)

### 3. Fix Routing - Conflitto Blueprint (29/06/2025)
**Problema**: Import da `app.views.labeling` causava conflitti di routing  
**Soluzione**: Rimosso import problematico e sostituito con placeholder  
**File modificati**: `app/views/ml.py` (rimosso import da labeling.py)

### 4. Task 1.4 - Rimozione Template Obsoleti (29/06/2025) ✅ COMPLETATO
**Problema**: Template e route ML obsoleti aumentavano complessità e confusione
**Soluzione**: Analisi approfondita e rimozione sistematica di codice non utilizzato

**Template e route rimossi**:
- ❌ `app/templates/ml/view_columns.html` + route
- ❌ `app/templates/ml/view_rows.html` + route  
- ❌ `app/templates/ml/select_column.html` + route
- ❌ `app/templates/ml/select_row.html` + route
- ❌ `app/templates/ml/single_column_view.html` + funzione `single_column_view()`
- ❌ `app/templates/ml/single_row_view.html` + funzione `single_row_view()`

**Template preservati (funzionali)**:
- ✅ `advanced_column_view.html` - Vista avanzata colonne
- ✅ `advanced_row_view.html` - Vista avanzata righe
- ✅ `analysis_results.html` - Risultati analisi ML
- ✅ `configure.html` - Configurazione ML  
- ✅ `new_dashboard.html` - Dashboard ML principale

**Benefici**:
- ✅ Riduzione complessità del codice (6 template e 2 route eliminati)
- ✅ Eliminazione funzionalità duplicate
- ✅ Chiarezza nelle opzioni disponibili per gli utenti
- ✅ Manutenibilità migliorata
- ✅ Preparazione per sistema etichettatura unificato

**File modificati**: 
- `app/views/ml.py` (rimosse funzioni `single_column_view`, `single_row_view`)
- `app/templates/ml/` (rimossi 6 template obsoleti)

**Documentazione**: [`docs/TASK_1_4_COMPLETION_REPORT.md`](TASK_1_4_COMPLETION_REPORT.md)
**Problema**: Le view colonne/righe avevano un pannello laterale complesso e confuso  
**Soluzione**: Rimosso completamente il "Pannello Etichettatura"

**Benefici ottenuti**:
- ✅ Interfaccia molto più pulita e meno confusa
- ✅ Focus sui dati invece che sui controlli
- ✅ Layout a 2 colonne invece di 3 (più spazio per i dati)
- ✅ Riduzione del cognitive load per l'utente
- ✅ Codice JavaScript ridotto (~230 righe rimosse)
- ✅ Vista pulita pronta per il nuovo sistema etichette unificato

**File modificati**: 
- `app/templates/ml/advanced_column_view.html` (~150 righe rimosse)
- `app/templates/ml/advanced_row_view.html` (~120 righe rimosse)

### 5. Task 2.4 - Fix Errore Template Jinja2 (6 luglio 2025) ✅ COMPLETATO
**Problema**: `TypeError: unsupported operand type(s) for +: 'int' and 'method'` in `projects/view.html`
**Causa**: Template Jinja2 tentava di sommare metodi `cell_labels.count()` invece di valori numerici
**Soluzione**: Sostituito `cell_labels.count` con `usage_count` in tutti i template

**Modifiche implementate**:
- ✅ Template `projects/view.html` corretto: `labels|sum(attribute='usage_count')`
- ✅ Backend `projects.py` aggiornato: aggiornamento automatico `usage_count` 
- ✅ Tutte le occorrenze di `cell_labels.count` rimosse dai template
- ✅ Sistema di statistiche etichette funzionante

**Benefici**:
- ✅ Pagina progetto visualizzabile senza errori
- ✅ Statistiche etichette accurate (Total, Unused, etc.)
- ✅ Performance migliorata (evita query dinamiche nel template)
- ✅ Preparazione per Task 2.5 (sistema pronto per AI)

**File modificati**: 
- `app/templates/projects/view.html` (corretti 3 riferimenti Jinja2)
- `app/views/projects.py` (aggiunto aggiornamento automatico usage_count)

---
