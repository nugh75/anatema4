#!/usr/bin/env python3

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def make_json_serializable(obj):
    """Convert pandas/numpy objects to JSON serializable types"""
    if pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, np.datetime64)):
        return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.ndarray, list)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    else:
        return obj

def test_serialization():
    """Test the JSON serialization function with various pandas/numpy types"""
    
    # Create test data with problematic types
    test_data = {
        'timestamp': pd.Timestamp('2024-11-26 12:52:50.618000'),
        'datetime64': np.datetime64('2024-11-26'),
        'int64': np.int64(42),
        'float64': np.float64(3.14),
        'bool_': np.bool_(True),
        'nan_value': np.nan,
        'none_value': None,
        'string': 'test string',
        'regular_int': 123,
        'regular_float': 4.56
    }
    
    print("Testing JSON serialization...")
    print("Original data types:")
    for key, value in test_data.items():
        print(f"  {key}: {type(value)} = {value}")
    
    print("\nAfter serialization:")
    serialized_data = {k: make_json_serializable(v) for k, v in test_data.items()}
    
    for key, value in serialized_data.items():
        print(f"  {key}: {type(value)} = {value}")
    
    # Test JSON serialization
    import json
    try:
        json_string = json.dumps(serialized_data)
        print(f"\nJSON serialization successful!")
        print(f"JSON length: {len(json_string)} characters")
        return True
    except Exception as e:
        print(f"\nJSON serialization failed: {e}")
        return False

if __name__ == "__main__":
    success = test_serialization()
    if success:
        print("\n✅ Test passed! JSON serialization works correctly.")
    else:
        print("\n❌ Test failed! JSON serialization has issues.")
        sys.exit(1)