"""
Semantic Clustering for automatic text categorization
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from typing import Dict, List, Any, Tuple, Optional
import re
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class SemanticClustering:
    """Clustering semantico per categorizzare automaticamente le risposte testuali"""
    
    def __init__(self, min_cluster_size: int = 3, max_clusters: int = 10):
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.vectorizer = None
        self.cluster_model = None
        self.cluster_labels = None
        self.cluster_centers = None
        
    def analyze_and_cluster(self, texts: List[str], method: str = 'kmeans') -> Dict[str, Any]:
        """Analizza e raggruppa i testi in cluster semantici"""
        
        if not texts or len(texts) < self.min_cluster_size:
            return self._create_empty_result("Troppo pochi testi per il clustering")
        
        # Preprocessa i testi
        processed_texts = self._preprocess_texts(texts)
        
        if not processed_texts:
            return self._create_empty_result("Nessun testo valido dopo il preprocessing")
        
        # Crea rappresentazioni vettoriali
        vectors = self._create_text_vectors(processed_texts)
        
        if vectors is None:
            return self._create_empty_result("Impossibile creare vettori di testo")
        
        # Determina il numero ottimale di cluster
        optimal_clusters = self._determine_optimal_clusters(vectors, processed_texts)
        
        # Esegui clustering
        if method == 'kmeans':
            cluster_labels = self._kmeans_clustering(vectors, optimal_clusters)
        else:  # dbscan
            cluster_labels = self._dbscan_clustering(vectors)
        
        # Analizza i cluster
        cluster_analysis = self._analyze_clusters(processed_texts, cluster_labels, vectors)
        
        # Genera etichette per i cluster
        cluster_labels_generated = self._generate_cluster_labels(cluster_analysis)
        
        return {
            'method': method,
            'num_clusters': len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0),
            'cluster_labels': cluster_labels.tolist(),
            'cluster_analysis': cluster_analysis,
            'generated_labels': cluster_labels_generated,
            'silhouette_score': self._calculate_silhouette_score(vectors, cluster_labels),
            'success': True
        }
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocessa i testi per il clustering"""
        processed = []
        
        for text in texts:
            if not text or not isinstance(text, str):
                continue
                
            # Converti in minuscolo
            text = text.lower().strip()
            
            # Rimuovi caratteri speciali ma mantieni punteggiatura importante
            text = re.sub(r'[^\w\s\.\!\?\,\;\:]', ' ', text)
            
            # Rimuovi spazi multipli
            text = re.sub(r'\s+', ' ', text)
            
            # Filtra testi troppo corti o troppo lunghi
            if 3 <= len(text) <= 1000:
                processed.append(text)
        
        return processed
    
    def _create_text_vectors(self, texts: List[str]) -> Optional[np.ndarray]:
        """Crea rappresentazioni vettoriali dei testi usando TF-IDF"""
        try:
            # Configura il vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=self._get_italian_stopwords(),
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            
            # Crea i vettori
            vectors = self.vectorizer.fit_transform(texts)
            
            return vectors.toarray()
            
        except Exception as e:
            logger.error(f"Errore nella creazione dei vettori: {str(e)}")
            return None
    
    def _get_italian_stopwords(self) -> List[str]:
        """Restituisce una lista di stopwords italiane"""
        return [
            'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una', 'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
            'e', 'o', 'ma', 'però', 'anche', 'ancora', 'già', 'sempre', 'mai', 'più', 'meno', 'molto', 'poco', 'tanto',
            'tutto', 'niente', 'nulla', 'qualcosa', 'qualcuno', 'nessuno', 'ogni', 'alcuni', 'molti', 'pochi',
            'che', 'chi', 'cui', 'dove', 'quando', 'come', 'perché', 'perche', 'se', 'mentre', 'durante', 'dopo', 'prima',
            'sono', 'è', 'sei', 'siamo', 'siete', 'era', 'ero', 'eri', 'eravamo', 'eravate', 'erano',
            'ho', 'hai', 'ha', 'abbiamo', 'avete', 'hanno', 'avevo', 'avevi', 'aveva', 'avevamo', 'avevate', 'avevano',
            'mi', 'ti', 'si', 'ci', 'vi', 'me', 'te', 'lui', 'lei', 'noi', 'voi', 'loro',
            'questo', 'questa', 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle'
        ]
    
    def _determine_optimal_clusters(self, vectors: np.ndarray, texts: List[str]) -> int:
        """Determina il numero ottimale di cluster"""
        n_samples = len(texts)
        
        # Limiti basati sulla dimensione del dataset
        min_clusters = 2
        max_clusters = min(self.max_clusters, n_samples // self.min_cluster_size)
        
        if max_clusters < min_clusters:
            return min_clusters
        
        # Usa il metodo dell'elbow per K-means
        inertias = []
        k_range = range(min_clusters, max_clusters + 1)
        
        for k in k_range:
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(vectors)
                inertias.append(kmeans.inertia_)
            except:
                break
        
        if len(inertias) < 2:
            return min_clusters
        
        # Trova il "gomito" nella curva
        optimal_k = self._find_elbow(inertias, k_range)
        
        return optimal_k
    
    def _find_elbow(self, inertias: List[float], k_range: range) -> int:
        """Trova il punto di gomito nella curva delle inerzie"""
        if len(inertias) < 3:
            return k_range[0]
        
        # Calcola le differenze seconde
        diffs = np.diff(inertias)
        second_diffs = np.diff(diffs)
        
        # Trova il punto con la maggiore variazione
        if len(second_diffs) > 0:
            elbow_idx = np.argmax(second_diffs) + 2  # +2 per compensare i diff
            return list(k_range)[min(elbow_idx, len(k_range) - 1)]
        
        return k_range[0]
    
    def _kmeans_clustering(self, vectors: np.ndarray, n_clusters: int) -> np.ndarray:
        """Esegue clustering K-means"""
        try:
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = self.cluster_model.fit_predict(vectors)
            self.cluster_centers = self.cluster_model.cluster_centers_
            return cluster_labels
        except Exception as e:
            logger.error(f"Errore nel clustering K-means: {str(e)}")
            return np.zeros(len(vectors), dtype=int)
    
    def _dbscan_clustering(self, vectors: np.ndarray) -> np.ndarray:
        """Esegue clustering DBSCAN"""
        try:
            # Calcola eps basato sulla distanza media
            distances = []
            for i in range(min(100, len(vectors))):
                for j in range(i + 1, min(100, len(vectors))):
                    dist = np.linalg.norm(vectors[i] - vectors[j])
                    distances.append(dist)
            
            eps = np.percentile(distances, 30) if distances else 0.5
            
            self.cluster_model = DBSCAN(eps=eps, min_samples=self.min_cluster_size)
            cluster_labels = self.cluster_model.fit_predict(vectors)
            
            return cluster_labels
        except Exception as e:
            logger.error(f"Errore nel clustering DBSCAN: {str(e)}")
            return np.zeros(len(vectors), dtype=int)
    
    def _analyze_clusters(self, texts: List[str], cluster_labels: np.ndarray, vectors: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """Analizza i cluster generati"""
        cluster_analysis = {}
        
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise cluster in DBSCAN
                continue
                
            # Trova i testi in questo cluster
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_texts = [texts[i] for i in cluster_indices]
            cluster_vectors = vectors[cluster_indices]
            
            # Analizza il cluster
            analysis = {
                'size': len(cluster_texts),
                'texts': cluster_texts,
                'representative_texts': self._find_representative_texts(cluster_texts, cluster_vectors),
                'keywords': self._extract_cluster_keywords(cluster_texts, cluster_id),
                'avg_length': np.mean([len(text) for text in cluster_texts]),
                'coherence_score': self._calculate_cluster_coherence(cluster_vectors)
            }
            
            cluster_analysis[cluster_id] = analysis
        
        return cluster_analysis
    
    def _find_representative_texts(self, cluster_texts: List[str], cluster_vectors: np.ndarray, max_representatives: int = 3) -> List[str]:
        """Trova i testi più rappresentativi del cluster"""
        if len(cluster_texts) <= max_representatives:
            return cluster_texts
        
        # Calcola il centroide del cluster
        centroid = np.mean(cluster_vectors, axis=0)
        
        # Calcola le distanze dal centroide
        distances = []
        for i, vector in enumerate(cluster_vectors):
            distance = np.linalg.norm(vector - centroid)
            distances.append((distance, i))
        
        # Ordina per distanza e prendi i più vicini
        distances.sort()
        representative_indices = [idx for _, idx in distances[:max_representatives]]
        
        return [cluster_texts[i] for i in representative_indices]
    
    def _extract_cluster_keywords(self, cluster_texts: List[str], cluster_id: int, max_keywords: int = 10) -> List[str]:
        """Estrae le parole chiave più significative del cluster"""
        if not self.vectorizer:
            return []
        
        try:
            # Crea un documento unico per il cluster
            cluster_document = ' '.join(cluster_texts)
            
            # Ottieni i pesi TF-IDF
            cluster_vector = self.vectorizer.transform([cluster_document])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Trova le parole con peso maggiore
            tfidf_scores = cluster_vector.toarray()[0]
            word_scores = list(zip(feature_names, tfidf_scores))
            word_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filtra e restituisci le migliori parole
            keywords = []
            for word, score in word_scores[:max_keywords * 2]:
                if score > 0 and len(word) > 2:
                    keywords.append(word)
                    if len(keywords) >= max_keywords:
                        break
            
            return keywords
            
        except Exception as e:
            logger.error(f"Errore nell'estrazione delle keywords: {str(e)}")
            return []
    
    def _calculate_cluster_coherence(self, cluster_vectors: np.ndarray) -> float:
        """Calcola la coerenza interna del cluster"""
        if len(cluster_vectors) < 2:
            return 1.0
        
        # Calcola la similarità coseno media tra tutti i vettori del cluster
        similarities = []
        for i in range(len(cluster_vectors)):
            for j in range(i + 1, len(cluster_vectors)):
                sim = cosine_similarity([cluster_vectors[i]], [cluster_vectors[j]])[0][0]
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _generate_cluster_labels(self, cluster_analysis: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Genera etichette descrittive per i cluster"""
        generated_labels = {}
        
        for cluster_id, analysis in cluster_analysis.items():
            keywords = analysis['keywords'][:5]  # Prime 5 keywords
            representative_texts = analysis['representative_texts']
            
            # Genera nome del cluster basato sulle keywords
            if keywords:
                cluster_name = self._create_cluster_name(keywords)
            else:
                cluster_name = f"Cluster {cluster_id + 1}"
            
            # Genera descrizione
            description = self._create_cluster_description(keywords, analysis['size'])
            
            # Determina tema principale
            theme = self._determine_cluster_theme(keywords, representative_texts)
            
            generated_labels[cluster_id] = {
                'name': cluster_name,
                'description': description,
                'theme': theme,
                'keywords': keywords,
                'confidence': min(analysis['coherence_score'] * 1.2, 1.0),
                'size': analysis['size']
            }
        
        return generated_labels
    
    def _create_cluster_name(self, keywords: List[str]) -> str:
        """Crea un nome per il cluster basato sulle keywords"""
        if not keywords:
            return "Cluster Generico"
        
        # Prendi le prime 2-3 parole più significative
        main_keywords = keywords[:3]
        
        # Crea combinazioni sensate
        if len(main_keywords) >= 2:
            return f"{main_keywords[0].title()} e {main_keywords[1].title()}"
        else:
            return main_keywords[0].title()
    
    def _create_cluster_description(self, keywords: List[str], size: int) -> str:
        """Crea una descrizione per il cluster"""
        if not keywords:
            return f"Gruppo di {size} risposte simili"
        
        keyword_str = ", ".join(keywords[:5])
        return f"Gruppo di {size} risposte riguardanti: {keyword_str}"
    
    def _determine_cluster_theme(self, keywords: List[str], representative_texts: List[str]) -> str:
        """Determina il tema principale del cluster"""
        if not keywords:
            return "generico"
        
        # Temi comuni nei questionari
        themes = {
            'soddisfazione': ['soddisfatto', 'contento', 'felice', 'bene', 'buono', 'ottimo'],
            'problemi': ['problema', 'difficoltà', 'errore', 'sbagliato', 'male', 'cattivo'],
            'suggerimenti': ['suggerimento', 'consiglio', 'miglioramento', 'proposta', 'idea'],
            'qualità': ['qualità', 'servizio', 'prodotto', 'esperienza'],
            'tempo': ['tempo', 'veloce', 'lento', 'rapido', 'attesa'],
            'prezzo': ['prezzo', 'costo', 'economico', 'caro', 'conveniente']
        }
        
        # Conta le corrispondenze per ogni tema
        theme_scores = {}
        for theme, theme_words in themes.items():
            score = 0
            for keyword in keywords:
                if any(tw in keyword.lower() for tw in theme_words):
                    score += 1
            theme_scores[theme] = score
        
        # Restituisci il tema con il punteggio più alto
        if theme_scores and max(theme_scores.values()) > 0:
            return max(theme_scores, key=theme_scores.get)
        
        return "generico"
    
    def _calculate_silhouette_score(self, vectors: np.ndarray, cluster_labels: np.ndarray) -> float:
        """Calcola il silhouette score per valutare la qualità del clustering"""
        try:
            from sklearn.metrics import silhouette_score
            
            # Filtra i punti noise (-1) per DBSCAN
            valid_indices = cluster_labels != -1
            if np.sum(valid_indices) < 2:
                return 0.0
            
            valid_vectors = vectors[valid_indices]
            valid_labels = cluster_labels[valid_indices]
            
            # Calcola solo se ci sono almeno 2 cluster
            if len(set(valid_labels)) < 2:
                return 0.0
            
            return silhouette_score(valid_vectors, valid_labels)
            
        except Exception as e:
            logger.error(f"Errore nel calcolo del silhouette score: {str(e)}")
            return 0.0
    
    def _create_empty_result(self, reason: str) -> Dict[str, Any]:
        """Crea un risultato vuoto con messaggio di errore"""
        return {
            'method': 'none',
            'num_clusters': 0,
            'cluster_labels': [],
            'cluster_analysis': {},
            'generated_labels': {},
            'silhouette_score': 0.0,
            'success': False,
            'error': reason
        }