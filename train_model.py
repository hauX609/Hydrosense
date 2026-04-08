import json
import keras.backend as K
import xarray as xr
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers # type: ignore
import joblib
import os
import argparse 

print("TensorFlow Version:", tf.__version__)

# --- 1. Configuration ---

def load_config(config_path: str = 'config.json') -> dict:
    """Loads the configuration file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    print("Configuration loaded.")
    return config

# --- 2. Data Generator (Manages Large Data) ---

class SpatiotemporalDataGenerator(keras.utils.Sequence):
    """
    Keras Sequence to generate batches of spatiotemporal data for the model.
    It handles loading, scaling, and batching of large NetCDF data that
    doesn't fit into memory.
    """
    def __init__(self, ds: xr.Dataset, 
                 time_range: pd.DatetimeIndex, 
                 feature_vars: list, 
                 target_var: str, 
                 sequence_length: int, 
                 batch_size: int, 
                 scaler_dict: dict):
        
        self.ds = ds
        self.time_range = time_range
        self.feature_vars = feature_vars
        self.target_var = target_var
        self.seq_len = sequence_length
        self.batch_size = batch_size
        self.scalers = scaler_dict
        
        # Create a list of valid start indices for sequences
        self.indices = [i for i in range(len(self.time_range) - self.seq_len)]
        print(f"Generator created with {len(self.indices)} possible samples.")

    def __len__(self):
        """Returns the number of batches per epoch."""
        return int(np.floor(len(self.indices) / self.batch_size))

    def __getitem__(self, index):
        """Generates one batch of data."""
        # Get indices for the current batch
        batch_indices = self.indices[index*self.batch_size:(index+1)*self.batch_size]
        start_times = self.time_range[batch_indices]
        
        X_batch, y_batch = [], []
        
        for start_time in start_times:
            # Define time windows for features and target
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
            y_sample = y_sample.astype(np.float32)

            X_batch.append(X_sample)
            y_batch.append(y_sample)
            
        # Stack samples into a batch
        X = np.stack(X_batch)
        y = np.stack(y_batch)
        
        return X, y

# --- 3. Model Definition & Custom Metrics ---

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    """
    Dice coefficient, a better metric for segmentation tasks.
    Measures the overlap between predicted and true flood areas.
    """
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss function to address extreme class imbalance.
    It down-weights easy-to-classify examples (no flood) and focuses
    training on hard-to-classify examples (flood).
    """
    def focal_loss_fixed(y_true, y_pred):
        # Ensure predictions are clipped to avoid log(0) errors
        y_pred = K.clip(y_pred, K.epsilon(), 1.0 - K.epsilon())
        
        # Calculate cross-entropy
        cross_entropy = -y_true * K.log(y_pred)
        
        # Calculate focal loss components
        loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy
        
        # Return the mean of the focal loss
        return K.mean(loss)
    return focal_loss_fixed

def build_convlstm_model(input_shape: tuple):
    """
    Builds the ConvLSTM model.
    Architecture is slightly refined for better pattern recognition.
    """
    print(f"Building model with input shape: {input_shape}")
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        
        layers.ConvLSTM2D(
            filters=128, kernel_size=(5, 5), padding="same", 
            return_sequences=True, activation="relu"
        ),
        layers.BatchNormalization(),
        
        layers.ConvLSTM2D(
            filters=64, kernel_size=(3, 3), padding="same", 
            return_sequences=False, activation="relu"
        ),
        layers.BatchNormalization(),
        
        layers.Dropout(0.5),
        
        # Bottleneck convolution to refine features before final prediction
        layers.Conv2D(
            filters=32, kernel_size=(3,3), padding="same", activation="relu"
        ),
        
        # Final prediction layer
        layers.Conv2D(filters=1, kernel_size=(1, 1), activation="sigmoid")
    ])
    
    model.compile(
        # Use the new loss and metric, with higher weight on the positive class
        loss=focal_loss(alpha=0.75),
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        metrics=[dice_coefficient]
    )
    return model

# --- 4. Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Train the flood prediction model.")
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Start training from scratch, deleting any existing model and history.'
    )
    args = parser.parse_args()

    try:
        # --- Load Config and Data ---
        config = load_config('config.json')
        data_path = config['output_paths']['final_dataset']
        processed_path = config['data_paths']['processed']
        scaler_path = os.path.join(processed_path, 'data_scalers.joblib')
        model_output_path = os.path.join(processed_path, 'flood_convlstm_model.keras')
        history_path = os.path.join(processed_path, 'training_history.json')
        
        # --- Handle --reset flag ---
        if args.reset:
            print("--- RESET flag detected. Deleting old model and history... ---")
            if os.path.exists(model_output_path):
                os.remove(model_output_path)
            if os.path.exists(history_path):
                os.remove(history_path)
        
        print(f"Loading dataset from {data_path} (lazily)...")
        ds = xr.open_dataset(data_path, engine='h5netcdf', chunks={'time': 10})
        
        # This check is no longer needed as the preprocessing script handles it.
        # if 'index' in ds.dims:
        #     print("Renaming dimension 'index' to 'time'...")
        #     ds = ds.rename({'index': 'time'})
        
        print("Downsampling data to reduce memory footprint and speed up training...")
        # A coarsening factor of 2 reduces each dimension by 2, so 4x fewer pixels.
        ds = ds.coarsen(y=2, x=2, boundary='trim').mean()
        print(f"New downsampled shape: (y={len(ds.y)}, x={len(ds.x)})")
        # print("Loading downsampled data into memory...")
        # ds = ds.load() # Load after downsampling - REMOVED TO PREVENT OOM
        # print("Data loaded.")

        static_features = ['elevation', 'slope', 'land_cover']
        dynamic_features = ['precip', 'precip_lag_1d', 'precip_roll_7d', 'river_discharge']
        all_features = static_features + dynamic_features
        target_var = 'is_flooded'
        
        # --- Chronological Split ---
        train_end_date = '2022-12-31'
        val_start_date = '2023-01-01'
        val_end_date   = '2023-06-30'
        train_times = ds.time.sel(time=slice(None, train_end_date))
        val_times = ds.time.sel(time=slice(val_start_date, val_end_date))

        # --- Calculate and Save Scalers (only if they don't exist) ---
        if os.path.exists(scaler_path) and not args.reset:
            print("Loading existing scalers...")
            scaler_dict = joblib.load(scaler_path)
        else:
            print("Calculating new scalers from training data...")
            scaler_dict = {}
            for var in all_features:
                if 'time' in ds[var].dims:
                  data_to_scale = ds[var].sel(time=train_times)
                else:
                  data_to_scale = ds[var]
                print(f"  Calculating scaler for: {var}...")
                mean = float(data_to_scale.mean().compute()) # Use .compute() and cast to float
                std = float(data_to_scale.std().compute())
                if std < 1e-6:
                  print(f"  WARNING: Standard deviation for {var} is near zero. Setting std to 1.0.")
                  std = 1.0
                
                scaler_dict[var] = {'mean': mean, 'std': std}
            joblib.dump(scaler_dict, scaler_path)
            print(f"Scalers saved to {scaler_path}")

        # --- Setup Model Parameters ---
        SEQUENCE_LENGTH = 10
        BATCH_SIZE = 4
        TOTAL_EPOCHS = 10 # Increased epochs slightly
        
        grid_y, grid_x = ds.y.size, ds.x.size
        num_features = len(all_features)
        input_shape = (SEQUENCE_LENGTH, grid_y, grid_x, num_features)

        # --- Instantiate Generators ---
        print("Initializing data generators...")
        train_generator = SpatiotemporalDataGenerator(
            ds, train_times, all_features, target_var,
            SEQUENCE_LENGTH, BATCH_SIZE, scaler_dict
        )
        val_generator = SpatiotemporalDataGenerator(
            ds, val_times, all_features, target_var,
            SEQUENCE_LENGTH, BATCH_SIZE, scaler_dict
        )

        # --- Load or Build Model ---
        initial_epoch = 0
        old_history = {}
        if os.path.exists(model_output_path):
            print(f"Loading existing model from {model_output_path}...")
            # When loading a model with custom objects, they must be specified
            custom_objects = {'focal_loss_fixed': focal_loss(), 'dice_coefficient': dice_coefficient}
            model = keras.models.load_model(model_output_path, custom_objects=custom_objects)
            
            try:
                with open(history_path, 'r') as f:
                    old_history = json.load(f)
                initial_epoch = len(old_history.get('loss', []))
                print(f"Resuming training from Epoch {initial_epoch + 1}")
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                print("Could not load or parse history, starting epoch count from 0.")
                initial_epoch = 0
            
        else:
            print("No existing model found. Building new model...")
            model = build_convlstm_model(input_shape)
            
        model.summary()

        # --- Set up Callbacks ---
        # Save the model after every epoch
        checkpoint_callback = keras.callbacks.ModelCheckpoint(
            filepath=model_output_path,
            save_weights_only=False,
            save_best_only=False, # We save every epoch to allow resumption
            verbose=1
        )
        
        # Reduce learning rate when validation dice coefficient plateaus
        lr_scheduler = keras.callbacks.ReduceLROnPlateau(
            monitor='val_dice_coefficient',
            factor=0.2, # Reduce LR by a factor of 5
            patience=3, # Wait 3 epochs of no improvement
            verbose=1,
            mode='max', # We want to maximize the dice coefficient
            min_lr=1e-7
        )
        
        # Custom callback to save history JSON file after each epoch
        class HistoryLogger(keras.callbacks.Callback):
            def on_train_begin(self, logs=None):
                # Start with existing history if it exists
                self.history = {k: list(v) for k, v in old_history.items()}
            
            def on_epoch_end(self, epoch, logs=None):
                logs = logs or {}
                # Append new logs to history
                for key, value in logs.items():
                    # Ensure value is JSON serializable
                    self.history.setdefault(key, []).append(float(value))
                
                # Save the updated history
                with open(history_path, 'w') as f:
                    json.dump(self.history, f, indent=4)
                print(f" - History saved to {history_path}")

        print("\n--- Starting Model Training ---")
        
        # Train the model
        model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=TOTAL_EPOCHS,
            initial_epoch=initial_epoch,
            callbacks=[
                checkpoint_callback,
                lr_scheduler,
                HistoryLogger()
            ]
        )
        
        print("\n--- Training Complete ---")

    except Exception as e:
        print(f"\n--- Model Training FAILED ---")
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
