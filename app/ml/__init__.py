"""
Machine Learning module for Anatema
Provides automatic analysis and labeling capabilities for Excel data
"""

from .analyzer import DataAnalyzer
from .column_detector import ColumnTypeDetector
from .clustering import SemanticClustering
from .sentiment import SentimentAnalyzer
from .api_client import MLAPIClient

__all__ = [
    'DataAnalyzer',
    'ColumnTypeDetector',
    'SemanticClustering',
    'SentimentAnalyzer',
    'MLAPIClient'
]