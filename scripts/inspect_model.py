import os
import sys
import json
# Use tf_keras explicitly to match the project's setup
import tf_keras as keras

model_path = r'C:\Users\aashi\OneDrive\Desktop\AI-Powered Retinal Disease classification System\best_model_latest.h5'

print("--- Inspecting best_model_latest.h5 ---")
try:
    model = keras.models.load_model(model_path, compile=False)
    print("Model loaded successfully.")
    
    print("\n--- Architecture ---")
    model.summary()
    
    print("\n--- Layers Details ---")
    for layer in model.layers:
        print(f"Name: {layer.name}, Type: {layer.__class__.__name__}, Trainable: {layer.trainable}")
        # Check if it's the backbone (Functional/Model)
        if isinstance(layer, keras.Model):
            print("  Backbone layers trainable status:")
            trainable_count = sum(1 for l in layer.layers if l.trainable)
            print(f"  {trainable_count}/{len(layer.layers)} layers trainable")
            
    print("\n--- Configuration Metadata ---")
    config = model.get_config()
    print("Input shape:", model.input_shape)
    print("Output shape:", model.output_shape)
    
except Exception as e:
    print(f"Error loading model: {e}")
