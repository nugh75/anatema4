"""
Column Type Detector for automatic data type recognition
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class ColumnTypeDetector:
    """Rileva automaticamente il tipo di dati nelle colonne Excel"""
    
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
            r'\d{1,2}\s+(gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)',  # Italian months
            r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # English months
        ]
        
        self.time_patterns = [
            r'\d{1,2}:\d{2}(:\d{2})?(\s*(AM|PM))?',  # HH:MM or HH:MM:SS with optional AM/PM
            r'\d{1,2}\.\d{2}(:\d{2})?',              # HH.MM format
        ]
        
        self.timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}',  # DD/MM/YYYY HH:MM
        ]
        
        self.name_indicators = [
            'nome', 'name', 'cognome', 'surname', 'firstname', 'lastname',
            'partecipante', 'participant', 'utente', 'user', 'persona', 'person'
        ]
        
        self.question_indicators = [
            'cosa', 'come', 'perché', 'perche', 'quando', 'dove', 'chi',
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'descrivi', 'describe', 'spiega', 'explain', 'racconta', 'tell',
            'opinione', 'opinion', 'pensiero', 'thought', 'commento', 'comment'
        ]
    
    def analyze_column(self, values: List[Any], column_name: str = "") -> Dict[str, Any]:
        """Analizza una colonna e determina il tipo di dati"""
        
        # Pulisci e prepara i dati
        clean_values = self._clean_values(values)
        
        if not clean_values:
            return self._create_result('unknown', 0.0, "Nessun valore valido trovato")
        
        # Statistiche di base
        stats = self._calculate_basic_stats(clean_values)
        
        # Analisi del nome della colonna
        column_hints = self._analyze_column_name(column_name)
        
        # Test per diversi tipi di dati
        type_scores = {}
        
        # Test timestamp
        type_scores['timestamp'] = self._test_timestamp(clean_values)
        
        # Test date
        type_scores['date'] = self._test_date(clean_values)
        
        # Test time
        type_scores['time'] = self._test_time(clean_values)
        
        # Test names
        type_scores['names'] = self._test_names(clean_values, column_hints)
        
        # Test short text vs long text
        short_score, long_score = self._test_text_length(clean_values, stats)
        type_scores['short_text'] = short_score
        type_scores['long_text'] = long_score
        
        # Test open questions
        type_scores['open_question'] = self._test_open_question(clean_values, column_name, stats)
        
        # Determina il tipo migliore
        best_type = max(type_scores, key=type_scores.get)
        confidence = type_scores[best_type]
        
        # Calcola variabilità del testo
        text_variability = self._calculate_text_variability(clean_values)
        
        # Determina complessità per domande aperte
        complexity = self._determine_complexity(clean_values, stats) if best_type == 'open_question' else None
        
        return {
            'detected_type': best_type,
            'confidence': confidence,
            'is_open_question': best_type == 'open_question',
            'complexity': complexity,
            'text_variability': text_variability,
            'unique_values_count': stats['unique_count'],
            'null_values_count': stats['null_count'],
            'avg_text_length': stats['avg_length'],
            'type_scores': type_scores,
            'reasoning': self._generate_reasoning(best_type, confidence, stats, column_hints)
        }
    
    def _clean_values(self, values: List[Any]) -> List[str]:
        """Pulisce e converte i valori in stringhe"""
        clean = []
        for val in values:
            if val is not None and not pd.isna(val):
                str_val = str(val).strip()
                if str_val and str_val.lower() not in ['nan', 'null', 'none', '']:
                    clean.append(str_val)
        return clean
    
    def _calculate_basic_stats(self, values: List[str]) -> Dict[str, Any]:
        """Calcola statistiche di base sui valori"""
        total_count = len(values)
        unique_values = list(set(values))
        unique_count = len(unique_values)
        
        lengths = [len(val) for val in values]
        avg_length = np.mean(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0
        min_length = min(lengths) if lengths else 0
        
        return {
            'total_count': total_count,
            'unique_count': unique_count,
            'null_count': 0,  # Già filtrati
            'avg_length': avg_length,
            'max_length': max_length,
            'min_length': min_length,
            'unique_ratio': unique_count / total_count if total_count > 0 else 0,
            'unique_values': unique_values[:10]  # Primi 10 per analisi
        }
    
    def _analyze_column_name(self, column_name: str) -> Dict[str, bool]:
        """Analizza il nome della colonna per indizi sul tipo"""
        name_lower = column_name.lower()
        
        return {
            'has_date_hint': any(word in name_lower for word in ['data', 'date', 'giorno', 'day']),
            'has_time_hint': any(word in name_lower for word in ['ora', 'time', 'orario', 'hour']),
            'has_name_hint': any(word in name_lower for word in self.name_indicators),
            'has_question_hint': any(word in name_lower for word in self.question_indicators),
            'has_timestamp_hint': any(word in name_lower for word in ['timestamp', 'created', 'updated'])
        }
    
    def _test_timestamp(self, values: List[str]) -> float:
        """Testa se i valori sono timestamp"""
        matches = 0
        for val in values[:20]:  # Test sui primi 20 valori
            for pattern in self.timestamp_patterns:
                if re.search(pattern, val, re.IGNORECASE):
                    matches += 1
                    break
            
            # Test anche con pandas
            try:
                pd.to_datetime(val)
                if ':' in val and ('-' in val or '/' in val):
                    matches += 1
            except:
                pass
        
        return min(matches / len(values[:20]), 1.0) if values else 0.0
    
    def _test_date(self, values: List[str]) -> float:
        """Testa se i valori sono date"""
        matches = 0
        for val in values[:20]:
            for pattern in self.date_patterns:
                if re.search(pattern, val, re.IGNORECASE):
                    matches += 1
                    break
            
            # Test con pandas
            try:
                parsed = pd.to_datetime(val)
                if ':' not in val:  # Esclude timestamp
                    matches += 1
            except:
                pass
        
        return min(matches / len(values[:20]), 1.0) if values else 0.0
    
    def _test_time(self, values: List[str]) -> float:
        """Testa se i valori sono orari"""
        matches = 0
        for val in values[:20]:
            for pattern in self.time_patterns:
                if re.search(pattern, val, re.IGNORECASE):
                    matches += 1
                    break
        
        return min(matches / len(values[:20]), 1.0) if values else 0.0
    
    def _test_names(self, values: List[str], column_hints: Dict[str, bool]) -> float:
        """Testa se i valori sono nomi di persone"""
        score = 0.0
        
        # Bonus dal nome della colonna
        if column_hints['has_name_hint']:
            score += 0.4
        
        # Analizza i valori
        name_patterns = 0
        for val in values[:20]:
            # Pattern tipici dei nomi
            if re.match(r'^[A-Za-z\s\'-]+$', val):  # Solo lettere, spazi, apostrofi
                if len(val.split()) <= 3:  # Massimo 3 parole
                    if val.istitle() or val.isupper():  # Iniziali maiuscole
                        name_patterns += 1
        
        pattern_score = min(name_patterns / len(values[:20]), 1.0) if values else 0.0
        score += pattern_score * 0.6
        
        return min(score, 1.0)
    
    def _test_text_length(self, values: List[str], stats: Dict[str, Any]) -> Tuple[float, float]:
        """Testa se è testo breve o lungo"""
        avg_length = stats['avg_length']
        max_length = stats['max_length']
        
        # Testo breve: lunghezza media < 50, max < 100
        short_score = 0.0
        if avg_length < 50:
            short_score += 0.5
        if max_length < 100:
            short_score += 0.3
        if stats['unique_ratio'] < 0.8:  # Molti valori ripetuti
            short_score += 0.2
        
        # Testo lungo: lunghezza media > 100, max > 200
        long_score = 0.0
        if avg_length > 100:
            long_score += 0.5
        if max_length > 200:
            long_score += 0.3
        if stats['unique_ratio'] > 0.9:  # Valori molto diversi
            long_score += 0.2
        
        return min(short_score, 1.0), min(long_score, 1.0)
    
    def _test_open_question(self, values: List[str], column_name: str, stats: Dict[str, Any]) -> float:
        """Testa se è una domanda aperta"""
        score = 0.0
        
        # Analizza il nome della colonna
        name_lower = column_name.lower()
        if any(indicator in name_lower for indicator in self.question_indicators):
            score += 0.3
        
        # Caratteristiche tipiche delle risposte a domande aperte
        if stats['avg_length'] > 50:  # Risposte tendenzialmente lunghe
            score += 0.2
        
        if stats['unique_ratio'] > 0.8:  # Alta variabilità
            score += 0.3
        
        # Analizza il contenuto per parole chiave
        question_words = 0
        descriptive_words = 0
        
        for val in values[:10]:
            val_lower = val.lower()
            
            # Parole che indicano risposte a domande
            if any(word in val_lower for word in ['perché', 'perche', 'because', 'since']):
                question_words += 1
            
            # Parole descrittive
            if any(word in val_lower for word in ['molto', 'poco', 'abbastanza', 'sempre', 'mai', 'spesso']):
                descriptive_words += 1
        
        if question_words > 0:
            score += 0.1
        if descriptive_words > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_text_variability(self, values: List[str]) -> float:
        """Calcola la variabilità del testo"""
        if not values:
            return 0.0
        
        # Calcola diversità lessicale
        all_words = []
        for val in values:
            words = re.findall(r'\b\w+\b', val.lower())
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        lexical_diversity = unique_words / total_words if total_words > 0 else 0
        
        # Calcola variabilità della lunghezza
        lengths = [len(val) for val in values]
        length_std = np.std(lengths) if len(lengths) > 1 else 0
        avg_length = np.mean(lengths) if lengths else 0
        length_variability = length_std / avg_length if avg_length > 0 else 0
        
        # Combina le metriche
        variability = (lexical_diversity + min(length_variability, 1.0)) / 2
        
        return min(variability, 1.0)
    
    def _determine_complexity(self, values: List[str], stats: Dict[str, Any]) -> str:
        """Determina la complessità delle risposte"""
        avg_length = stats['avg_length']
        
        if avg_length < 30:
            return 'simple'
        elif avg_length < 100:
            return 'medium'
        else:
            return 'complex'
    
    def _create_result(self, detected_type: str, confidence: float, reasoning: str) -> Dict[str, Any]:
        """Crea un risultato standardizzato"""
        return {
            'detected_type': detected_type,
            'confidence': confidence,
            'is_open_question': detected_type == 'open_question',
            'reasoning': reasoning
        }
    
    def _generate_reasoning(self, detected_type: str, confidence: float, stats: Dict[str, Any], column_hints: Dict[str, bool]) -> str:
        """Genera una spiegazione del ragionamento"""
        reasons = []
        
        if detected_type == 'timestamp':
            reasons.append("Rilevati pattern di data e ora combinati")
        elif detected_type == 'date':
            reasons.append("Rilevati pattern di date")
        elif detected_type == 'time':
            reasons.append("Rilevati pattern di orari")
        elif detected_type == 'names':
            reasons.append("Pattern tipici di nomi di persone")
            if column_hints['has_name_hint']:
                reasons.append("Nome colonna suggerisce nomi")
        elif detected_type == 'short_text':
            reasons.append(f"Testo breve (lunghezza media: {stats['avg_length']:.1f})")
        elif detected_type == 'long_text':
            reasons.append(f"Testo lungo (lunghezza media: {stats['avg_length']:.1f})")
        elif detected_type == 'open_question':
            reasons.append(f"Alta variabilità ({stats['unique_ratio']:.2f})")
            reasons.append(f"Lunghezza media {stats['avg_length']:.1f} caratteri")
        
        reasons.append(f"Confidenza: {confidence:.2f}")
        
        return "; ".join(reasons)