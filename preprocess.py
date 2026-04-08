# preprocess.py
#
# Main script for preprocessing and integrating all raw datasets for the
# AI-Based Disaster Response project (Bangladesh Focus).
#
# This script performs:
# 1. Loading of raw data (DEM, Land Cover, Precip, River, Flood Events).
# 2. Creation of a common reference grid (1km, UTM Zone 45N).
# 3. Reprojection and resampling of all raster data.
# 4. Feature engineering (Slope, Lagged Precipitation).
# 5. Rasterization of polygon flood event data to create a daily target.
# 6. Merging all features into a single xarray.Dataset and saving as NetCDF.

import json
import os
import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.enums import Resampling
from typing import Dict, Any

print("Starting data preprocessing pipeline...")

# --- Utility Functions ---

def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """Loads the configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create directories if they don't exist
        os.makedirs(config['data_paths']['processed'], exist_ok=True)
        os.makedirs(config['data_paths']['raw'], exist_ok=True)
        
        print("Configuration file loaded successfully.")
        return config
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at {config_path}")
        raise
    except json.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON from {config_path}")
        raise

def get_time_range(config: Dict[str, Any]) -> pd.DatetimeIndex:
    """Generates the target daily time range from config."""
    return pd.date_range(
        start=config['processing_params']['time_start'],
        end=config['processing_params']['time_end'],
        freq=config['processing_params']['time_freq']
    )

def save_as_netcdf(dataset: xr.Dataset, filepath: str):
    """Saves an xarray Dataset to a NetCDF file with error handling."""
    try:
        print(f"Saving dataset to {filepath}...")
        dataset.to_netcdf(filepath, engine='h5netcdf') # Using h5netcdf for performance
        print(f"Successfully saved to {filepath}")
    except Exception as e:
        print(f"ERROR: Failed to save NetCDF file to {filepath}. Error: {e}")
        raise

# --- Step 1: Create Reference Grid ---

def create_reference_grid(config: Dict[str, Any]) -> xr.DataArray:
    """
    Creates a reference grid based on the DEM, reprojected to the target
    CRS and resolution. This grid will be the template for all other data.
    """
    print("Step 1: Creating reference grid...")
    try:
        dem_path = config['data_paths']['dem']
        ref_grid_path = config['output_paths']['reference_grid']
        target_crs = config['processing_params']['target_crs']
        target_res = config['processing_params']['target_resolution']

        with rioxarray.open_rasterio(dem_path) as dem:
            # Reproject DEM to the target CRS and resolution
            ref_grid = dem.rio.reproject(
                dst_crs=target_crs,
                resolution=target_res,
                resampling=Resampling.bilinear
            )
            
            # Save the reference grid as a GeoTIFF for inspection
            ref_grid.rio.to_raster(ref_grid_path)
            
            print(f"Reference grid created and saved to {ref_grid_path}")
            print(f"Grid shape: {ref_grid.shape}")
            return ref_grid.squeeze() # Remove band dimension
            
    except FileNotFoundError:
        print(f"ERROR: DEM file not found at {dem_path}")
        raise
    except Exception as e:
        print(f"ERROR in create_reference_grid: {e}")
        raise

# --- Step 2: Process Static Features (DEM, Land Cover) ---

def process_static_features(config: Dict[str, Any], ref_grid: xr.DataArray) -> xr.Dataset:
    """
    Loads, reprojects, and processes static features (DEM, Slope, Land Cover).
    """
    print("Step 2: Processing static features (DEM, Land Cover)...")
    try:
        lc_path = config['data_paths']['land_cover']

        # 1. Add DEM (already in ref_grid format)
        dem = ref_grid.rename('elevation')
        
        # 2. Calculate Slope (requires 'xarray-spatial' or numpy)
        print("Calculating slope...")
        try:
            grad_y, grad_x = np.gradient(dem.values)
            slope_rad = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
            slope_deg = np.degrees(slope_rad)
            
            slope = xr.DataArray(
                data=slope_deg,
                coords=dem.coords,
                dims=dem.dims,
                name='slope',
                attrs={'units': 'degrees'}
            )
        except Exception as e:
            print(f"Warning: Could not calculate slope, filling with 0. Error: {e}")
            slope = xr.zeros_like(dem, name='slope')

        # 3. Process Land Cover
        print("Processing land cover...")
        with rioxarray.open_rasterio(lc_path) as lc:
            lc_reprojected = lc.rio.reproject_match(
                match_data_array=dem,
                resampling=Resampling.nearest # Use 'nearest' for categorical data
            )
        
        land_cover = lc_reprojected.squeeze().rename('land_cover')
        land_cover.attrs = lc.attrs
        land_cover.attrs['long_name'] = 'ESA WorldCover (resampled to 1km)'

        # 4. Combine into a single Dataset
        static_dataset = xr.merge([dem, slope, land_cover])
        
        save_as_netcdf(static_dataset, config['output_paths']['static_features'])
        return static_dataset

    except FileNotFoundError:
        print(f"ERROR: Land Cover file not found at {lc_path}")
        raise
    except Exception as e:
        print(f"ERROR in process_static_features: {e}")
        raise

# --- Step 3: Process Dynamic Features (Precip, River) ---

def process_dynamic_data(config: Dict[str, Any], ref_grid: xr.DataArray, time_range: pd.DatetimeIndex) -> xr.Dataset:
    """
    Loads, reprojects, and creates time-lag features for all dynamic data.
    ADAPTED to use IMERG.csv for precipitation.
    Includes FIX for 'time' KeyError in river data.
    """
    print("Step 3: Processing dynamic features...")
    
    # --- 3.1: Precipitation (from IMERG.csv) ---
    print("Processing precipitation (IMERG.csv)...")
    precip_path = config['data_paths']['precipitation']
    try:
        # Load the CSV
        df_precip = pd.read_csv(precip_path)
        
        # Rename columns, parse dates, and set index
        df_precip = df_precip.rename(columns={'cdate': 'time', 'mean_precip_mm': 'precip'})
        df_precip['time'] = pd.to_datetime(df_precip['time'])
        df_precip = df_precip.set_index('time')
        
        # Reindex to our master time range, filling missing days with 0
        df_precip = df_precip.reindex(time_range, fill_value=0)

        # --- Feature Engineering (Time-Series) ---
        print("Creating time-series features for precipitation...")
        
        # 1-day lag
        df_precip['precip_lag_1d'] = df_precip['precip'].shift(periods=1, fill_value=0)
        # 7-day rolling sum
        df_precip['precip_roll_7d'] = df_precip['precip'].rolling(window=7, min_periods=1).sum()

        # Convert this pandas DataFrame to an xarray Dataset
        ts_precip_ds = df_precip.to_xarray()
        
        # --- Broadcast time-series data to the 2D spatial grid ---
        print("Broadcasting time-series precipitation to spatial grid...")
        
        precip_ds_spatial = xr.Dataset()
        
        for var in ts_precip_ds.data_vars:
            time_series = ts_precip_ds[var]
            _, broadcasted_data = xr.broadcast(ref_grid, time_series)
            precip_ds_spatial[var] = broadcasted_data
            
        print("Precipitation processing complete.")
        
    except FileNotFoundError:
        print(f"ERROR: Precipitation file not found at {precip_path}")
        raise
    except Exception as e:
        print(f"ERROR processing precipitation: {e}")
        raise

    # --- 3.2: River Level ---
    print("Processing river levels (river_levels.nc)...")
    river_path = config['data_paths']['river_level']
    try:
        # Open river data
        with xr.open_dataset(river_path) as ds:
            
            # --- START NEW FIX for KeyError: 'time' ---
            print("Inspecting river_levels.nc coordinates:")
            print(ds.coords)
            
            # Find the time coordinate name automatically
            # It's usually the one with 'datetime' dtype
            time_dim_name = None
            for coord_name, coord in ds.coords.items():
                if np.issubdtype(coord.dtype, np.datetime64):
                    time_dim_name = str(coord_name) # Convert to string
                    break
            
            if time_dim_name:
                print(f"Found time dimension: '{time_dim_name}'. Renaming to 'time'.")
                ds = ds.rename({time_dim_name: 'time'})
            else:
                # Fallback if no datetime dtype is found
                print("Warning: Could not auto-detect datetime coordinate.")
                # Try to find a common GRIB/NetCDF name
                common_names = ['valid_time', 't', 'step', 'forecast_reference_time', 'date']
                found_name = None
                for name in common_names:
                    if name in ds.coords:
                        found_name = name
                        break
                
                if found_name:
                    print(f"Found potential time-like dim: '{found_name}'. Renaming to 'time'.")
                    ds = ds.rename({found_name: 'time'})
                else:
                    print("ERROR: Could not find a recognizable time coordinate.")
                    print("Please inspect the coordinates printed above and update the script.")
                    raise KeyError("Could not find time dimension in river_levels.nc")
            # --- END NEW FIX ---

            # Find data variable (e.g., 'dis24')
            var_name = 'dis' # Ideal name
            if var_name not in ds.data_vars:
                non_coord_vars = [v for v in ds.data_vars if v not in ds.coords]
                if not non_coord_vars:
                    raise ValueError("No valid data variables found in river_levels.nc")
                var_name = non_coord_vars[0]
                print(f"Warning: 'dis' variable not found, using first available: '{var_name}'")
            
            # Set spatial dims if not already set
            if 'latitude' in ds.coords and 'longitude' in ds.coords:
                ds = ds.rio.set_spatial_dims(x_dim='longitude', y_dim='latitude', inplace=True)
            ds = ds.rio.write_crs('EPSG:4326', inplace=True)
            
            river_level = ds[var_name]

            # Reproject to match reference grid
            print("Reprojecting river levels...")
            river_reprojected = river_level.rio.reproject_match(
                match_data_array=ref_grid,
                resampling=Resampling.bilinear
            )
            
            # Reindex to master time, fill NaNs
            # These lines should now work
            river_reprojected = river_reprojected.reindex(
                {'time': time_range}, method='nearest', tolerance='1D'
            )
            river_reprojected = river_reprojected.interpolate_na(dim='time', method='linear')
            river_reprojected = river_reprojected.fillna(0)
            
            river_ds = river_reprojected.rename('river_discharge')

    except FileNotFoundError:
        print(f"ERROR: River level file not found at {river_path}")
        raise
    except Exception as e:
        print(f"ERROR processing river data: {e}")
        raise

    # Combine all dynamic features
    dynamic_dataset = xr.merge([precip_ds_spatial, river_ds])
    save_as_netcdf(dynamic_dataset, config['output_paths']['dynamic_features'])
    return dynamic_dataset

# --- Step 4: Process Target Variable (Flood Events) ---

def process_flood_events(config: Dict[str, Any], ref_grid: xr.DataArray, time_range: pd.DatetimeIndex) -> xr.Dataset:
    """
    Loads flood event polygons and rasterizes them into a daily
    binary mask ('is_flooded') matching the reference grid.
    """
    print("Step 4: Processing target variable (Flood Events)...")
    events_path = config['data_paths']['flood_events']
    target_crs = config['processing_params']['target_crs']
    
    try:
        # 1. Load flood polygons
        gdf = gpd.read_file(events_path)
        
        # 2. Reproject to match reference grid
        gdf = gdf.to_crs(target_crs)
        
        # 3. Ensure date columns are datetime objects
        # *** Using 'BEGAN' and 'ENDED' from your snippet ***
        gdf['began'] = pd.to_datetime(gdf['BEGAN'])
        gdf['ended'] = pd.to_datetime(gdf['ENDED'])
        
        # 4. Get raster metadata from reference grid for rasterizing
        transform = ref_grid.rio.transform()
        out_shape = (ref_grid.y.size, ref_grid.x.size)
        
        # 5. Create empty 3D array to store daily flood masks
        flood_mask_3d = np.zeros(
            (len(time_range), out_shape[0], out_shape[1]), 
            dtype=np.uint8
        )
        
        print(f"Rasterizing flood polygons for {len(time_range)} days...")
        
        for _, event in gdf.iterrows():
            event_geom = [event.geometry] # Needs to be a list
            
            # Find time indices for the event duration
            start_idx = time_range.searchsorted(event['began'], side='left')
            end_idx = time_range.searchsorted(event['ended'], side='right')
            
            start_idx = max(0, start_idx)
            end_idx = min(len(time_range), end_idx)

            if start_idx >= end_idx:
                continue # Event is outside our time range

            # Rasterize the polygon once
            try:
                event_mask_2d = rasterize(
                    shapes=event_geom,
                    out_shape=out_shape,
                    transform=transform,
                    fill=0,
                    default_value=1,
                    dtype=np.uint8
                )
            except Exception as e:
                print(f"Warning: Skipping geometry, failed to rasterize. Error: {e}")
                continue

            # "Burn" this 2D mask onto all active days in the 3D array
            flood_mask_3d[start_idx:end_idx, :, :] = np.logical_or(
                flood_mask_3d[start_idx:end_idx, :, :],
                event_mask_2d
            )

        print("Rasterization complete.")
        
        # 6. Create xarray DataArray
        target_dataset = xr.Dataset(
            {
                'is_flooded': (
                    ['time', 'y', 'x'], 
                    flood_mask_3d,
                    {'long_name': 'Binary flood mask (1=flooded, 0=not flooded)'}
                )
            },
            coords={ 'time': time_range, 'y': ref_grid.y, 'x': ref_grid.x }
        )
        
        save_as_netcdf(target_dataset, config['output_paths']['target_variable'])
        return target_dataset

    except FileNotFoundError:
        print(f"ERROR: Flood events file not found at {events_path}")
        raise
    except KeyError as e:
        print(f"ERROR: Missing expected attribute in flood GeoJSON: {e}")
        print("Please ensure GeoJSON has 'BEGAN' and 'ENDED' properties.")
        raise
    except Exception as e:
        print(f"ERROR in process_flood_events: {e}")
        raise

# --- Step 5: Main Orchestration ---

def main():
    """
    Main function to run the entire data preprocessing pipeline.
    """
    try:
        # 0. Load Configuration
        config = load_config('config.json')
        time_range = get_time_range(config)
        
        # 1. Create Reference Grid
        ref_grid = create_reference_grid(config)
        
        # 2. Process Static Features
        static_ds = process_static_features(config, ref_grid)
        
        # 3. Process Dynamic Features
        dynamic_ds = process_dynamic_data(config, ref_grid, time_range)
        
        # 4. Process Target Variable
        target_ds = process_flood_events(config, ref_grid, time_range)
        
        # 5. Combine all datasets into the final model-ready file
        print("Step 5: Merging all datasets...")
        # Ensure static data is broadcast across the time dimension
        final_dataset = xr.merge([
            static_ds,
            dynamic_ds,
            target_ds
        ])
        
        # Set attributes for clarity
        final_dataset.attrs['description'] = 'Final preprocessed dataset for Bangladesh flood prediction.'
        final_dataset.attrs['crs'] = config['processing_params']['target_crs']
        final_dataset.attrs['grid_resolution'] = f"{config['processing_params']['target_resolution']} meters"
        
        # Save the final masterpiece
        save_as_netcdf(final_dataset, config['output_paths']['final_dataset'])
        
        print("\n--- Preprocessing Pipeline COMPLETE ---")
        print(f"Final dataset saved to: {config['output_paths']['final_dataset']}")
        print("\nDataset structure:")
        print(final_dataset)
        
    except Exception as e:
        print(f"\n--- Preprocessing Pipeline FAILED ---")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()