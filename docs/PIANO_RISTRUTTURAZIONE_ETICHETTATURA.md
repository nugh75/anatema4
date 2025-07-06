# Piano di Ristrutturazione: Sistema di Etichettatura Umano/Macchina

## 📋 Analisi Situazione Attuale

### Problemi Identificati
1. **Complessità eccessiva**: Troppe view ML confuse
2. **Naming inadeguato**: "Machine Learning" non rappresenta la funzionalità
3. **Duplicazione funzionalità**: View simili con logiche diverse
4. **UX inconsistente**: Comportamenti diversi tra view colonne e righe
5. **Sistema etichette frammentato**: Non condiviso tra le view

### Obiettivi della Ristrutturazione
1. **Semplificazione**: Solo 2 view principali (Colonne e Righe)
2. **Denominazione chiara**: "Etichettatura Umano/Macchina"
3. **Sistema etichette unificato**: Condiviso tra tutte le view
4. **UX coerente**: Comportamenti standardizzati
5. **Funzionalità AI integrate**: Suggerimenti e batch processing

## 🎯 Architettura Target

### 1. Struttura delle View
```
Etichettatura Umano/Macchina/
├── Dashboard Principale
├── View Colonne (Advanced Column View rinnovata)
└── View Righe (Advanced Row View rinnovata)
```

### 2. Sistema Etichette Unificato
- **Creazione rapida**: Box integrato in entrambe le view
- **Riutilizzo**: Dropdown con etichette esistenti del progetto
- **Gestione avanzata**: Link alla gestione etichette del progetto
- **AI Integration**: Suggerimenti automatici per nuove etichette

### 3. Comportamenti Standardizzati

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

## 📝 Piano di Implementazione

### Fase 1: Pulizia e Ristrutturazione Base
- [x] **1.1** Rinominare "Machine Learning" → "Etichettatura Umano/Macchina"
- [x] **1.2** Creare nuovo dashboard principale semplificato
- [ ] **1.3** Identificare e rimuovere view obsolete
- [x] **1.4** Aggiornare routing e navigazione
- [x] **1.5** Test: Navigazione e accesso alle view principali

### Fase 2: Sistema Etichette Unificato
- [ ] **2.1** Creare componente condiviso per gestione etichette
- [ ] **2.2** Implementare box di creazione/selezione etichette
- [ ] **2.3** Integrare con sistema etichette progetto esistente
- [ ] **2.4** Implementare autocomplete e suggerimenti
- [ ] **2.5** Test: Creazione, selezione e riutilizzo etichette

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

## 🔧 Miglioramenti Proposti Aggiuntivi

### 1. **Sistema di Template Etichette**
- Template predefiniti per tipi comuni (sentiment, categorie, ecc.)
- Possibilità di salvare set di etichette come template riutilizzabili
- Import/export template tra progetti

### 2. **Analytics e Insights**
- Dashboard con statistiche etichettatura
- Visualizzazione distribuzione etichette
- Tracking accuracy AI vs umano
- Report di qualità etichettatura

### 3. **Collaborazione**
- Assegnazione celle a diversi utenti
- Sistema di review e approvazione
- Commenti e discussioni su etichette controverse
- History delle modifiche

### 4. **Export e Integrazione**
- Export in formati standard (CSV, JSON, Excel)
- API per integrazione con sistemi esterni
- Webhook per notifiche cambiamenti
- Backup automatico dati etichettatura

### 5. **AI Avanzato**
- Apprendimento da correzioni umane
- Suggerimenti basati su pattern progetto
- Rilevamento anomalie nelle etichette
- Confidence scoring dinamico

## 📊 Metriche di Successo

### Funzionalità
- ✅ Solo 2 view principali funzionanti
- ✅ Sistema etichette unificato
- ✅ Etichettatura multipla supportata
- ✅ AI integration fluida

### UX
- ✅ Riduzione del 70% click per completare task
- ✅ Eliminazione confusione navigazione
- ✅ Feedback utente positivo
- ✅ Curva apprendimento ridotta

### Performance
- ✅ Caricamento view < 2 secondi
- ✅ Risposta AI < 3 secondi
- ✅ Salvataggio etichette < 1 secondo
- ✅ Zero errori backend

## 🚀 Prossimi Passi

1. **Revisione Piano**: Confermare approccio e priorità
2. **Setup Branch**: Creare branch dedicato per la ristrutturazione
3. **Backup**: Creare backup completo stato attuale
4. **Implementazione**: Seguire fasi in ordine sequenziale
5. **Testing**: Test continuo durante implementazione

---

**Note**: Questo piano è progettato per essere implementato in modo incrementale, permettendo rollback in caso di problemi e testing continuo delle funzionalità.

## ✅ AGGIORNAMENTO STATO PROGETTO

### Fix Critici Applicati (29/06/2025)

#### 1. Problema Database - Campo column_name troppo corto
- **Problema**: `StringDataRightTruncation` - nomi di colonne lunghi (>255 char) causavano errori
- **Soluzione**: Migrazione database per aumentare `column_name` da 255 a 1000 caratteri
- **File modificati**: 
  - `migrations/versions/1b3e32d81e77_increase_column_name_field_length_to_.py`
  - `app/models.py` (AutoLabel, AutoLabelApplication)
  - `app/models_labeling.py` (LabelGeneration, LabelApplication)
- **Status**: ✅ Risolto e testato

#### 2. Problema Etichettatura AI Batch - Etichette non salvate  
- **Problema**: La funzione `batch_ai_label` generava etichette ma non le salvava nel database
- **Soluzione**: Implementato salvataggio automatico delle etichette AI nel database
- **Funzionalità aggiunte**:
  - Creazione/riutilizzo AutoLabel per ogni etichetta generata
  - Salvataggio AutoLabelApplication per ogni cella etichettata
  - Reporting del numero di etichette effettivamente salvate
- **File modificati**: `app/views/ml.py` (funzione `batch_ai_label`)
- **Status**: ✅ Implementato, da testare

#### 3. Problema Routing - Conflitto blueprint labeling
- **Problema**: Import da `app.views.labeling` causava conflitti di routing
- **Soluzione**: Rimosso import problematico e sostituito con placeholder per Fase 2
- **File modificati**: `app/views/ml.py` (rimosso import da labeling.py)
- **Status**: ✅ Risolto temporaneamente

### Test Creati
- `test_routing_fix.py` - Verifica routing corretto
- `test_ai_batch_fix.py` - Test etichettatura AI batch
- `test_fase_1.py` - Test login e accesso dashboard
