#!/usr/bin/env python
"""
更新的FNO模型推理脚本
支持包含弹性模量特征的模型
"""

import os
import sys
import argparse
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

class SimplifiedFNO:
    def __init__(self, hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42):
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=random_state,
            verbose=True
        )
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def evaluate(self, X_test, y_test):
        from sklearn.metrics import mean_squared_error
        predictions = self.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        return mse

class FNOInference:
    """更新的FNO模型推理器 - 支持弹性模量作为特征"""
    
    def __init__(self, model_path, scalers_path, dataset_path):
        self.model_path = model_path
        self.scalers_path = scalers_path
        self.dataset_path = dataset_path
        
        self.model = None
        self.scaler_features = None
        self.scaler_labels = None
        self.sample_coords = None
        self.e_moduli_available = None
        
        self._load_data()
    
    def _load_data(self):
        print("=" * 60)
        print("Loading data...")
        print("=" * 60)
        
        try:
            dataset = np.load(self.dataset_path)
            features = dataset['features']
            self.sample_coords = features[0, :, :3]
            self.e_moduli_available = dataset['e_moduli']
            print("✓ Dataset loaded")
            print(f"  Coordinates shape: {self.sample_coords.shape}")
            print(f"  Available E moduli: {self.e_moduli_available}")
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset: {e}")
        
        try:
            self.model = joblib.load(self.model_path)
            print(f"✓ Model loaded: {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
        
        try:
            scalers = np.load(self.scalers_path)
            self.scaler_features = StandardScaler()
            self.scaler_features.mean_ = scalers['feature_mean']
            self.scaler_features.scale_ = scalers['feature_std']
            
            self.scaler_labels = StandardScaler()
            self.scaler_labels.mean_ = scalers['label_mean']
            self.scaler_labels.scale_ = scalers['label_std']
            print("✓ Scalers loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load scalers: {e}")
    
    def predict(self, e_modulus, coordinates=None):
        print("\n" + "=" * 60)
        print("Performing inference...")
        print("=" * 60)
        
        if coordinates is None:
            coords = self.sample_coords.copy()
        else:
            coords = np.array(coordinates)
        
        num_nodes = coords.shape[0]
        
        print(f"Target E modulus: {e_modulus}")
        
        print("\nPreparing input features (X, Y, Z, E)...")
        X_input = np.zeros((num_nodes, 4))
        X_input[:, :3] = coords
        X_input[:, 3] = e_modulus
        
        print("Normalizing input...")
        X_normalized = self.scaler_features.transform(X_input)
        
        print("Running model inference...")
        y_pred_normalized = self.model.predict(X_normalized)
        
        print("Denormalizing output...")
        y_pred = self.scaler_labels.inverse_transform(y_pred_normalized)
        
        total_displacement = np.sqrt(np.sum(y_pred**2, axis=1))
        
        print(f"\nInference complete!")
        print(f"  Displacement ranges:")
        print(f"    X: [{y_pred[:, 0].min():.6f}, {y_pred[:, 0].max():.6f}]")
        print(f"    Y: [{y_pred[:, 1].min():.6f}, {y_pred[:, 1].max():.6f}]")
        print(f"    Z: [{y_pred[:, 2].min():.6f}, {y_pred[:, 2].max():.6f}]")
        print(f"  Max total displacement: {total_displacement.max():.6f}")
        
        return {
            'coordinates': coords,
            'displacements': y_pred,
            'total_displacement': total_displacement,
            'e_modulus_target': e_modulus
        }
    
    def save_results(self, results, output_dir="."):
        print("\n" + "=" * 60)
        print("Saving results...")
        print("=" * 60)
        
        os.makedirs(output_dir, exist_ok=True)
        
        npy_path = os.path.join(output_dir, 'prediction_results.npy')
        np.save(npy_path, results)
        print(f"✓ NumPy format saved: {npy_path}")
        
        try:
            import pyvista as pv
            
            grid = pv.PolyData(results['coordinates'])
            grid['x_displacement'] = results['displacements'][:, 0]
            grid['y_displacement'] = results['displacements'][:, 1]
            grid['z_displacement'] = results['displacements'][:, 2]
            grid['displacement_vector'] = results['displacements']
            grid['total_displacement'] = results['total_displacement']
            
            vtp_path = os.path.join(output_dir, 'displacement_results.vtp')
            grid.save(vtp_path)
            print(f"✓ VTP format saved: {vtp_path}")
            
            grid_ugrid = grid.cast_to_unstructured_grid()
            vtu_path = os.path.join(output_dir, 'displacement_results.vtu')
            grid_ugrid.save(vtu_path)
            print(f"✓ VTU format saved: {vtu_path}")
            
        except ImportError:
            print("Warning: PyVista not installed, skipping Paraview formats")
        
        return output_dir
    
    def visualize(self, results, output_dir=".", output_filename="displacement_pyvista.png"):
        print("\n" + "=" * 60)
        print("Generating visualization...")
        print("=" * 60)
        
        try:
            import pyvista as pv
            
            os.makedirs(output_dir, exist_ok=True)
            
            coords = results['coordinates']
            y_pred = results['displacements']
            total_disp = results['total_displacement']
            
            grid = pv.PolyData(coords)
            grid['x_displacement'] = y_pred[:, 0]
            grid['y_displacement'] = y_pred[:, 1]
            grid['z_displacement'] = y_pred[:, 2]
            grid['total_displacement'] = total_disp
            
            def get_percentile_range(data, lower=2, upper=98):
                return np.percentile(data, lower), np.percentile(data, upper)
            
            x_clim = get_percentile_range(y_pred[:, 0])
            y_clim = get_percentile_range(y_pred[:, 1])
            total_clim = get_percentile_range(total_disp, 0, 95)
            
            print(f"Data distribution analysis:")
            print(f"  X disp range: [{x_clim[0]:.3f}, {x_clim[1]:.3f}]")
            print(f"  Y disp range: [{y_clim[0]:.3f}, {y_clim[1]:.3f}]")
            print(f"  Total disp range: [{total_clim[0]:.3f}, {total_clim[1]:.3f}]")
            
            plotter = pv.Plotter(shape=(2, 2), off_screen=True, window_size=(1600, 1200))
            plotter.set_background('white')
            
            plotter.subplot(0, 0)
            plotter.add_mesh(grid, color='cornflowerblue', point_size=10, render_points_as_spheres=True)
            plotter.add_text('Original Geometry', font_size=14, color='black', position='upper_edge')
            plotter.add_axes(line_width=3, color='black')
            plotter.camera_position = 'xy'
            
            plotter.subplot(0, 1)
            plotter.add_mesh(grid, scalars='x_displacement', cmap='seismic', clim=x_clim, point_size=10, render_points_as_spheres=True)
            plotter.add_text('X Displacement', font_size=14, color='black', position='upper_edge')
            plotter.add_scalar_bar(title='X Displacement', color='black', title_font_size=12, label_font_size=10, n_labels=7, position_x=0.7, width=0.25)
            plotter.add_axes(line_width=3, color='black')
            plotter.camera_position = 'xy'
            
            plotter.subplot(1, 0)
            plotter.add_mesh(grid, scalars='y_displacement', cmap='plasma', clim=y_clim, point_size=10, render_points_as_spheres=True)
            plotter.add_text('Y Displacement', font_size=14, color='black', position='upper_edge')
            plotter.add_scalar_bar(title='Y Displacement', color='black', title_font_size=12, label_font_size=10, n_labels=7, position_x=0.7, width=0.25)
            plotter.add_axes(line_width=3, color='black')
            plotter.camera_position = 'xy'
            
            plotter.subplot(1, 1)
            plotter.add_mesh(grid, scalars='total_displacement', cmap='rainbow', clim=total_clim, point_size=10, render_points_as_spheres=True)
            plotter.add_text('Total Displacement', font_size=14, color='black', position='upper_edge')
            plotter.add_scalar_bar(title='Total Displacement', color='black', title_font_size=12, label_font_size=10, n_labels=7, position_x=0.7, width=0.25)
            plotter.add_axes(line_width=3, color='black')
            plotter.camera_position = 'xy'
            
            output_path = os.path.join(output_dir, output_filename)
            plotter.screenshot(output_path, return_img=False, scale=2)
            plotter.close()
            
            print(f"✓ Visualization saved: {output_path}")
            return output_path
            
        except ImportError:
            print("Warning: PyVista not installed, skipping visualization")
            return None


def main():
    parser = argparse.ArgumentParser(description='Updated FNO Model Inference Tool')
    parser.add_argument('--model_path', type=str, required=True, help='Path to FNO model (.pkl)')
    parser.add_argument('--scalers_path', type=str, required=True, help='Path to scalers (.npz)')
    parser.add_argument('--dataset_path', type=str, required=True, help='Path to dataset (.npz)')
    parser.add_argument('--output_dir', type=str, default='.', help='Output directory (default: .)')
    parser.add_argument('--e_modulus', type=float, default=200000, help='Target E modulus (default: 200000)')
    
    args = parser.parse_args()
    
    try:
        inferencer = FNOInference(
            model_path=args.model_path,
            scalers_path=args.scalers_path,
            dataset_path=args.dataset_path
        )
        
        results = inferencer.predict(e_modulus=args.e_modulus)
        inferencer.save_results(results, output_dir=args.output_dir)
        inferencer.visualize(results, output_dir=args.output_dir)
        
        print("\n" + "=" * 60)
        print("Inference complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
