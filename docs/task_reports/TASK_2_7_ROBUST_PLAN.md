# Task 2.7 - Piano Robusto per Completamento Store Etichette

**Data**: 6 luglio 2025  
**Stato**: IN CORSO - Problemi identificati e piano di risoluzione  
**Priorità**: CRITICA - Blocca Fase 3

## 🎯 PROBLEMI IDENTIFICATI

### 1. **Autenticazione API Non Funzionante**
- **Problema**: Errore 401 su tutte le chiamate API (POST /api/projects/.../labels)
- **Causa**: Sistema di autenticazione non configurato correttamente per le API
- **Impatto**: Impossibile creare, modificare, eliminare etichette

### 2. **JavaScript Store Non Collegato**
- **Problema**: I bottoni funzionano ma le chiamate API falliscono
- **Causa**: Manca il file label_store.js caricato correttamente
- **Impatto**: Interfaccia non funzionante

### 3. **Modal Valori Celle Incompleto**
- **Problema**: Modal aggiunto ma non testato
- **Causa**: Endpoint /cell-values non testato
- **Impatto**: Funzionalità di visualizzazione mancante

## 🔧 PIANO DI RISOLUZIONE - 4 FASI

### **FASE 1: FIX AUTENTICAZIONE API** (30 min)

#### 1.1 Analizzare Sistema Autenticazione
- [ ] Verificare come funziona l'autenticazione nelle altre API
- [ ] Identificare se serve session-based o token-based
- [ ] Controllare decoratori di autenticazione

#### 1.2 Implementare Autenticazione Labels API
- [ ] Aggiungere decoratore di autenticazione corretto
- [ ] Testare con curl/browser per verificare funzionamento
- [ ] Verificare che tutte le operazioni CRUD funzionino

#### 1.3 Fix Frontend per Autenticazione
- [ ] Aggiungere headers di autenticazione corretti
- [ ] Testare con browser developer tools
- [ ] Verificare che i cookie/session vengano passati

### **FASE 2: VALIDAZIONE CRUD COMPLETO** (45 min)

#### 2.1 Test Creazione Etichette
- [ ] Testare via API diretta (curl)
- [ ] Testare via frontend (browser)
- [ ] Verificare salvataggio in database PostgreSQL
- [ ] Controllare che i campi siano popolati correttamente

#### 2.2 Test Modifica Etichette
- [ ] Testare caricamento dati nel form di modifica
- [ ] Testare salvataggio modifiche
- [ ] Verificare aggiornamento in tempo reale nell'interfaccia

#### 2.3 Test Eliminazione Etichette
- [ ] Testare controlli di sicurezza (etichette in uso)
- [ ] Testare eliminazione effettiva
- [ ] Verificare rimozione dal database

### **FASE 3: IMPLEMENTAZIONE VISUALIZZAZIONE CELLE** (30 min)

#### 3.1 Test Endpoint Cell Values
- [ ] Testare /api/projects/{id}/labels/{id}/cell-values
- [ ] Verificare che restituisca dati corretti
- [ ] Testare paginazione

#### 3.2 Test Modal Visualizzazione
- [ ] Testare apertura modal
- [ ] Testare caricamento dati
- [ ] Testare paginazione nel modal

### **FASE 4: VALIDAZIONE FINALE E DOCUMENTAZIONE** (15 min)

#### 4.1 Test End-to-End
- [ ] Workflow completo: crea → modifica → visualizza celle → elimina
- [ ] Test su multiple etichette
- [ ] Test performance con molte celle

#### 4.2 Documentazione
- [ ] Aggiornare MASTER_REFACTORING.md
- [ ] Documentare API endpoints
- [ ] Creare report di completamento

## 🛠️ AZIONI IMMEDIATE

### 1. **PRIMA AZIONE**: Identificare Sistema Autenticazione
```bash
# Cercare come funziona l'autenticazione nelle API esistenti
grep -r "login_required\|api_key\|session" app/views/
```

### 2. **SECONDA AZIONE**: Test Database Connection
```bash
# Verificare che le etichette siano salvate correttamente
psql $DATABASE_URL -c "SELECT * FROM labels LIMIT 5;"
```

### 3. **TERZA AZIONE**: Debug Frontend
```javascript
// Aggiungere console.log per debug autenticazione
console.log('Making API call with headers:', headers);
```

## 📋 CHECKLIST COMPLETAMENTO

### Sistema Autenticazione
- [ ] API accetta chiamate autenticate
- [ ] Frontend invia credenziali corrette
- [ ] Errori di autenticazione gestiti correttamente

### CRUD Etichette
- [ ] ✅ CREATE: Crea nuova etichetta e salva in PostgreSQL
- [ ] ✅ READ: Visualizza lista etichette dal database
- [ ] ✅ UPDATE: Modifica etichetta esistente
- [ ] ✅ DELETE: Elimina etichetta (con controlli sicurezza)

### Visualizzazione Celle
- [ ] ✅ Endpoint /cell-values funzionante
- [ ] ✅ Modal caricamento dati
- [ ] ✅ Paginazione funzionante
- [ ] ✅ Gestione stati vuoti

### Validazione Finale
- [ ] ✅ Test su ambiente reale
- [ ] ✅ Performance accettabile
- [ ] ✅ Nessun errore in console
- [ ] ✅ Database PostgreSQL aggiornato correttamente

## 🎯 CRITERI DI SUCCESSO

1. **Funzionalità**: Tutte le operazioni CRUD funzionano senza errori
2. **Database**: Dati salvati correttamente in PostgreSQL
3. **UX**: Interfaccia responsive e feedback utente
4. **Stabilità**: Nessun errore 401/500 in produzione
5. **Performance**: Operazioni completate in <2 secondi

## 🚨 BLOCCHI NOTI

- **Autenticazione**: Principale blocco attuale
- **Session Management**: Possibile problema con cookie/session
- **CSRF**: Possibile problema con token CSRF

## 📊 TEMPO STIMATO

- **Fase 1**: 30 minuti
- **Fase 2**: 45 minuti  
- **Fase 3**: 30 minuti
- **Fase 4**: 15 minuti
- **TOTALE**: 2 ore

## 🔄 PROSSIMI PASSI

1. **SUBITO**: Analizzare sistema autenticazione esistente
2. **POI**: Implementare fix autenticazione
3. **INFINE**: Validare tutto il workflow

---

**Nota**: Questo piano è stato creato dopo aver identificato che il task originale non era completo e presentava problemi di autenticazione che impedivano il funzionamento delle API.
