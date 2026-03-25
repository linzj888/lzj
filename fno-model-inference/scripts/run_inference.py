import os
import sys
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

print("=" * 60)
print("FNO Model Inference")
print("=" * 60)

model_path = r"D:\test\tensile\fno_model.pkl"
scalers_path = r"D:\test\tensile\simulation_inputs\scalers.npz"
dataset_path = r"D:\test\tensile\simulation_inputs\fno_dataset.npz"
output_dir = r"D:\test\tensile"
e_modulus = 180000

print("\nLoading data...")

dataset = np.load(dataset_path)
features = dataset['features']
sample_coords = features[0, :, :3]
print(f"✓ Dataset loaded")
print(f"  Coordinates shape: {sample_coords.shape}")

model = joblib.load(model_path)
print(f"✓ Model loaded: {model_path}")

scalers = np.load(scalers_path)
scaler_features = StandardScaler()
scaler_features.mean_ = scalers['feature_mean']
scaler_features.scale_ = scalers['feature_std']

scaler_labels = StandardScaler()
scaler_labels.mean_ = scalers['label_mean']
scaler_labels.scale_ = scalers['label_std']
print("✓ Scalers loaded")

print("\nPerforming inference...")
print(f"Target E modulus: {e_modulus}")

num_nodes = sample_coords.shape[0]
X_input = np.zeros((num_nodes, 4))
X_input[:, :3] = sample_coords
X_input[:, 3] = e_modulus

print("Normalizing input...")
X_normalized = scaler_features.transform(X_input)

print("Running model inference...")
y_pred_normalized = model.predict(X_normalized)

print("Denormalizing output...")
y_pred = scaler_labels.inverse_transform(y_pred_normalized)

total_displacement = np.sqrt(np.sum(y_pred**2, axis=1))

print(f"\nInference complete!")
print(f"  Displacement ranges:")
print(f"    X: [{y_pred[:, 0].min():.6f}, {y_pred[:, 0].max():.6f}]")
print(f"    Y: [{y_pred[:, 1].min():.6f}, {y_pred[:, 1].max():.6f}]")
print(f"    Z: [{y_pred[:, 2].min():.6f}, {y_pred[:, 2].max():.6f}]")
print(f"  Max total displacement: {total_displacement.max():.6f}")

results = {
    'coordinates': sample_coords,
    'displacements': y_pred,
    'total_displacement': total_displacement,
    'e_modulus_target': e_modulus
}

print("\nSaving results...")
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

try:
    import pyvista as pv
    
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
    
    print(f"\nData distribution analysis:")
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
    
    output_path = os.path.join(output_dir, 'displacement_pyvista.png')
    plotter.screenshot(output_path, return_img=False, scale=2)
    plotter.close()
    
    print(f"✓ Visualization saved: {output_path}")
    
except ImportError:
    print("Warning: PyVista not installed, skipping visualization")

print("\n" + "=" * 60)
print("Inference complete!")
print("=" * 60)
