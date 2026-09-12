import os
import sys
import json
import h5py

model_path = r'C:\Users\aashi\OneDrive\Desktop\AI-Powered Retinal Disease classification System\best_model_latest.h5'

print("--- Inspecting best_model_latest.h5 metadata ---")
try:
    with h5py.File(model_path, 'r') as f:
        print("Keys in root:", list(f.keys()))
        if 'model_weights' in f:
            print("Contains model_weights")
        if 'optimizer_weights' in f:
            print("Contains optimizer_weights")
            
        print("\n--- Attributes ---")
        for key in f.attrs.keys():
            val = f.attrs[key]
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            if key == 'model_config':
                print(f"model_config is present")
            elif key == 'training_config':
                print(f"training_config is present")
                try:
                    tc = json.loads(val)
                    print(json.dumps(tc, indent=2))
                except:
                    print(val)
            else:
                print(f"{key}: {val}")
except Exception as e:
    print(f"Error inspecting hdf5: {e}")
