"""
API Client for Machine Learning services (OpenRouter and Ollama)
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MLAPIClient:
    """Client per comunicare con servizi di ML esterni"""
    
    def __init__(self, provider: str = None, api_key: str = None, api_url: str = None, model: str = None):
        self.provider = provider or current_app.config.get('ML_PROVIDER', 'openrouter')
        self.api_key = api_key or current_app.config.get('OPENROUTER_API_KEY')
        self.model = model or current_app.config.get('ML_MODEL', 'anthropic/claude-3-haiku')
        
        if self.provider == 'openrouter':
            self.api_url = api_url or current_app.config.get('OPENROUTER_API_URL', 'https://openrouter.ai/api/v1')
        else:  # ollama
            self.api_url = api_url or current_app.config.get('OLLAMA_API_URL', 'http://localhost:11434')
    
    def _make_request(self, endpoint: str, data: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Effettua una richiesta HTTP all'API"""
        try:
            if self.provider == 'openrouter':
                return self._make_openrouter_request(endpoint, data, timeout)
            else:
                return self._make_ollama_request(endpoint, data, timeout)
        except Exception as e:
            logger.error(f"Errore nella richiesta API: {str(e)}")
            raise
    
    def _make_openrouter_request(self, endpoint: str, data: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Richiesta a OpenRouter"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://anatema.app',
            'X-Title': 'Anatema Data Analysis'
        }
        
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        
        return response.json()
    
    def _make_ollama_request(self, endpoint: str, data: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Richiesta a Ollama"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Adatta il formato per Ollama
        if endpoint == 'chat/completions':
            ollama_data = {
                'model': self.model,
                'messages': data.get('messages', []),
                'stream': False
            }
        else:
            ollama_data = data
        
        response = requests.post(url, headers=headers, json=ollama_data, timeout=timeout)
        response.raise_for_status()
        
        return response.json()
    
    def analyze_text(self, prompt: str, analysis_type: str = 'general', return_json: bool = True) -> Dict[str, Any]:
        """Analizza un testo usando l'AI con prompt personalizzato o predefinito"""
        
        # Se il prompt è breve, assume che sia solo il testo da analizzare
        if len(prompt.split()) < 10 and analysis_type != 'general':
            if analysis_type == 'column_type':
                prompt = self._get_column_type_prompt(prompt)
            elif analysis_type == 'sentiment':
                prompt = self._get_sentiment_prompt(prompt)
            elif analysis_type == 'categorization':
                prompt = self._get_categorization_prompt(prompt)
            else:
                prompt = f"Analizza questo testo: {prompt}"
        
        # Determina il system message basato sul tipo di analisi
        if return_json:
            system_content = "Sei un esperto analista di dati specializzato nell'analisi di questionari e risposte testuali. Rispondi sempre in formato JSON valido."
        else:
            system_content = "Sei un esperto analista di dati specializzato nell'analisi di questionari e risposte testuali. Fornisci risposte chiare e concise."
        
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            if self.provider == 'openrouter':
                response = self._make_request('chat/completions', data)
                content = response['choices'][0]['message']['content']
            else:  # ollama
                response = self._make_request('api/chat', data)
                content = response['message']['content']
            
            if return_json:
                try:
                    return {
                        'success': True,
                        'analysis': json.loads(content),
                        'confidence': 0.85
                    }
                except json.JSONDecodeError:
                    # Se la risposta non è JSON valido, prova a estrarre il JSON
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return {
                            'success': True,
                            'analysis': json.loads(json_match.group()),
                            'confidence': 0.75
                        }
                    else:
                        return {
                            'success': True,
                            'analysis': content,
                            'confidence': 0.60,
                            'note': 'Risposta non in formato JSON'
                        }
            else:
                return {
                    'success': True,
                    'analysis': content,
                    'confidence': 0.85
                }
                
        except Exception as e:
            logger.error(f"Errore nell'analisi del testo: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def analyze_column_samples(self, samples: List[str], column_name: str) -> Dict[str, Any]:
        """Analizza campioni di una colonna per determinarne il tipo"""
        
        # Limita il numero di campioni per evitare prompt troppo lunghi
        limited_samples = samples[:20] if len(samples) > 20 else samples
        
        prompt = f"""
Analizza questi campioni dalla colonna "{column_name}" e determina il tipo di dati:

Campioni:
{chr(10).join([f"- {sample}" for sample in limited_samples if sample and str(sample).strip()])}

Determina:
1. Il tipo di dati (timestamp, date, time, short_text, long_text, names, open_question)
2. Se è una domanda aperta che richiede categorizzazione
3. La variabilità del contenuto
4. La complessità delle risposte

Rispondi in questo formato JSON:
{{
    "detected_type": "tipo_rilevato",
    "confidence": 0.95,
    "is_open_question": true/false,
    "complexity": "simple/medium/complex",
    "variability_score": 0.85,
    "reasoning": "spiegazione del ragionamento",
    "suggested_categories": ["categoria1", "categoria2"]
}}
"""
        
        return self.analyze_text(prompt, 'column_type')
    
    def generate_labels_for_texts(self, texts: List[str], context: str = "") -> Dict[str, Any]:
        """Genera etichette per un gruppo di testi"""
        
        # Limita il numero di testi
        limited_texts = texts[:15] if len(texts) > 15 else texts
        
        prompt = f"""
Analizza questi testi e genera etichette categoriche appropriate:

Contesto: {context}

Testi da analizzare:
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(limited_texts) if text and str(text).strip()])}

Genera:
1. Categorie tematiche principali
2. Etichette specifiche per ogni categoria
3. Analisi del sentiment generale
4. Emozioni prevalenti

Rispondi in questo formato JSON:
{{
    "main_themes": ["tema1", "tema2"],
    "categories": [
        {{
            "name": "nome_categoria",
            "description": "descrizione",
            "labels": ["etichetta1", "etichetta2"],
            "sample_texts": ["testo1", "testo2"]
        }}
    ],
    "sentiment_distribution": {{
        "positive": 0.4,
        "negative": 0.3,
        "neutral": 0.3
    }},
    "emotions": ["joy", "concern", "satisfaction"],
    "confidence": 0.85
}}
"""
        
        return self.analyze_text(prompt, 'categorization')
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analizza il sentiment di un testo"""
        
        prompt = f"""
Analizza il sentiment di questo testo:

"{text}"

Determina:
1. Sentiment generale (positive, negative, neutral)
2. Score numerico da -1 a 1
3. Emozioni specifiche presenti
4. Intensità emotiva

Rispondi in questo formato JSON:
{{
    "sentiment": "positive/negative/neutral",
    "score": 0.75,
    "emotions": ["joy", "satisfaction"],
    "intensity": "high/medium/low",
    "confidence": 0.90
}}
"""
        
        return self.analyze_text(prompt, 'sentiment')
    
    def _get_column_type_prompt(self, text: str) -> str:
        """Genera prompt per l'analisi del tipo di colonna"""
        return f"""
Analizza questo contenuto di colonna e determina il tipo di dati:

{text}

Tipi possibili:
- timestamp: date e orari completi
- date: solo date
- time: solo orari  
- short_text: testo breve (nomi, categorie)
- long_text: testo lungo (descrizioni, commenti)
- names: nomi di persone
- open_question: domande aperte che richiedono categorizzazione

Rispondi in formato JSON con tipo, confidenza e ragionamento.
"""
    
    def _get_sentiment_prompt(self, text: str) -> str:
        """Genera prompt per l'analisi del sentiment"""
        return f"""
Analizza il sentiment di questo testo:

{text}

Determina sentiment (positive/negative/neutral), score (-1 a 1), emozioni e intensità.
Rispondi in formato JSON.
"""
    
    def _get_categorization_prompt(self, text: str) -> str:
        """Genera prompt per la categorizzazione"""
        return f"""
Categorizza e genera etichette per questo contenuto:

{text}

Genera categorie tematiche, etichette specifiche e analisi del sentiment.
Rispondi in formato JSON.
"""
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa la connessione all'API"""
        try:
            test_prompt = "Rispondi con un JSON contenente solo: {\"status\": \"ok\", \"message\": \"Connessione riuscita\"}"
            
            messages = [
                {"role": "user", "content": test_prompt}
            ]
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 50
            }
            
            start_time = time.time()
            
            if self.provider == 'openrouter':
                response = self._make_request('chat/completions', data, timeout=10)
            else:
                response = self._make_request('api/chat', data, timeout=10)
            
            response_time = time.time() - start_time
            
            return {
                "status": "success",
                "provider": self.provider,
                "model": self.model,
                "response_time": response_time,
                "message": "Connessione riuscita"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "provider": self.provider,
                "model": self.model,
                "error": str(e),
                "message": "Connessione fallita"
            }