#!/usr/bin/env python3
"""
Script to inspect the model file and understand its structure
"""

import joblib
import os

model_path = "ml_models/multi_output_model.pkl"

print(f"Inspecting model file: {model_path}")
print(f"File exists: {os.path.exists(model_path)}")

if os.path.exists(model_path):
    try:
        # Load the model
        loaded_obj = joblib.load(model_path)
        
        print(f"\nLoaded object type: {type(loaded_obj)}")
        print(f"Loaded object: {loaded_obj}")
        
        if isinstance(loaded_obj, dict):
            print(f"\nDictionary keys: {loaded_obj.keys()}")
            for key, value in loaded_obj.items():
                print(f"  {key}: {type(value)}")
                if hasattr(value, 'predict'):
                    print(f"    -> {key} has predict method!")
        
        elif hasattr(loaded_obj, 'predict'):
            print("\nObject has predict method!")
            print(f"Object attributes: {dir(loaded_obj)}")
        else:
            print(f"\nObject does not have predict method")
            print(f"Available methods: {[method for method in dir(loaded_obj) if not method.startswith('_')]}")
            
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Model file does not exist!")
