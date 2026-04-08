import json
import os
import argparse
import joblib
import numpy as np
import xarray as xr
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt

# --- Custom Objects from Training Script ---

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    """Dice coefficient for segmentation tasks."""
    y_true_f = tf.keras.backend.flatten(y_true)
    y_pred_f = tf.keras.backend.flatten(y_pred)
    intersection = tf.keras.backend.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.keras.backend.sum(y_true_f) + tf.keras.backend.sum(y_pred_f) + smooth)

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss function to address extreme class imbalance.
    It down-weights easy-to-classify examples (no flood) and focuses
    training on hard-to-classify examples (flood).
    """
    def focal_loss_fixed(y_true, y_pred):
        # Ensure predictions are clipped to avoid log(0) errors
        y_pred = tf.keras.backend.clip(y_pred, tf.keras.backend.epsilon(), 1.0 - tf.keras.backend.epsilon())
        
        # Calculate cross-entropy
        cross_entropy = -y_true * tf.keras.backend.log(y_pred)
        
        # Calculate focal loss components
        loss = alpha * tf.keras.backend.pow(1 - y_pred, gamma) * cross_entropy
        
        # Return the mean of the focal loss
        return tf.keras.backend.mean(loss)
    return focal_loss_fixed

# --- Data Generator (Copied from train.py) ---

class SpatiotemporalDataGenerator(keras.utils.Sequence):
    """Keras Sequence for spatiotemporal data."""
    def __init__(self, ds: xr.Dataset, time_range: pd.DatetimeIndex, feature_vars: list, 
                 target_var: str, sequence_length: int, batch_size: int, scaler_dict: dict):
        self.ds = ds
        self.time_range = time_range
        self.feature_vars = feature_vars
        self.target_var = target_var
        self.seq_len = sequence_length
        self.batch_size = batch_size
        self.scalers = scaler_dict
        self.indices = [i for i in range(len(self.time_range) - self.seq_len)]
        print(f"Generator created with {len(self.indices)} samples.")

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, index):
        batch_indices = self.indices[index*self.batch_size:(index+1)*self.batch_size]
        start_times = self.time_range[batch_indices]
        
        X_batch, y_batch = [], []
        for start_time in start_times:
            end_time = start_time + pd.Timedelta(days=self.seq_len - 1)
            target_time = start_time + pd.Timedelta(days=self.seq_len)
            time_slice = slice(start_time, end_time)
            
            feature_stack = []
            for var in self.feature_vars:
                # Handle dynamic (time-series) vs. static features
                if 'time' in self.ds[var].dims:
                    # Load and scale dynamic data
                    chunk = self.ds[var].sel(time=time_slice).to_numpy()
                    scaled_data = (chunk - self.scalers[var]['mean']) / self.scalers[var]['std']
                else:
                    # Load, scale, and broadcast static data
                    chunk = self.ds[var].to_numpy()
                    scaled_static = (chunk - self.scalers[var]['mean']) / self.scalers[var]['std']
                    # Tile the static data to match the sequence length
                    scaled_data = np.tile(scaled_static, (self.seq_len, 1, 1))

                # Clean and clip data, then add to the feature stack
                scaled_data = np.nan_to_num(scaled_data, nan=0.0, posinf=5.0, neginf=-5.0)
                scaled_data = np.clip(scaled_data, -5.0, 5.0)
                feature_stack.append(scaled_data[..., np.newaxis])
            
            # Combine all features into a single sample array
            X_sample = np.concatenate(feature_stack, axis=-1)
            
            # Load and clean the target variable (flood mask)
            y_sample_raw = self.ds[self.target_var].sel(time=target_time).to_numpy()
            y_sample_clean = np.nan_to_num(y_sample_raw, nan=0.0)
            y_sample = y_sample_clean[..., np.newaxis]
            
            X_batch.append(X_sample)
            y_batch.append(y_sample.astype(np.float32))
            
        return np.stack(X_batch), np.stack(y_batch)

# --- Main Evaluation Logic ---

def main():
    """Main function to run the evaluation."""
    print("--- Starting Model Evaluation ---")
    
    # 1. Load configuration and define paths
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    processed_path = config['data_paths']['processed']
    model_path = os.path.join(processed_path, 'flood_convlstm_model.keras')
    data_path = config['output_paths']['final_dataset']
    scaler_path = os.path.join(processed_path, 'data_scalers.joblib')
    
    # 2. Load the trained model
    print(f"Loading model from {model_path}...")
    custom_objects = {'focal_loss_fixed': focal_loss(), 'dice_coefficient': dice_coefficient}
    model = keras.models.load_model(model_path, custom_objects=custom_objects)
    
    # 3. Load and prepare the test data
    print(f"Loading and preparing test data from {data_path}...")
    ds = xr.open_dataset(data_path, engine='h5netcdf')
    
    # Ensure the same downsampling is applied as in training
    ds = ds.coarsen(y=2, x=2, boundary='trim').mean().load()
    print("Data loaded and downsampled.")
    
    # Load scalers
    print(f"Loading scalers from {scaler_path}...")
    scaler_dict = joblib.load(scaler_path)
    
    # 4. Generate predictions on the test set
    # This will be implemented in the next step
    
    # 4. Generate predictions on the test set
    print("Setting up test data generator...")
    test_start_date = '2023-07-01'
    test_end_date = '2023-12-31'
    test_times = ds.time.sel(time=slice(test_start_date, test_end_date))
    
    static_features = ['elevation', 'slope', 'land_cover']
    dynamic_features = ['precip', 'precip_lag_1d', 'precip_roll_7d', 'river_discharge']
    all_features = static_features + dynamic_features
    target_var = 'is_flooded'
    
    SEQUENCE_LENGTH = 10 # Should match training
    BATCH_SIZE = 4      # Can be the same or different from training
    
    test_generator = SpatiotemporalDataGenerator(
        ds, test_times, all_features, target_var,
        SEQUENCE_LENGTH, BATCH_SIZE, scaler_dict
    )
    
    print("Generating predictions...")
    predictions = model.predict(test_generator)
    
    # 5. Calculate and print performance metrics
    print("\n--- Overall Performance on Test Set ---")
    
    # We need to get the ground truth from the generator
    y_true = np.concatenate([test_generator[i][1] for i in range(len(test_generator))])
    
    # Ensure predictions and y_true are aligned in shape
    y_true = y_true[:len(predictions)]
    
    # Calculate metrics
    dice = dice_coefficient(y_true.astype(np.float32), predictions)
    precision = tf.keras.metrics.Precision()(y_true, predictions)
    recall = tf.keras.metrics.Recall()(y_true, predictions)
    
    print(f"Dice Coefficient: {dice.numpy():.4f}")
    print(f"Precision: {precision.numpy():.4f}")
    print(f"Recall: {recall.numpy():.4f}")
    
    # 6. Generate and save visualizations
    print("\nGenerating visualizations for top flood events...")
    output_vis_path = os.path.join(processed_path, 'evaluation_visualizations')
    os.makedirs(output_vis_path, exist_ok=True)
    
    # Find the top 5 days with the most flooded pixels in the ground truth
    flood_pixel_counts = y_true.sum(axis=(1, 2, 3))
    top_k = 5
    top_k_indices = np.argsort(flood_pixel_counts)[-top_k:]
    
    for i, idx in enumerate(top_k_indices):
        true_mask = y_true[idx].squeeze()
        pred_mask = predictions[idx].squeeze()
        
        # Get the corresponding input data for context
        input_sequence = test_generator[idx // BATCH_SIZE][0][idx % BATCH_SIZE]
        
        # We'll visualize the precipitation from the last day of the input sequence
        precip_last_day = input_sequence[-1, :, :, 0] # Assuming precip is the first feature
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        axes[0].imshow(precip_last_day, cmap='viridis')
        axes[0].set_title(f'Input Precipitation (Day T-1)')
        axes[0].axis('off')
        
        axes[1].imshow(true_mask, cmap='Blues')
        axes[1].set_title('Ground Truth Flood')
        axes[1].axis('off')
        
        axes[2].imshow(pred_mask, cmap='Reds')
        axes[2].set_title('Predicted Flood')
        axes[2].axis('off')
        
        plt.suptitle(f"Flood Event Visualization #{i+1} (Day Index: {idx})")
        save_path = os.path.join(output_vis_path, f'comparison_event_{i+1}.png')
        plt.savefig(save_path)
        plt.close()
        print(f"Saved visualization to {save_path}")
    
    print("--- Evaluation Complete ---")

if __name__ == "__main__":
    main()
