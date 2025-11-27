# API Reference

This document provides a reference for the main Python modules in MaSIF.

## Module Overview

```
source/
├── default_config/     # Configuration and global variables
├── data_preparation/   # Data preprocessing scripts
├── geometry/           # Geometric calculations
├── input_output/       # File I/O utilities
├── masif_modules/      # Neural network definitions
├── masif_site/         # MaSIF-site application
├── masif_ligand/       # MaSIF-ligand application
├── masif_ppi_search/   # MaSIF-search application
├── masif_pymol_plugin/ # PyMOL visualization
└── triangulation/      # Surface computation
```

## Configuration

### default_config.masif_opts

Central configuration dictionary for all MaSIF applications.

```python
from default_config.masif_opts import masif_opts

# Access application-specific options
site_opts = masif_opts['site']
ligand_opts = masif_opts['ligand']
ppi_search_opts = masif_opts['ppi_search']
```

**Key Configuration Fields**:

| Field | Description |
|-------|-------------|
| `masif_precomputation_dir` | Directory for precomputed data |
| `ply_chain_dir` | Directory for PLY surface files |
| `coord_dir` | Directory for coordinate arrays |
| `max_shape_size` | Maximum vertices per patch |
| `patch_radius` | Geodesic radius in Angstroms |
| `feature_mask` | Boolean mask for input features |

### default_config.global_vars

Environment-dependent paths for external tools.

```python
from default_config.global_vars import (
    msms_bin,      # MSMS executable
    apbs_bin,      # APBS executable
    pdb2pqr_bin,   # PDB2PQR executable
    multivalue_bin # APBS multivalue tool
)
```

### default_config.chemistry

Chemical data tables.

```python
from default_config.chemistry import (
    radii,            # Atomic radii dictionary
    polarHydrogens,   # Polar hydrogen atom names by residue
    hbond_std_dev     # Standard deviation for H-bond distance
)
```

## Input/Output

### input_output.read_ply

Read MaSIF-formatted PLY surface files.

```python
from input_output.read_ply import read_ply

vertices, faces, normals, charge, cb, hbond, hphob = read_ply(filename)
```

**Returns**:
- `vertices`: (N, 3) array of vertex coordinates
- `faces`: (M, 3) array of triangle indices
- `normals`: (N, 3) array of vertex normals
- `charge`: (N,) array of electrostatic charges
- `cb`: (N,) array of curvature values
- `hbond`: (N,) array of hydrogen bond potential
- `hphob`: (N,) array of hydrophobicity values

### input_output.save_ply

Save mesh with attributes as PLY file.

```python
from input_output.save_ply import save_ply

save_ply(
    filename,
    vertices,       # (N, 3) coordinates
    faces,          # (M, 3) triangle indices
    normals=None,   # (N, 3) optional normals
    charges=None,   # (N,) optional charges
    normalize_charges=False,
    hbond=None,     # (N,) optional H-bond potential
    hphob=None,     # (N,) optional hydrophobicity
    iface=None      # (N,) optional interface labels
)
```

### input_output.extractPDB

Extract chains from PDB files.

```python
from input_output.extractPDB import extractPDB

extractPDB(
    infilename,     # Input PDB path
    outfilename,    # Output PDB path
    chain_ids       # List of chain IDs to extract
)
```

### input_output.protonate

Add hydrogen atoms using Reduce.

```python
from input_output.protonate import protonate

protonate(
    in_pdb_file,    # Input PDB without hydrogens
    out_pdb_file    # Output PDB with hydrogens
)
```

### input_output.read_msms

Read MSMS surface output files.

```python
from input_output.read_msms import read_msms

vertices, faces, normals, names = read_msms(file_root)
```

## Triangulation

### triangulation.computeMSMS

Compute molecular surface using MSMS.

```python
from triangulation.computeMSMS import computeMSMS

vertices, faces, normals, names, areas = computeMSMS(
    pdb_file,
    protonate=True
)
```

### triangulation.fixmesh

Regularize mesh for consistent vertex density.

```python
from triangulation.fixmesh import fix_mesh

mesh = fix_mesh(mesh, resolution=1.0)
```

### triangulation.computeCharges

Compute Poisson-Boltzmann electrostatics using APBS.

```python
from triangulation.computeCharges import computeCharges

charges = computeCharges(
    pdb_file,
    vertices    # Surface vertex coordinates
)
```

### triangulation.computeHydrophobicity

Assign hydrophobicity values to surface vertices.

```python
from triangulation.computeHydrophobicity import computeHydrophobicity

hphob = computeHydrophobicity(names)
```

**Hydrophobicity Scale**: Kyte-Doolittle scale normalized to [0, 1]

### triangulation.compute_normal

Compute vertex normals from mesh.

```python
from triangulation.compute_normal import compute_normal

normals = compute_normal(vertices, faces)
```

## Geometry

### geometry.compute_polar_coordinates

Compute geodesic polar coordinates for surface patches.

```python
from geometry.compute_polar_coordinates import compute_polar_coordinates

rho, theta, neigh_idx, mask = compute_polar_coordinates(
    mesh,
    radius=12.0,      # Patch radius in Angstroms
    max_vertices=200  # Maximum vertices per patch
)
```

**Returns**:
- `rho`: (N, max_vertices) geodesic distances
- `theta`: (N, max_vertices) angular coordinates
- `neigh_idx`: (N, max_vertices) neighbor indices
- `mask`: (N, max_vertices) validity mask

## Neural Network Modules

### masif_modules.MaSIF_site

Site prediction neural network.

```python
from masif_modules.MaSIF_site import MaSIF_site

model = MaSIF_site(
    max_rho=9.0,
    n_thetas=4,
    n_rhos=3,
    n_rotations=16,
    idx_gpu='/gpu:0',
    feat_mask=[1, 1, 1, 1, 1],
    n_conv_layers=2,
    learning_rate=1e-4,
    n_features=5
)

# Training
model.session.run(model.optimizer, feed_dict={...})

# Inference
predictions = model.session.run(model.full_score, feed_dict={...})
```

### masif_modules.MaSIF_ppi_search

Surface fingerprint network.

```python
from masif_modules.MaSIF_ppi_search import MaSIF_ppi_search

model = MaSIF_ppi_search(
    max_rho=12.0,
    n_thetas=16,
    n_rhos=5,
    n_rotations=16,
    idx_gpu='/gpu:0',
    feat_mask=[1, 1, 1, 1, 1],
    n_conv_layers=2,
    out_channels=80,
    learning_rate=1e-3
)

# Compute descriptors
desc = model.session.run(model.descriptor, feed_dict={...})
```

### masif_modules.MaSIF_ligand

Ligand pocket classification network.

```python
from masif_modules.MaSIF_ligand import MaSIF_ligand

model = MaSIF_ligand(
    max_rho=12.0,
    n_thetas=16,
    n_rhos=5,
    n_ligands=7,    # Number of ligand classes
    idx_gpu='/gpu:0'
)
```

### masif_modules.read_data_from_surface

Load precomputed surface data for neural network input.

```python
from masif_modules.read_data_from_surface import read_data_from_surface

data = read_data_from_surface(
    pdb_id,
    masif_opts,
    pid='p1'  # 'p1' or 'p2' for protein 1 or 2
)
```

**Returns** dictionary with:
- `input_feat`: (N, max_vertices, n_features) feature tensor
- `rho`: (N, max_vertices) geodesic distances
- `theta`: (N, max_vertices) angular coordinates
- `mask`: (N, max_vertices) validity mask
- `indices`: Vertex indices for each patch

## Application Scripts

### masif_site.masif_site_predict

Run MaSIF-site predictions.

```python
from masif_site.masif_site_predict import run_masif_site

run_masif_site(params, pdb_list)
```

### masif_ppi_search.masif_ppi_search_comp_desc

Compute MaSIF-search descriptors.

```python
from masif_ppi_search.masif_ppi_search_comp_desc import compute_descriptors

compute_descriptors(params, pdb_list)
```

## Data Preparation Scripts

### 00-pdb_download

Download PDB structures from RCSB.

```bash
python 00-pdb_download.py --pdb_list lists/all.txt
```

### 01-pdb_extract_and_triangulate

Extract chains and compute molecular surface.

```bash
python 01-pdb_extract_and_triangulate.py 4ZQK_A
```

### 04-masif_precompute

Precompute patches and features for neural network input.

```bash
python 04-masif_precompute.py 4ZQK_A
```

## Utility Functions

### Common Feed Dict Construction

```python
def build_feed_dict(model, data):
    return {
        model.input_feat: data['input_feat'],
        model.rho_coords: data['rho'],
        model.theta_coords: data['theta'],
        model.mask: data['mask'],
        model.labels: data['labels'],
        model.keep_prob: 1.0  # 1.0 for inference, <1.0 for training
    }
```

### Loading Pretrained Models

```python
import tensorflow.compat.v1 as tf

# Create model instance
model = MaSIF_site(...)

# Restore weights
saver = tf.train.Saver()
saver.restore(model.session, 'nn_models/model_data/model')
```

## Error Handling

Common exceptions and how to handle them:

```python
# Missing precomputed data
try:
    data = read_data_from_surface(pdb_id, opts)
except FileNotFoundError:
    print(f"Run data preparation for {pdb_id} first")

# Invalid PDB structure
try:
    vertices, faces, normals, names, areas = computeMSMS(pdb_file)
except RuntimeError:
    print(f"MSMS failed for {pdb_file}")
```

## See Also

- [Configuration Reference](configuration.md) - Detailed configuration options
- [Neural Network Architecture](neural-networks.md) - Network architecture details
- [Data Preparation Pipeline](data-preparation.md) - Complete preprocessing workflow
