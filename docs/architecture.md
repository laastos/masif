# Source Code Architecture

This document describes the organization and structure of the MaSIF source code.

## Table of Contents

- [Directory Overview](#directory-overview)
- [Core Modules](#core-modules)
- [Neural Network Modules](#neural-network-modules)
- [Data Preparation Modules](#data-preparation-modules)
- [Application Modules](#application-modules)
- [Utility Modules](#utility-modules)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)

---

## Directory Overview

```
masif/
├── source/                          # All Python source code
│   ├── default_config/              # Configuration files
│   ├── masif_modules/               # Core neural network code
│   ├── data_preparation/            # Preprocessing scripts
│   ├── triangulation/               # Surface computation
│   ├── geometry/                    # Geometric calculations
│   ├── input_output/                # File I/O utilities
│   ├── masif_site/                  # MaSIF-site application
│   ├── masif_ppi_search/            # MaSIF-search application
│   ├── masif_ligand/                # MaSIF-ligand application
│   └── masif_pymol_plugin/          # PyMOL visualization
├── data/                            # Application data directories
│   ├── masif_site/
│   ├── masif_ppi_search/
│   ├── masif_ligand/
│   └── ...
├── comparison/                      # Benchmark comparisons
└── docker/                          # Docker configuration
```

---

## Core Modules

### default_config/

Central configuration for all MaSIF applications.

```
source/default_config/
├── __init__.py
├── masif_opts.py      # Main configuration dictionary
├── chemistry.py       # Chemical property definitions
└── global_vars.py     # Environment variable references
```

#### masif_opts.py

The main configuration file defining all parameters:

```python
masif_opts = {}

# Directory paths
masif_opts["raw_pdb_dir"] = "data_preparation/00-raw_pdbs/"
masif_opts["pdb_chain_dir"] = "data_preparation/01-benchmark_pdbs/"
masif_opts["ply_chain_dir"] = "data_preparation/01-benchmark_surfaces/"
masif_opts["tmp_dir"] = tempfile.gettempdir()

# Surface features
masif_opts["use_hbond"] = True
masif_opts["use_hphob"] = True
masif_opts["use_apbs"] = True
masif_opts["compute_iface"] = True

# Mesh parameters
masif_opts["mesh_res"] = 1.0
masif_opts["feature_interpolation"] = True
masif_opts["radius"] = 12.0

# Application-specific parameters
masif_opts["site"] = {...}
masif_opts["ppi_search"] = {...}
masif_opts["ligand"] = {...}
```

#### global_vars.py

References to external tool paths:

```python
import os

apbs_bin = os.environ.get('APBS_BIN', '')
multivalue_bin = os.environ.get('MULTIVALUE_BIN', '')
pdb2pqr_bin = os.environ.get('PDB2PQR_BIN', '')
msms_bin = os.environ.get('MSMS_BIN', '')
pdb2xyzrn = os.environ.get('PDB2XYZRN', '')
```

---

## Neural Network Modules

### masif_modules/

Core neural network definitions and training code.

```
source/masif_modules/
├── __init__.py
├── MaSIF_site.py              # MaSIF-site network
├── MaSIF_ppi_search.py        # MaSIF-search network
├── MaSIF_ligand.py            # MaSIF-ligand network
├── train_masif_site.py        # Site training loop
├── train_ppi_search.py        # Search training loop
├── read_data_from_surface.py  # Data loading utilities
└── read_ligand_tfrecords.py   # TFRecord reader
```

#### MaSIF_site.py

Neural network for interaction site prediction:

```python
class MaSIF_site:
    """
    Neural network for predicting protein-protein interaction sites.

    Architecture:
    - Input: Surface patches with chemical/geometric features
    - Geodesic convolution layers (configurable depth)
    - Dense output layer
    - Sigmoid activation for binary classification
    """

    def __init__(self, params):
        self.max_distance = params['max_distance']
        self.n_conv_layers = params['n_conv_layers']
        self.max_shape_size = params['max_shape_size']
        # ... build network

    def build_network(self):
        # Input placeholders
        self.input_feat = tf.placeholder(...)
        self.rho_coords = tf.placeholder(...)
        self.theta_coords = tf.placeholder(...)
        self.mask = tf.placeholder(...)

        # Geodesic convolution layers
        for i in range(self.n_conv_layers):
            x = self.geodesic_conv(x, ...)

        # Output layer
        self.output = tf.sigmoid(...)
```

#### MaSIF_ppi_search.py

Neural network for surface descriptor computation:

```python
class MaSIF_ppi_search:
    """
    Siamese network for computing complementary surface descriptors.

    Architecture:
    - Dual input streams for two proteins
    - Shared geodesic convolution layers
    - 80-dimensional descriptor output
    - Contrastive loss for training
    """

    def __init__(self, params):
        self.desc_dim = 80  # Descriptor dimensionality
        # ... build network

    def compute_descriptor(self, input_feat, rho, theta, mask):
        # Shared encoder for both proteins
        desc = self.encoder(input_feat, rho, theta, mask)
        return tf.nn.l2_normalize(desc, axis=-1)
```

#### read_data_from_surface.py

Utilities for loading and processing surface data:

```python
def read_data_from_surface(ply_file, params):
    """
    Read surface data from PLY file and decompose into patches.

    Returns:
        input_feat: Chemical features (N, max_neighbors, 5)
        rho: Radial coordinates (N, max_neighbors)
        theta: Angular coordinates (N, max_neighbors)
        mask: Valid neighbor mask (N, max_neighbors)
        neigh_indices: Neighbor vertex indices (N, max_neighbors)
        iface_labels: Interface labels (N,)
        verts: Vertex coordinates (N, 3)
    """
    # Read PLY file
    mesh = read_ply(ply_file)

    # Compute geodesic patches
    rho, theta, mask, neigh_indices = compute_patches(
        mesh.vertices, mesh.faces, params['max_distance']
    )

    # Extract features
    input_feat = extract_features(mesh, neigh_indices, params['feat_mask'])

    return input_feat, rho, theta, mask, neigh_indices, iface_labels, verts

def compute_shape_complementarity(ply1, ply2, ...):
    """
    Compute shape complementarity between two protein surfaces.
    Used for MaSIF-search training labels.
    """
    # ... implementation
```

---

## Data Preparation Modules

### data_preparation/

Scripts for preprocessing protein structures.

```
source/data_preparation/
├── 00-pdb_download.py               # Download PDB files
├── 00b-generate_assembly.py         # Biological assembly (ligand)
├── 00c-save_ligand_coords.py        # Ligand coordinates (ligand)
├── 01-pdb_extract_and_triangulate.py # Surface computation
├── 01b-helix_extract_and_triangulate.py # Helix extraction
├── 04-masif_precompute.py           # Patch precomputation
└── 04b-make_ligand_tfrecords.py     # TFRecord generation
```

#### Pipeline Flow

```
00-pdb_download.py
        │
        ▼ PDB file
01-pdb_extract_and_triangulate.py
        │
        ▼ PLY surface file
04-masif_precompute.py
        │
        ▼ Precomputed patches (.npy files)
```

### triangulation/

Surface generation and feature computation.

```
source/triangulation/
├── __init__.py
├── computeMSMS.py           # MSMS surface computation
├── computeAPBS.py           # Electrostatics
├── computeHydrophobicity.py # Hydrophobicity assignment
├── computeCharges.py        # Hydrogen bond features
├── assignChargesToNewMesh.py # Feature transfer
├── fixmesh.py               # Mesh regularization
├── xyzrn.py                 # XYZRN format conversion
└── compute_normal.py        # Surface normals
```

#### computeMSMS.py

Interface to MSMS external tool:

```python
def computeMSMS(pdb_file, protonate=True):
    """
    Compute molecular surface using MSMS.

    Args:
        pdb_file: Path to PDB file
        protonate: Whether to include hydrogens

    Returns:
        vertices: Surface vertex coordinates (N, 3)
        faces: Triangle face indices (M, 3)
        normals: Vertex normals (N, 3)
        names: Atom names for each vertex
        areas: Per-vertex area
    """
    # Convert PDB to XYZRN format
    xyzrn_file = convert_to_xyzrn(pdb_file)

    # Run MSMS
    subprocess.run([msms_bin, '-if', xyzrn_file, ...])

    # Parse output
    vertices, faces, normals = read_msms_output(...)

    return vertices, faces, normals, names, areas
```

#### computeAPBS.py

Poisson-Boltzmann electrostatics:

```python
def computeAPBS(vertices, pdb_file, prefix):
    """
    Compute electrostatic potential using APBS.

    This is the slowest preprocessing step (~30-60 seconds).

    Args:
        vertices: Surface vertex coordinates
        pdb_file: Input PDB file
        prefix: Output file prefix

    Returns:
        charges: Electrostatic potential at each vertex
    """
    # Convert to PQR format
    run_pdb2pqr(pdb_file, pqr_file)

    # Run APBS
    run_apbs(pqr_file, potential_file)

    # Map potential to vertices
    charges = multivalue(vertices, potential_file)

    return charges
```

### geometry/

Geometric calculations for patch decomposition.

```
source/geometry/
├── __init__.py
├── compute_polar_coordinates.py  # MDS-based coordinates
└── open3d_import.py              # Open3D integration
```

#### compute_polar_coordinates.py

This is a performance-critical module:

```python
def compute_polar_coordinates(vertices, faces, center_idx, radius):
    """
    Compute polar coordinates for a surface patch using MDS.

    This is computationally expensive (~20-30 seconds per protein).

    Algorithm:
    1. Find vertices within geodesic radius using Dijkstra
    2. Compute pairwise geodesic distances
    3. Apply MDS to embed in 2D
    4. Convert to polar coordinates (rho, theta)

    Args:
        vertices: Surface vertices
        faces: Triangle faces
        center_idx: Patch center vertex
        radius: Geodesic radius

    Returns:
        rho: Radial coordinates
        theta: Angular coordinates
        mask: Valid vertex mask
        indices: Neighbor vertex indices
    """
    # Dijkstra for geodesic distances
    distances = dijkstra(vertices, faces, center_idx)

    # Select vertices within radius
    neighbors = np.where(distances <= radius)[0]

    # MDS embedding
    coords_2d = mds_embed(distances[neighbors][:, neighbors])

    # Convert to polar
    rho = np.sqrt(coords_2d[:, 0]**2 + coords_2d[:, 1]**2)
    theta = np.arctan2(coords_2d[:, 1], coords_2d[:, 0])

    return rho, theta, mask, neighbors
```

### input_output/

File I/O utilities.

```
source/input_output/
├── __init__.py
├── extractPDB.py      # PDB chain extraction
├── extractHelix.py    # Helix extraction
├── protonate.py       # REDUCE protonation
├── read_msms.py       # MSMS output parsing
├── read_ply.py        # PLY file reading
└── save_ply.py        # PLY file writing
```

#### save_ply.py

Writing surface files with features:

```python
def save_ply(filename, vertices, faces, normals=None, charges=None,
             hbond=None, hphob=None, iface=None, normalize_charges=True):
    """
    Save mesh to PLY format with vertex attributes.

    Attributes saved:
    - Position (x, y, z)
    - Normal (nx, ny, nz)
    - Charges (electrostatic potential)
    - Hydrogen bond potential
    - Hydrophobicity
    - Interface labels
    """
    # Write PLY header
    write_header(file, len(vertices), len(faces), attributes)

    # Write vertex data
    for i in range(len(vertices)):
        write_vertex(file, vertices[i], normals[i],
                    charges[i], hbond[i], hphob[i], iface[i])

    # Write face data
    for face in faces:
        write_face(file, face)
```

---

## Application Modules

### masif_site/

MaSIF-site application entry points.

```
source/masif_site/
├── masif_site_train.py          # Training script
├── masif_site_predict.py        # Prediction script
├── masif_site_label_surface.py  # Surface coloring
└── README.md
```

### masif_ppi_search/

MaSIF-search application.

```
source/masif_ppi_search/
├── masif_ppi_search_train.py                  # Training
├── masif_ppi_search_comp_desc.py              # Descriptor computation
├── masif_ppi_search_cache_training_data.py    # Training data caching
├── alignment_utils_masif_search.py            # Alignment utilities
├── second_stage_alignment.py                  # RANSAC refinement
├── second_stage_alignment_nn.py               # NN-based refinement
└── README.md
```

### masif_ligand/

MaSIF-ligand application.

```
source/masif_ligand/
├── masif_ligand_train.py              # Training
├── masif_ligand_evaluate_test.py      # Evaluation
└── README.md
```

---

## Data Flow

### Complete Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT                                │
│              PDB File (protein structure)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PREPROCESSING                              │
│                                                             │
│  input_output/protonate.py     →  Add hydrogens             │
│  input_output/extractPDB.py    →  Extract chains            │
│  triangulation/computeMSMS.py  →  Molecular surface         │
│  triangulation/computeAPBS.py  →  Electrostatics            │
│  triangulation/fixmesh.py      →  Regularize mesh           │
│  input_output/save_ply.py      →  Save PLY surface          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PATCH DECOMPOSITION                        │
│                                                             │
│  geometry/compute_polar_coordinates.py                      │
│  masif_modules/read_data_from_surface.py                   │
│                                                             │
│  Output: rho, theta, mask, features, indices               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  NEURAL NETWORK                             │
│                                                             │
│  masif_modules/MaSIF_site.py                               │
│  masif_modules/MaSIF_ppi_search.py                         │
│  masif_modules/MaSIF_ligand.py                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        OUTPUT                               │
│                                                             │
│  MaSIF-site:    Per-vertex interaction probability         │
│  MaSIF-search:  80-dim surface descriptors                 │
│  MaSIF-ligand:  7-class ligand prediction                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feature Pipeline

```
Raw Atom Coordinates
        │
        ├──► MSMS → Surface mesh (vertices, faces)
        │
        ├──► REDUCE → Hydrogen positions
        │
        └──► BioPython → Residue assignments
                │
                ├──► Hydrophobicity (per-residue → per-vertex)
                │
                ├──► H-bond potential (polar atoms)
                │
                └──► APBS → Electrostatic potential
                        │
                        ▼
               Feature Vector [5 dimensions]
               [shape_idx, ddc, hphob, hbond, charges]
```

---

## Extension Points

### Adding New Features

1. **Create feature computation module** in `triangulation/`:

```python
# source/triangulation/computeNewFeature.py
def computeNewFeature(vertices, mesh, params):
    """Compute your new feature."""
    feature = ...
    return feature
```

2. **Modify preprocessing script**:

```python
# In 01-pdb_extract_and_triangulate.py
from triangulation.computeNewFeature import computeNewFeature

if masif_opts['use_new_feature']:
    new_feature = computeNewFeature(vertices, mesh, params)
```

3. **Update configuration**:

```python
# In masif_opts.py
masif_opts["use_new_feature"] = True
masif_opts["site"]["feat_mask"] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]  # 6 features
```

### Adding New Applications

1. **Create neural network class** in `masif_modules/`:

```python
# source/masif_modules/MaSIF_new_app.py
class MaSIF_new_app:
    def __init__(self, params):
        # Build network
        pass
```

2. **Create application module**:

```python
# source/masif_new_app/
#   ├── masif_new_app_train.py
#   ├── masif_new_app_predict.py
#   └── README.md
```

3. **Add configuration**:

```python
# In masif_opts.py
masif_opts["new_app"] = {
    "training_list": "lists/training.txt",
    "max_distance": 9.0,
    ...
}
```

4. **Create data directory**:

```
data/masif_new_app/
├── lists/
├── nn_models/
├── data_prepare_one.sh
└── train_nn.sh
```

### Modifying Neural Network Architecture

The geodesic convolution layers are defined in each `MaSIF_*.py` file. To modify:

```python
# In MaSIF_site.py
class MaSIF_site:
    def geodesic_conv(self, input_feat, rho, theta, mask, filters):
        """
        Geodesic convolution layer.

        Modify this to change convolution behavior.
        """
        # Current implementation
        ...

        # Your modifications
        ...

        return output
```

---

## Code Quality Notes

### Python Version

MaSIF was developed for Python 3.6. Key compatibility notes:
- Uses TensorFlow 1.x API
- Some modules require Python 2.7 (assembly generation)
- f-strings used throughout

### Dependencies

Critical dependencies and their roles:
- **TensorFlow 1.9**: Neural network framework
- **BioPython**: PDB file parsing
- **PyMesh**: Mesh operations
- **Open3D**: RANSAC alignment
- **NumPy/SciPy**: Numerical operations

### Error Handling

Most scripts include basic error handling:

```python
try:
    vertices, faces, ... = computeMSMS(pdb_file)
except:
    set_trace()  # IPython debugger
```

For production use, consider adding more robust error handling.
