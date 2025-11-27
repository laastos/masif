# File Formats

This document describes the file formats used in MaSIF for input, output, and intermediate data storage.

## Input Files

### PDB Files

Standard Protein Data Bank format for protein structures.

**Requirements**:
- Chain identifiers must be present
- ATOM records for protein atoms
- HETATM records for ligands (MaSIF-ligand only)

**Naming Convention**:
```
{PDBID}.pdb           # Full structure
{PDBID}_{CHAIN}.pdb   # Single chain extracted
```

**Example**:
```
4ZQK.pdb      # Full crystal structure
4ZQK_A.pdb    # Chain A only
```

## Surface Files

### PLY Format (Polygon File Format)

MaSIF stores molecular surfaces as PLY files with custom vertex attributes.

**Standard Structure**:
```
ply
format binary_little_endian 1.0
element vertex {N}
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float charge
property float cb
property float hbond
property float hphob
property float iface
element face {M}
property list uchar int vertex_indices
end_header
{binary data}
```

**Vertex Properties**:

| Property | Type | Description |
|----------|------|-------------|
| x, y, z | float | 3D coordinates |
| nx, ny, nz | float | Surface normal vector |
| charge | float | Electrostatic potential (APBS) |
| cb | float | Curvature value |
| hbond | float | Hydrogen bond potential |
| hphob | float | Hydrophobicity value |
| iface | float | Interface label (0 or 1) |

**Naming Convention**:
```
{PDBID}_{CHAIN}.ply
```

### MSMS Output Files

Intermediate files from MSMS surface computation.

**Files Generated**:
- `.vert`: Vertex coordinates and normals
- `.face`: Triangle connectivity
- `.area`: Per-atom surface areas

**Vertex File Format** (`.vert`):
```
{header_lines}
{x} {y} {z} {nx} {ny} {nz} {face_num} {sphere_num} {atom_name}
...
```

**Face File Format** (`.face`):
```
{header_lines}
{v1} {v2} {v3} {face_type} {atom_num}
...
```

## Precomputed Data

### NumPy Arrays

MaSIF stores precomputed data as NumPy `.npy` files.

**Directory Structure**:
```
04a-precomputation_12/
└── {PDBID}_{CHAIN}/
    ├── p1_X.npy              # X coordinates
    ├── p1_Y.npy              # Y coordinates
    ├── p1_Z.npy              # Z coordinates
    ├── p1_input_feat.npy     # Input features
    ├── p1_rho_wrt_center.npy # Geodesic distances
    ├── p1_theta_wrt_center.npy # Angular coordinates
    ├── p1_mask.npy           # Validity mask
    ├── p1_list_indices.npy   # Patch vertex indices
    └── p1_sc_labels.npy      # Shape complementarity labels
```

**Array Dimensions**:

| File | Shape | Description |
|------|-------|-------------|
| `p1_X.npy` | (N,) | X coordinates of patch centers |
| `p1_input_feat.npy` | (N, max_vertices, n_features) | Feature tensor |
| `p1_rho_wrt_center.npy` | (N, max_vertices) | Geodesic distances |
| `p1_theta_wrt_center.npy` | (N, max_vertices) | Angular coordinates |
| `p1_mask.npy` | (N, max_vertices) | Valid vertex mask |

### Coordinate Files

Stored in `03-coords/` directory.

```
{PDBID}_{CHAIN}/
├── p1_X.npy    # All X coordinates
├── p1_Y.npy    # All Y coordinates
├── p1_Z.npy    # All Z coordinates
└── p1_n.npy    # Normal vectors
```

## TFRecord Files (MaSIF-ligand)

TensorFlow record format for efficient training data loading.

**File Location**:
```
data/masif_ligand/tfrecords/
├── training_data_sequenceSplit_30.tfrecord
├── validation_data_sequenceSplit_30.tfrecord
└── testing_data_sequenceSplit_30.tfrecord
```

**Record Structure**:
```python
features = {
    'input_feat_shape': tf.io.FixedLenFeature([3], tf.int64),
    'input_feat': tf.io.VarLenFeature(tf.float32),
    'rho_wrt_center_shape': tf.io.FixedLenFeature([2], tf.int64),
    'rho_wrt_center': tf.io.VarLenFeature(tf.float32),
    'theta_wrt_center_shape': tf.io.FixedLenFeature([2], tf.int64),
    'theta_wrt_center': tf.io.VarLenFeature(tf.float32),
    'mask_shape': tf.io.FixedLenFeature([3], tf.int64),
    'mask': tf.io.VarLenFeature(tf.float32),
    'pdb': tf.io.FixedLenFeature([], tf.string),
    'pocket_labels_shape': tf.io.FixedLenFeature([2], tf.int64),
    'pocket_labels': tf.io.VarLenFeature(tf.int64),
}
```

## Descriptor Files

### MaSIF-search Descriptors

Surface fingerprint descriptors for protein matching.

**File Location**:
```
data/masif_ppi_search/descriptors/
└── {PDBID}_{CHAIN}/
    ├── p1_desc_flipped.npy    # Descriptors (flipped)
    ├── p1_desc_straight.npy   # Descriptors (straight)
    └── p1_sc_filt.npy         # Shape complementarity filter
```

**Descriptor Shape**: (N_patches, 80)

### GIF Descriptors

Geometric invariant fingerprints for comparison.

**Location**: `gif_descriptors/`

## Model Checkpoints

### TensorFlow Checkpoint Files

Model weights saved during training.

**Files**:
```
nn_models/{model_name}/model_data/
├── checkpoint              # Checkpoint index
├── model.index             # Variable index
├── model.data-00000-of-00001  # Variable data
└── model.meta              # Graph metadata (optional)
```

**Loading Checkpoints**:
```python
saver = tf.train.Saver()
saver.restore(session, 'model_data/model')
```

## List Files

### Training/Testing Lists

Plain text files with PDB identifiers.

**Format**:
```
4ZQK_A
1ABC_B
2DEF_CD
```

**Naming Convention**:
- `training.txt` - Training set
- `validation.txt` - Validation set
- `testing.txt` - Test set

### Ligand Coordinate Files

**Location**: `data/masif_ligand/ligand_coords/`

**Files**:
```
{PDBID}_ligand_coords.npy   # (N_ligands, N_atoms, 3) coordinates
{PDBID}_ligand_types.npy    # (N_ligands,) ligand type strings
```

## Configuration Files

### custom_params.py

Python module defining application-specific parameters.

**Example**:
```python
# nn_models/all_feat/custom_params.py
custom_params = {
    'model_dir': 'nn_models/all_feat/model_data/',
    'feat_mask': [1.0, 1.0, 1.0, 1.0, 1.0],
    'max_shape_size': 200,
    'n_thetas': 4,
    'n_rhos': 3,
}
```

## XYZRN Format

Intermediate format for MSMS input.

**Format**:
```
{x} {y} {z} {radius} {charge} {atom_name}
```

**Example**:
```
12.345 23.456 34.567 1.740000 1 ALA_42_CA
```

## Output Files

### Prediction Results

**MaSIF-site Output**:
- Per-vertex interaction probability
- Stored in PLY `iface` attribute

**MaSIF-search Output**:
- 80D descriptor vectors per patch
- Alignment scores for protein pairs

**MaSIF-ligand Output**:
- Per-vertex ligand class probabilities
- Confusion matrices for evaluation

## File Size Estimates

| File Type | Typical Size | Notes |
|-----------|--------------|-------|
| PDB file | 100KB - 10MB | Depends on complex size |
| PLY surface | 1-5 MB | ~10K-50K vertices |
| Precomputed data | 10-50 MB | Per protein |
| TFRecord | 1-5 GB | Full dataset |
| Descriptor file | 1-10 MB | Per protein |

## Compatibility Notes

### PyMesh PLY Format

MaSIF uses PyMesh for PLY I/O, which expects:
- Binary little-endian format
- Standard vertex/face elements
- Custom attributes as vertex properties

### Reading with Other Tools

```python
# Using plyfile library
from plyfile import PlyData
plydata = PlyData.read('surface.ply')
vertices = plydata['vertex']

# Using Open3D
import open3d as o3d
mesh = o3d.io.read_triangle_mesh('surface.ply')
```

## See Also

- [Data Preparation Pipeline](data-preparation.md) - How files are generated
- [API Reference](api-reference.md) - Functions for reading/writing files
- [Configuration Reference](configuration.md) - Directory paths configuration
