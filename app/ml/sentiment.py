"""
Sentiment Analysis module for automatic emotion and sentiment detection
"""

import re
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analizzatore di sentiment per testi in italiano e inglese"""
    
    def __init__(self):
        # Dizionari di parole positive e negative
        self.positive_words_it = {
            'ottimo', 'eccellente', 'fantastico', 'meraviglioso', 'perfetto', 'splendido',
            'buono', 'bene', 'bello', 'bravo', 'contento', 'felice', 'soddisfatto',
            'piacevole', 'gradevole', 'interessante', 'utile', 'efficace', 'veloce',
            'facile', 'semplice', 'chiaro', 'preciso', 'accurato', 'professionale',
            'cortese', 'gentile', 'disponibile', 'competente', 'esperto', 'qualità',
            'consiglio', 'raccomando', 'apprezzo', 'ringrazio', 'grazie', 'complimenti'
        }
        
        self.negative_words_it = {
            'pessimo', 'terribile', 'orribile', 'disgustoso', 'inaccettabile', 'sbagliato',
            'cattivo', 'male', 'brutto', 'difficile', 'complicato', 'confuso',
            'lento', 'inefficace', 'inutile', 'problematico', 'difettoso', 'rotto',
            'deluso', 'insoddisfatto', 'arrabbiato', 'frustrato', 'annoiato', 'preoccupato',
            'scortese', 'maleducato', 'incompetente', 'inadeguato', 'insufficiente',
            'errore', 'problema', 'difetto', 'mancanza', 'critica', 'lamentela'
        }
        
        self.positive_words_en = {
            'excellent', 'fantastic', 'wonderful', 'perfect', 'amazing', 'great',
            'good', 'nice', 'beautiful', 'happy', 'satisfied', 'pleased', 'glad',
            'pleasant', 'enjoyable', 'interesting', 'useful', 'effective', 'fast',
            'easy', 'simple', 'clear', 'precise', 'accurate', 'professional',
            'polite', 'kind', 'helpful', 'competent', 'expert', 'quality',
            'recommend', 'appreciate', 'thank', 'thanks', 'compliments'
        }
        
        self.negative_words_en = {
            'terrible', 'horrible', 'awful', 'disgusting', 'unacceptable', 'wrong',
            'bad', 'ugly', 'difficult', 'complicated', 'confusing', 'slow',
            'ineffective', 'useless', 'problematic', 'defective', 'broken',
            'disappointed', 'unsatisfied', 'angry', 'frustrated', 'bored', 'worried',
            'rude', 'impolite', 'incompetent', 'inadequate', 'insufficient',
            'error', 'problem', 'defect', 'lack', 'criticism', 'complaint'
        }
        
        # Intensificatori
        self.intensifiers_it = {
            'molto': 1.5, 'estremamente': 2.0, 'incredibilmente': 2.0, 'davvero': 1.3,
            'veramente': 1.3, 'particolarmente': 1.4, 'abbastanza': 1.2, 'piuttosto': 1.2,
            'troppo': 1.8, 'super': 1.6, 'ultra': 1.8, 'iper': 1.8
        }
        
        self.intensifiers_en = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'really': 1.3,
            'truly': 1.3, 'particularly': 1.4, 'quite': 1.2, 'rather': 1.2,
            'too': 1.8, 'super': 1.6, 'ultra': 1.8, 'hyper': 1.8
        }
        
        # Negazioni
        self.negations_it = {'non', 'no', 'niente', 'nulla', 'mai', 'nemmeno', 'neanche'}
        self.negations_en = {'not', 'no', 'never', 'nothing', 'neither', 'nor', 'none'}
        
        # Emozioni specifiche
        self.emotions_it = {
            'gioia': ['felice', 'contento', 'gioioso', 'allegro', 'euforico', 'entusiasta'],
            'tristezza': ['triste', 'depresso', 'melanconico', 'abbattuto', 'sconsolato'],
            'rabbia': ['arrabbiato', 'furioso', 'irritato', 'infuriato', 'indignato'],
            'paura': ['spaventato', 'terrorizzato', 'preoccupato', 'ansioso', 'nervoso'],
            'sorpresa': ['sorpreso', 'stupito', 'meravigliato', 'scioccato'],
            'disgusto': ['disgustato', 'nauseato', 'schifato', 'ripugnato'],
            'fiducia': ['fiducioso', 'sicuro', 'tranquillo', 'sereno', 'rilassato'],
            'anticipazione': ['eccitato', 'impaziente', 'curioso', 'interessato']
        }
        
        self.emotions_en = {
            'joy': ['happy', 'joyful', 'cheerful', 'euphoric', 'enthusiastic', 'delighted'],
            'sadness': ['sad', 'depressed', 'melancholic', 'dejected', 'sorrowful'],
            'anger': ['angry', 'furious', 'irritated', 'enraged', 'indignant'],
            'fear': ['scared', 'terrified', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'amazed', 'astonished', 'shocked'],
            'disgust': ['disgusted', 'nauseated', 'revolted', 'repulsed'],
            'trust': ['confident', 'secure', 'calm', 'serene', 'relaxed'],
            'anticipation': ['excited', 'impatient', 'curious', 'interested']
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analizza il sentiment di un singolo testo"""
        if not text or not isinstance(text, str):
            return self._create_neutral_result("Testo vuoto o non valido")
        
        # Preprocessa il testo
        processed_text = self._preprocess_text(text)
        words = processed_text.split()
        
        if not words:
            return self._create_neutral_result("Nessuna parola valida trovata")
        
        # Rileva la lingua
        language = self._detect_language(words)
        
        # Calcola il sentiment
        sentiment_score = self._calculate_sentiment_score(words, language)
        
        # Determina la polarità
        sentiment_label = self._determine_sentiment_label(sentiment_score)
        
        # Rileva le emozioni
        emotions = self._detect_emotions(words, language)
        
        # Calcola l'intensità
        intensity = self._calculate_intensity(abs(sentiment_score))
        
        # Calcola la confidenza
        confidence = self._calculate_confidence(words, sentiment_score, language)
        
        return {
            'sentiment': sentiment_label,
            'score': round(sentiment_score, 3),
            'emotions': emotions,
            'intensity': intensity,
            'confidence': round(confidence, 3),
            'language': language,
            'word_count': len(words),
            'details': {
                'positive_words': self._find_sentiment_words(words, 'positive', language),
                'negative_words': self._find_sentiment_words(words, 'negative', language),
                'intensifiers': self._find_intensifiers(words, language),
                'negations': self._find_negations(words, language)
            }
        }
    
    def analyze_texts_batch(self, texts: List[str]) -> Dict[str, Any]:
        """Analizza il sentiment di una lista di testi"""
        if not texts:
            return {
                'overall_sentiment': 'neutral',
                'overall_score': 0.0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'common_emotions': [],
                'individual_results': []
            }
        
        individual_results = []
        scores = []
        sentiments = []
        all_emotions = []
        
        for text in texts:
            result = self.analyze_text(text)
            individual_results.append(result)
            scores.append(result['score'])
            sentiments.append(result['sentiment'])
            all_emotions.extend(result['emotions'])
        
        # Calcola statistiche aggregate
        overall_score = np.mean(scores) if scores else 0.0
        overall_sentiment = self._determine_sentiment_label(overall_score)
        
        # Distribuzione dei sentiment
        sentiment_counts = Counter(sentiments)
        total_texts = len(texts)
        sentiment_distribution = {
            'positive': sentiment_counts.get('positive', 0) / total_texts,
            'negative': sentiment_counts.get('negative', 0) / total_texts,
            'neutral': sentiment_counts.get('neutral', 0) / total_texts
        }
        
        # Emozioni più comuni
        emotion_counts = Counter(all_emotions)
        common_emotions = [emotion for emotion, count in emotion_counts.most_common(5)]
        
        return {
            'overall_sentiment': overall_sentiment,
            'overall_score': round(overall_score, 3),
            'sentiment_distribution': sentiment_distribution,
            'common_emotions': common_emotions,
            'individual_results': individual_results,
            'statistics': {
                'total_texts': total_texts,
                'avg_score': round(overall_score, 3),
                'score_std': round(np.std(scores), 3) if len(scores) > 1 else 0.0,
                'min_score': round(min(scores), 3) if scores else 0.0,
                'max_score': round(max(scores), 3) if scores else 0.0
            }
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessa il testo per l'analisi"""
        # Converti in minuscolo
        text = text.lower().strip()
        
        # Rimuovi caratteri speciali ma mantieni punteggiatura importante
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', ' ', text)
        
        # Rimuovi spazi multipli
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _detect_language(self, words: List[str]) -> str:
        """Rileva la lingua del testo (italiano o inglese)"""
        italian_indicators = 0
        english_indicators = 0
        
        # Parole comuni italiane
        italian_common = {'il', 'la', 'di', 'che', 'e', 'a', 'un', 'per', 'con', 'non', 'sono', 'molto'}
        # Parole comuni inglesi
        english_common = {'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was'}
        
        for word in words:
            if word in italian_common:
                italian_indicators += 1
            elif word in english_common:
                english_indicators += 1
            elif word in self.positive_words_it or word in self.negative_words_it:
                italian_indicators += 1
            elif word in self.positive_words_en or word in self.negative_words_en:
                english_indicators += 1
        
        return 'italian' if italian_indicators >= english_indicators else 'english'
    
    def _calculate_sentiment_score(self, words: List[str], language: str) -> float:
        """Calcola il punteggio di sentiment"""
        if language == 'italian':
            positive_words = self.positive_words_it
            negative_words = self.negative_words_it
            intensifiers = self.intensifiers_it
            negations = self.negations_it
        else:
            positive_words = self.positive_words_en
            negative_words = self.negative_words_en
            intensifiers = self.intensifiers_en
            negations = self.negations_en
        
        score = 0.0
        i = 0
        
        while i < len(words):
            word = words[i]
            
            # Controlla intensificatori
            intensifier = 1.0
            if i > 0 and words[i-1] in intensifiers:
                intensifier = intensifiers[words[i-1]]
            
            # Controlla negazioni
            negated = False
            if i > 0 and words[i-1] in negations:
                negated = True
            elif i > 1 and words[i-2] in negations:
                negated = True
            
            # Calcola il contributo della parola
            word_score = 0.0
            if word in positive_words:
                word_score = 1.0
            elif word in negative_words:
                word_score = -1.0
            
            # Applica modificatori
            if word_score != 0:
                word_score *= intensifier
                if negated:
                    word_score *= -1
                score += word_score
            
            i += 1
        
        # Normalizza il punteggio
        if len(words) > 0:
            score = score / len(words)
        
        # Limita il punteggio tra -1 e 1
        return max(-1.0, min(1.0, score))
    
    def _determine_sentiment_label(self, score: float) -> str:
        """Determina l'etichetta di sentiment basata sul punteggio"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_emotions(self, words: List[str], language: str) -> List[str]:
        """Rileva le emozioni specifiche nel testo"""
        emotions = self.emotions_it if language == 'italian' else self.emotions_en
        detected_emotions = []
        
        for emotion, emotion_words in emotions.items():
            for word in words:
                if word in emotion_words:
                    if emotion not in detected_emotions:
                        detected_emotions.append(emotion)
                    break
        
        return detected_emotions
    
    def _calculate_intensity(self, abs_score: float) -> str:
        """Calcola l'intensità del sentiment"""
        if abs_score >= 0.7:
            return 'high'
        elif abs_score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self, words: List[str], score: float, language: str) -> float:
        """Calcola la confidenza dell'analisi"""
        if language == 'italian':
            sentiment_words = self.positive_words_it | self.negative_words_it
        else:
            sentiment_words = self.positive_words_en | self.negative_words_en
        
        # Conta le parole di sentiment trovate
        sentiment_word_count = sum(1 for word in words if word in sentiment_words)
        
        # Calcola la confidenza basata sulla presenza di parole di sentiment
        if len(words) == 0:
            return 0.0
        
        sentiment_ratio = sentiment_word_count / len(words)
        
        # Combina con l'intensità del punteggio
        score_confidence = min(abs(score) * 2, 1.0)
        
        # Confidenza finale
        confidence = (sentiment_ratio + score_confidence) / 2
        
        return min(confidence, 1.0)
    
    def _find_sentiment_words(self, words: List[str], sentiment_type: str, language: str) -> List[str]:
        """Trova le parole di sentiment nel testo"""
        if language == 'italian':
            if sentiment_type == 'positive':
                sentiment_words = self.positive_words_it
            else:
                sentiment_words = self.negative_words_it
        else:
            if sentiment_type == 'positive':
                sentiment_words = self.positive_words_en
            else:
                sentiment_words = self.negative_words_en
        
        return [word for word in words if word in sentiment_words]
    
    def _find_intensifiers(self, words: List[str], language: str) -> List[str]:
        """Trova gli intensificatori nel testo"""
        intensifiers = self.intensifiers_it if language == 'italian' else self.intensifiers_en
        return [word for word in words if word in intensifiers]
    
    def _find_negations(self, words: List[str], language: str) -> List[str]:
        """Trova le negazioni nel testo"""
        negations = self.negations_it if language == 'italian' else self.negations_en
        return [word for word in words if word in negations]
    
    def _create_neutral_result(self, reason: str) -> Dict[str, Any]:
        """Crea un risultato neutro con messaggio di errore"""
        return {
            'sentiment': 'neutral',
            'score': 0.0,
            'emotions': [],
            'intensity': 'low',
            'confidence': 0.0,
            'language': 'unknown',
            'word_count': 0,
            'error': reason,
            'details': {
                'positive_words': [],
                'negative_words': [],
                'intensifiers': [],
                'negations': []
            }
        }