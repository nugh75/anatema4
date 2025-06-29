# Anat## 📋 STATO PROGETTO - REFACTORING IN CORSO

### 🚧 **Sistema di Etichettatura Umano/Macchina - In Ristrutturazione**

Il progetto è attualmente in fase di **refactoring maggiore** per semplificare e unificare il sistema di etichettatura.

#### 📖 **Documentazione Completa**
➡️ **[docs/MASTER_REFACTORING.md](docs/MASTER_REFACTORING.md)** - **LEGGI QUESTO PRIMO**
- 🎯 Piano completo di refactoring
- 📊 Stato attuale (Fase 1 - 83% completato)
- 🚀 Prossimi passi (Task 1.4 in preparazione)
- ✅ Problemi risolti e fix applicati

#### 📂 **Indice Documentazione**
➡️ **[docs/INDICE_DOCUMENTAZIONE.md](docs/INDICE_DOCUMENTAZIONE.md)** - Navigazione rapida a tutta la documentazione  
➡️ **[docs/README.md](docs/README.md)** - Indice documenti tecnici specifici

#### 🎯 **Progresso Attuale**
- **Fase 1**: Pulizia e Ristrutturazione Base (**83% completato** ✅)
- **Prossimo**: Task 1.4 - Rimozione view obsolete 
- **Target**: Sistema etichette unificato e UX semplificata

---

## 📁 Struttura Documentazione

```
docs/
├── MASTER_REFACTORING.md          # 📋 Documento principale (leggi questo primo)
├── INDICE_DOCUMENTAZIONE.md       # 🗂️ Navigazione rapida
├── README.md                      # 📖 Indice documenti tecnici
├── ANALISI_FRAMMENTAZIONE_ETICHETTE.md  # 🔍 Problema etichette frammentate
├── DATABASE_STRUCTURE.md          # 🗄️ Struttura completa DB
└── [altri file tecnici...]        # 🔧 Dettagli implementazione
```chettatura Dati

![Anatema Logo](app/static/images/logo.png)

Anatema è un sistema web avanzato per l'etichettatura e l'analisi di dati Excel, costruito con Flask e Material Design. Permette agli utenti di organizzare, etichettare e analizzare i propri dati in modo intuitivo e professionale.

## � STATO PROGETTO - REFACTORING IN CORSO

### 🚧 **Sistema di Etichettatura Umano/Macchina - In Ristrutturazione**

Il progetto è attualmente in fase di **refactoring maggiore** per semplificare e unificare il sistema di etichettatura.

#### 📖 **Documentazione Completa**
➡️ **[MASTER_REFACTORING.md](MASTER_REFACTORING.md)** - **LEGGI QUESTO PRIMO**
- 🎯 Piano completo di refactoring
- 📊 Stato attuale (Fase 1 - 83% completato)
- �🚀 Prossimi passi (Task 1.4 in preparazione)
- ✅ Problemi risolti e fix applicati

#### 📂 **Indice Documentazione**
➡️ **[INDICE_DOCUMENTAZIONE.md](INDICE_DOCUMENTAZIONE.md)** - Navigazione rapida a tutta la documentazione

#### 🎯 **Progresso Attuale**
- **Fase 1**: Pulizia e Ristrutturazione Base (**83% completato** ✅)
- **Prossimo**: Task 1.4 - Rimozione view obsolete 
- **Target**: Sistema etichette unificato e UX semplificata

---

## 🚀 Caratteristiche Principali

### 📊 Gestione Dati
- **Upload File Excel**: Supporto per file .xlsx, .xls e CSV
- **Elaborazione Automatica**: Parsing automatico dei fogli Excel con estrazione di righe e colonne
- **Visualizzazione Dati**: Interfaccia tabellare per esplorare i dati caricati
- **Gestione Multi-Sheet**: Supporto completo per file Excel con più fogli

### 🤖 Etichettatura Umano/Macchina (IN REFACTORING)
- **Sistema Unificato**: Etichettatura manuale e automatica in un unico flusso (🔄 In sviluppo)
- **View Semplificate**: Solo 2 view principali - Colonne e Righe (✅ Dashboard completato)
- **AI Integration**: Suggerimenti automatici e batch processing (✅ Fix applicati)
- **Etichette Multiple**: Supporto per più etichette per cella (🔄 Pianificato Fase 3-4)

#### Funzionalità AI Attuali
- **Analisi Automatica**: Rilevamento automatico di tipi di colonna e domande aperte
- **Clustering Semantico**: Raggruppamento intelligente di risposte simili
- **Analisi Sentiment**: Classificazione automatica del sentiment
- **Integrazione API**: Supporto per OpenRouter (Claude, GPT) e Ollama (modelli locali)

### 🏷️ Sistema di Etichettatura (LEGACY - IN MIGRAZIONE)
- **Etichette Personalizzate**: Crea etichette con colori e categorie personalizzate
- **Etichettatura Automatica**: Applica etichette generate da ML con un click
- **Etichettatura Manuale**: Applica etichette a celle specifiche
- **⚠️ Nota**: Sistema in migrazione verso architettura unificata (vedi MASTER_REFACTORING.md)

### 📁 Organizzazione Progetti
- **Progetti Strutturati**: Organizza i dati in progetti logici e separati
- **Controllo Accesso**: Progetti privati e pubblici con gestione della visibilità
- **Collaborazione**: Condivisione di progetti pubblici tra utenti
- **Statistiche Progetto**: Dashboard con metriche dettagliate per ogni progetto

### 🔍 Ricerca e Analisi
- **Ricerca Globale**: Trova rapidamente progetti, file e etichette
- **Filtri Avanzati**: Filtra i dati per tipo, data, stato e altri criteri
- **Dashboard Analytics**: Visualizzazione di statistiche e tendenze
- **Export Dati**: Esporta i dati etichettati per analisi esterne

### 🛡️ Sicurezza e Autenticazione
- **Autenticazione Sicura**: Sistema di login con hash delle password
- **JWT Support**: API REST con autenticazione JWT
- **Controllo Accessi**: Gestione granulare dei permessi utente
- **Sessioni Sicure**: Gestione sicura delle sessioni utente

### 🎨 Interfaccia Utente
- **Material Design**: Interfaccia moderna e responsive
- **Mobile-First**: Ottimizzata per dispositivi mobili e desktop
- **Tema Personalizzabile**: Colori e stili configurabili
- **Accessibilità**: Conforme agli standard di accessibilità web

## 🛠️ Tecnologie Utilizzate

### Backend
- **Flask 2.3.3**: Framework web Python
- **SQLAlchemy**: ORM per gestione database
- **PostgreSQL**: Database principale (SQLite per sviluppo)
- **Flask-Login**: Gestione autenticazione
- **Flask-JWT-Extended**: API authentication
- **Pandas**: Elaborazione dati Excel
- **OpenPyXL**: Lettura file Excel

### Machine Learning
- **Scikit-learn**: Algoritmi di clustering e analisi
- **NLTK**: Natural Language Processing
- **Transformers**: Modelli di linguaggio avanzati
- **PyTorch**: Backend per deep learning
- **Sentence-Transformers**: Embeddings semantici
- **OpenAI API**: Integrazione con GPT e Claude
- **Ollama**: Supporto per modelli locali

### Frontend
- **Materialize CSS**: Framework Material Design
- **JavaScript ES6+**: Logica frontend moderna
- **Material Icons**: Iconografia coerente
- **Responsive Design**: Supporto multi-dispositivo

### Infrastruttura
- **Redis**: Cache e sessioni (opzionale)
- **Celery**: Task asincroni (opzionale)
- **Gunicorn**: Server WSGI per produzione
- **Docker**: Containerizzazione (configurazione inclusa)

## 📋 Requisiti di Sistema

### Requisiti Minimi
- Python 3.8+
- 2GB RAM
- 1GB spazio disco
- Browser moderno (Chrome, Firefox, Safari, Edge)

### Requisiti Consigliati
- Python 3.10+
- 4GB RAM
- PostgreSQL 12+
- Redis 6+ (per performance ottimali)

## 🚀 Installazione Rapida

### 1. Clone del Repository
```bash
git clone https://github.com/your-username/anatema.git
cd anatema
```

### 2. Setup Automatico
```bash
python setup.py
```

Il script di setup automatico:
- Crea l'ambiente virtuale
- Installa le dipendenze
- Configura il database
- Crea utenti di esempio
- Genera dati demo

### 3. Avvio Applicazione
```bash
# Attiva l'ambiente virtuale
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# Avvia l'applicazione
python run.py
```

L'applicazione sarà disponibile su: http://localhost:5000

## 🔧 Installazione Manuale

### 1. Ambiente Virtuale
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione Database
```bash
# Inizializza migrazioni
flask db init

# Crea migrazione
flask db migrate -m "Initial migration"

# Applica migrazioni
flask db upgrade
```

### 4. Utente Amministratore
```bash
flask create-admin
```

## ⚙️ Configurazione

### Variabili d'Ambiente (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/anatema_db

# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=xlsx,xls,csv

# Machine Learning
OPENROUTER_API_KEY=your-openrouter-api-key
OLLAMA_API_URL=http://localhost:11434
ML_PROVIDER=openrouter
ML_MODEL=anthropic/claude-3-haiku
ML_TIMEOUT=30

# Redis (opzionale)
REDIS_URL=redis://localhost:6379/0
```

### Configurazione Database

#### SQLite (Sviluppo)
```env
DATABASE_URL=sqlite:///anatema.db
```

#### PostgreSQL (Produzione)
```env
DATABASE_URL=postgresql://anatema_user:password@localhost:5432/anatema_db
```

## 📖 Utilizzo

### 1. Primo Accesso
- Vai su http://localhost:5000
- Registra un nuovo account o usa le credenziali demo:
  - **Admin**: username=`admin`, password=`admin123`
  - **Demo**: username=`demo`, password=`demo123`

### 2. Creazione Progetto
1. Clicca su "Nuovo Progetto" nella dashboard
2. Inserisci nome e descrizione
3. Scegli la visibilità (privato/pubblico)
4. Seleziona un template (opzionale)

### 3. Upload File
1. Entra nel progetto creato
2. Clicca su "Carica File"
3. Seleziona un file Excel (.xlsx, .xls) o CSV
4. Attendi l'elaborazione automatica

### 4. Creazione Etichette
1. Vai nella sezione "Etichette" del progetto
2. Clicca su "Nuova Etichetta"
3. Configura nome, colore e categorie
4. Salva l'etichetta

### 5. Etichettatura Dati
1. Visualizza un file elaborato
2. Seleziona le celle da etichettare
3. Applica le etichette create
4. Monitora le statistiche di utilizzo

## 🔌 API REST

Anatema fornisce API REST complete per l'integrazione con sistemi esterni.

### Autenticazione
```bash
# Login
POST /api/login
{
  "username": "your_username",
  "password": "your_password"
}

# Risposta
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "user": {...}
}
```

### Progetti
```bash
# Lista progetti
GET /api/projects
Authorization: Bearer <jwt_token>

# Crea progetto
POST /api/projects
{
  "name": "Nome Progetto",
  "description": "Descrizione",
  "is_public": false
}

# Dettagli progetto
GET /api/projects/{project_id}
```

### File e Dati
```bash
# Dettagli file
GET /api/files/{file_id}

# Dati foglio Excel
GET /api/files/{file_id}/sheets/{sheet_id}/data?page=1&per_page=50
```

### Etichette
```bash
# Etichette progetto
GET /api/projects/{project_id}/labels

# Applica etichetta
POST /api/labels/{label_id}/apply
{
  "row_id": "row_uuid",
  "column_index": 0,
  "cell_value": "valore_cella"
}
```

## 🐳 Docker

### Build e Run
```bash
# Build immagine
docker build -t anatema .

# Run container
docker run -p 5000:5000 -e DATABASE_URL=sqlite:///anatema.db anatema
```

### Docker Compose
```bash
# Avvia tutti i servizi
docker-compose up -d

# Include PostgreSQL e Redis
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Test Unitari
```bash
# Esegui tutti i test
python -m pytest

# Test con copertura
python -m pytest --cov=app

# Test specifici
python -m pytest tests/test_models.py
```

### Test API
```bash
# Test API con curl
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

## 📊 Monitoraggio e Logging

### Logs
```bash
# Visualizza logs
tail -f logs/anatema.log

# Logs errori
tail -f logs/error.log
```

### Metriche
- Dashboard admin per statistiche sistema
- Monitoraggio utilizzo storage
- Performance query database
- Statistiche utenti attivi

## 🔒 Sicurezza

### Best Practices Implementate
- Hash sicuro delle password (bcrypt)
- Protezione CSRF
- Validazione input lato server
- Sanitizzazione dati
- Rate limiting API
- Sessioni sicure

### Configurazione Produzione
```env
# Usa sempre HTTPS in produzione
FLASK_ENV=production
SECRET_KEY=strong-random-secret-key
JWT_SECRET_KEY=strong-jwt-secret

# Database sicuro
DATABASE_URL=postgresql://secure_user:strong_password@db:5432/anatema_prod
```

## 🚀 Deploy in Produzione

### Server Linux (Ubuntu/Debian)
```bash
# Installa dipendenze sistema
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx

# Setup database
sudo -u postgres createuser anatema_user
sudo -u postgres createdb anatema_db -O anatema_user

# Deploy applicazione
git clone https://github.com/your-username/anatema.git
cd anatema
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configurazione
cp .env.example .env
# Modifica .env con configurazioni produzione

# Migrazioni
flask db upgrade

# Avvia con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/anatema/app/static;
    }
}
```

## 🤝 Contribuire

### Sviluppo
1. Fork del repository
2. Crea branch feature (`git checkout -b feature/amazing-feature`)
3. Commit modifiche (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Apri Pull Request

### Coding Standards
- Segui PEP 8 per Python
- Usa type hints dove possibile
- Scrivi test per nuove funzionalità
- Documenta API changes

### Bug Reports
Usa GitHub Issues per segnalare bug includendo:
- Versione Python e OS
- Steps per riprodurre
- Log errori
- Screenshots (se applicabile)

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.

## 👥 Team

- **Sviluppatore Principal**: [Il tuo nome]
- **Contributors**: Vedi [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 📞 Supporto

- **Documentazione**: [Wiki del progetto](https://github.com/your-username/anatema/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/anatema/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/your-username/anatema/discussions)
- **Email**: support@anatema.com

## 🗺️ Roadmap

### v2.0 (COMPLETATO! ✅)
- [x] **Machine Learning per auto-etichettatura** - Sistema completo implementato
- [x] **Clustering semantico** - Raggruppamento intelligente di risposte
- [x] **Analisi sentiment** - Classificazione automatica del sentiment
- [x] **Integrazione API ML** - Supporto OpenRouter e Ollama
- [ ] Export avanzato (PDF, Word)
- [ ] Collaborazione real-time
- [ ] API GraphQL

### v2.1 (Q3 2025)
- [ ] Modelli ML pre-addestrati per domini specifici
- [ ] Analisi temporale dei sentiment
- [ ] Clustering gerarchico avanzato
- [ ] Integrazione cloud storage
- [ ] Mobile app
- [ ] Plugin sistema

### v3.0 (Q4 2025)
- [ ] AI-powered insights avanzati
- [ ] GPT-4 Vision per analisi immagini
- [ ] Multi-tenant architecture
- [ ] Enterprise features
- [ ] Advanced security
- [ ] Suggerimenti automatici per miglioramenti questionari

---

**Anatema** - Organizza, etichetta e analizza i tuoi dati con facilità! 🚀