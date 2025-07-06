# Task 3.1 - Semplificare interfaccia View Colonne

**Data avvio**: 7 luglio 2025  
**Stato**: 🔄 IN CORSO

## 🎯 Obiettivo
Semplificare l'interfaccia della view colonne rimuovendo elementi non necessari e preparando per l'integrazione del sistema etichettatura unificato.

## 📋 Analisi Stato Attuale

### 🔍 Problemi Identificati
1. **Interfaccia complessa**: Troppi controlli e sezioni
2. **Mancanza integrazione**: Sistema unificato non integrato
3. **Duplicazione controlli**: Controlli AI duplicati
4. **Layout confuso**: Troppi elementi in competizione per l'attenzione
5. **Mancanza coerenza**: Non usa i componenti unificati

### 📊 Struttura Attuale
```
advanced_column_view.html (1471 righe)
├── Header Controls (navigazione)
├── Column Selection (selezione colonna)
├── Progress Tracking (progresso)
├── Cell Labeling Interface (interfaccia principale)
├── Batch AI Controls (controlli AI legacy)
└── Modals (finestre modali)
```

## 🔧 Modifiche da Implementare

### 1. Pulizia Header
- ✅ Mantenere navigazione breadcrumb
- ✅ Semplificare titolo e descrizione
- ❌ Rimuovere controlli ridondanti

### 2. Semplificazione Selezione Colonna
- ✅ Mantenere dropdown selezione
- ✅ Semplificare info colonna
- ❌ Rimuovere statistiche superflue

### 3. Integrazione Sistema Unificato
- 🔄 Sostituire controlli AI legacy con sistema unificato
- 🔄 Integrare pannello etichettatura unificato
- 🔄 Collegare store etichette centralizzato

### 4. Ottimizzazione Layout
- 🔄 Ridurre sezioni da 4 a 2 principali
- 🔄 Focus su selezione colonna + etichettatura
- 🔄 Rimuovere elementi di distrazione

## 🎯 Risultato Atteso
- Interfaccia più pulita e focalizzata
- Meno cognitive load per l'utente
- Preparazione per integrazione sistema unificato
- Riduzione codice di ~20-30%

## 📝 Prossimi Step
1. Analizzare componenti da rimuovere
2. Implementare semplificazioni
3. Preparare per integrazione Task 3.3

**Tempo stimato**: 0.5 giorni  
**Dipendenze**: ✅ Fase 2 completata (sistema unificato pronto)
