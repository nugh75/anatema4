# Anatema - Machine Learning Features

## Panoramica

Anatema ora include funzionalità avanzate di Machine Learning per l'analisi automatica e l'etichettatura intelligente dei dati contenuti nei file Excel. Il sistema utilizza algoritmi di clustering semantico, analisi del sentiment e rilevamento automatico dei tipi di colonna per generare etichette significative.

## Funzionalità Implementate

### 1. Rilevamento Automatico Tipi di Colonna
- **Identificazione automatica** di diversi tipi di colonna:
  - Timestamp, Date, Time
  - Testo breve/lungo
  - Nomi e identificatori
  - **Domande aperte** (focus principale)
- **Analisi statistica** per determinare la variabilità del testo
- **Punteggio di confidenza** per ogni classificazione

### 2. Clustering Semantico
- **TF-IDF Vectorization** per l'analisi testuale
- **Algoritmi di clustering**:
  - K-means per cluster definiti
  - DBSCAN per cluster di densità variabile
- **Generazione automatica di etichette** basata sui cluster
- **Testi rappresentativi** per ogni cluster identificato

### 3. Analisi del Sentiment
- **Supporto multilingue** (Italiano/Inglese)
- **Dizionari di parole** positive e negative
- **Punteggi di sentiment** da -1.0 (negativo) a +1.0 (positivo)
- **Classificazione automatica** in Positivo/Neutro/Negativo

### 4. Integrazione API Esterne
- **OpenRouter** per modelli cloud (Claude, GPT, ecc.)
- **Ollama** per modelli locali (Llama, Mistral, ecc.)
- **Configurazione flessibile** di provider e modelli
- **Test di connessione** integrato

## Architettura del Sistema

### Moduli ML

```
app/ml/
├── __init__.py           # Esportazione componenti principali
├── analyzer.py           # Coordinatore principale
├── api_client.py         # Client per OpenRouter/Ollama
├── column_detector.py    # Rilevatore tipi di colonna
├── clustering.py         # Clustering semantico
└── sentiment.py          # Analizzatore sentiment
```

### Modelli Database

1. **MLConfiguration**: Configurazioni ML per progetto
2. **MLAnalysis**: Analisi complete di fogli Excel
3. **ColumnAnalysis**: Analisi dettagliata delle colonne
4. **AutoLabel**: Etichette generate automaticamente
5. **AutoLabelApplication**: Applicazioni delle etichette ai dati

### Viste e Template

- **Dashboard ML**: `/projects/{id}/ml/dashboard`
- **Configurazione**: `/projects/{id}/ml/configure`
- **Risultati Analisi**: `/ml/analysis/{id}/results`

## Utilizzo

### 1. Configurazione Iniziale

1. Accedi al progetto
2. Clicca su "Machine Learning" nelle azioni rapide
3. Configura le impostazioni ML:
   - Scegli provider (OpenRouter/Ollama)
   - Inserisci API key (se necessaria)
   - Seleziona modello
   - Imposta parametri di analisi

### 2. Avvio Analisi

1. Dalla dashboard ML, seleziona i fogli da analizzare
2. Clicca "Avvia Analisi"
3. Il sistema:
   - Rileva automaticamente i tipi di colonna
   - Identifica le domande aperte
   - Applica clustering semantico
   - Genera etichette con sentiment

### 3. Revisione Risultati

1. Visualizza i risultati dell'analisi
2. Esamina le etichette generate
3. Seleziona quelle da applicare
4. Applica le etichette ai dati

## Configurazioni Avanzate

### Parametri di Clustering
- **Campioni minimi per cluster**: Numero minimo di risposte per formare un cluster
- **Soglia domande aperte**: Confidenza minima per identificare domande aperte
- **Soglia variabilità testo**: Livello di diversità richiesto nel testo

### Impostazioni Analisi
- **Rilevamento automatico colonne**: Abilita/disabilita l'identificazione automatica
- **Analisi sentiment**: Abilita/disabilita l'analisi del sentiment
- **Valori unici minimi**: Numero minimo di valori unici per l'analisi
- **Lunghezza massima testo**: Limite di caratteri per l'analisi testuale

## API Endpoints

### Configurazione
- `GET /projects/{id}/ml/configure` - Form di configurazione
- `POST /projects/{id}/ml/configure` - Salva configurazione
- `POST /ml/test-connection` - Test connessione API

### Analisi
- `GET /projects/{id}/ml/dashboard` - Dashboard ML
- `POST /projects/{id}/ml/start-analysis` - Avvia analisi
- `GET /ml/analysis/{id}/results` - Visualizza risultati
- `POST /ml/analysis/{id}/apply-labels` - Applica etichette

### Esportazione
- `GET /ml/analysis/{id}/export` - Esporta risultati

## Dipendenze

### Python Packages
```
scikit-learn>=1.7.0      # Machine learning algorithms
nltk>=3.9.1              # Natural language processing
transformers>=4.53.0     # Transformer models
torch>=2.7.1             # PyTorch backend
sentence-transformers    # Sentence embeddings
openai>=1.93.0          # OpenAI API client
requests>=2.32.4        # HTTP requests
```

### Installazione
```bash
pip install scikit-learn nltk transformers torch sentence-transformers openai requests
```

## Esempi di Utilizzo

### 1. Analisi Questionario Soddisfazione
```
Input: "Come valuti il servizio ricevuto?"
Risposte: ["Ottimo servizio", "Molto soddisfatto", "Potrebbe migliorare", ...]

Output:
- Cluster 1: "Feedback Positivo" (sentiment: +0.8)
- Cluster 2: "Aree di Miglioramento" (sentiment: -0.3)
- Cluster 3: "Suggerimenti Costruttivi" (sentiment: 0.1)
```

### 2. Analisi Feedback Prodotto
```
Input: "Cosa pensi del nuovo prodotto?"
Risposte: ["Innovativo e utile", "Prezzo troppo alto", "Design eccellente", ...]

Output:
- Cluster 1: "Apprezzamento Design" (sentiment: +0.7)
- Cluster 2: "Preoccupazioni Prezzo" (sentiment: -0.5)
- Cluster 3: "Innovazione Tecnologica" (sentiment: +0.6)
```

## Limitazioni e Considerazioni

### Performance
- **Campionamento automatico** per dataset grandi (>1000 righe)
- **Timeout configurabile** per API esterne
- **Cache dei risultati** per evitare rianalisi

### Precisione
- **Confidenza variabile** basata sulla qualità dei dati
- **Validazione manuale** raccomandata per risultati critici
- **Tuning parametri** necessario per domini specifici

### Privacy
- **Crittografia API keys** nel database
- **Nessun salvataggio** di dati sensibili su servizi esterni
- **Opzione locale** con Ollama per massima privacy

## Roadmap Future

### Versione 2.0
- [ ] Supporto per più lingue
- [ ] Modelli pre-addestrati per domini specifici
- [ ] Integrazione con GPT-4 Vision per analisi immagini
- [ ] Export automatico in formati standard (SPSS, R)

### Versione 2.1
- [ ] Analisi temporale dei sentiment
- [ ] Clustering gerarchico avanzato
- [ ] Suggerimenti automatici per miglioramenti questionari
- [ ] Dashboard analytics avanzata

## Supporto

Per problemi o domande sulle funzionalità ML:

1. Verifica la configurazione API
2. Controlla i log dell'applicazione
3. Testa la connessione dal pannello di configurazione
4. Consulta la documentazione dei provider ML utilizzati

## Contributi

Le funzionalità ML sono progettate per essere estensibili. Per aggiungere nuovi algoritmi o provider:

1. Implementa l'interfaccia base in `app/ml/`
2. Aggiungi i test appropriati
3. Aggiorna la documentazione
4. Invia una pull request

---

**Nota**: Questo sistema rappresenta un'implementazione completa di machine learning per l'analisi automatica di questionari e survey, progettato per essere sia potente che facile da usare.