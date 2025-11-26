# Data Preparation Pipeline

This guide explains the complete data preprocessing workflow that transforms PDB structures into feature-rich surface patches ready for neural network analysis.

## Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Step 0: PDB Download](#step-0-pdb-download)
- [Step 1: Surface Triangulation](#step-1-surface-triangulation)
- [Step 4: Patch Precomputation](#step-4-patch-precomputation)
- [Application-Specific Steps](#application-specific-steps)
- [Running the Pipeline](#running-the-pipeline)
- [Performance Considerations](#performance-considerations)
- [Output File Reference](#output-file-reference)

---

## Pipeline Overview

The data preparation pipeline converts raw protein structures into feature-rich surface patches:

```
PDB File
    │
    ▼
┌─────────────────────────────────────┐
│  Step 0: Download/Load PDB          │  00-pdb_download.py
│  - Fetch from RCSB PDB              │
│  - Or use local file                │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Step 1: Extract & Triangulate      │  01-pdb_extract_and_triangulate.py
│  - Protonate with REDUCE            │
│  - Extract chains                   │
│  - Compute MSMS surface             │
│  - Calculate chemical features      │
│  - Regularize mesh                  │
│  - Save PLY file                    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Step 4: Precompute Patches         │  04-masif_precompute.py
│  - Extract overlapping patches      │
│  - Compute polar coordinates        │
│  - Calculate geodesic distances     │
│  - Save patch data                  │
└─────────────────────────────────────┘
    │
    ▼
Ready for Neural Network
```

---

## Step 0: PDB Download

**Script**: `source/data_preparation/00-pdb_download.py`

Downloads protein structure files from the RCSB Protein Data Bank.

### Usage

```bash
python $masif_source/data_preparation/00-pdb_download.py PDBID

# Example
python $masif_source/data_preparation/00-pdb_download.py 4ZQK
```

### What It Does

1. Connects to RCSB PDB (www.rcsb.org)
2. Downloads the PDB file
3. Saves to `data_preparation/00-raw_pdbs/{PDBID}.pdb`

### Using Local PDB Files

To skip download and use a local file:

```bash
# Copy your file to the raw_pdbs directory
cp /path/to/myprotein.pdb data_preparation/00-raw_pdbs/MYPDB.pdb

# Or use the --file flag in data_prepare_one.sh
./data_prepare_one.sh --file /path/to/myprotein.pdb MYPDB_A
```

---

## Step 1: Surface Triangulation

**Script**: `source/data_preparation/01-pdb_extract_and_triangulate.py`

This is the main preprocessing step that converts the atomic coordinates into a triangulated molecular surface with chemical features.

### Usage

```bash
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py PDBID_CHAIN

# Examples
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py 4ZQK_A
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py 1AKJ_AB
```

### Processing Steps

#### 1. Protonation (REDUCE)

```python
protonate(pdb_filename, protonated_file)
```

Adds hydrogen atoms to the structure using the REDUCE program. Hydrogen atoms are essential for:
- Accurate surface calculation
- Hydrogen bond detection
- Proper charge assignment

#### 2. Chain Extraction (BioPython)

```python
extractPDB(pdb_filename, out_filename+".pdb", chain_ids)
```

Extracts the specified chain(s) from the full PDB file:
- Single chain: `4ZQK_A` → extracts chain A
- Multiple chains: `4ZQK_AB` → extracts chains A and B together

#### 3. Surface Computation (MSMS)

```python
vertices, faces, normals, names, areas = computeMSMS(out_filename+".pdb", protonate=True)
```

Computes the solvent-excluded surface (Connolly surface) using MSMS:
- **Probe radius**: 1.5 Å (water molecule)
- **Output**: Triangulated mesh with vertices, faces, and normals
- **Names**: Atom names for each vertex (for feature assignment)

#### 4. Hydrogen Bond Features

```python
vertex_hbond = computeCharges(out_filename, vertices, names)
```

Computes hydrogen bond donor/acceptor potential:
- Identifies polar atoms (N, O, S)
- Assigns hydrogen bond capability to each vertex
- Feature values: donor (+1), acceptor (-1), none (0)

#### 5. Hydrophobicity

```python
vertex_hphobicity = computeHydrophobicity(names)
```

Assigns Kyte-Doolittle hydrophobicity values:
- Maps each vertex to nearest amino acid
- Assigns hydrophobicity value (-4.5 to +4.5)
- Normalized for neural network input

#### 6. Mesh Regularization (PyMesh)

```python
mesh = pymesh.form_mesh(vertices, faces)
regular_mesh = fix_mesh(mesh, masif_opts['mesh_res'])
```

Regularizes the mesh to ensure uniform vertex density:
- Removes degenerate triangles
- Ensures consistent edge lengths
- Target resolution: 1.0 Å (configurable)

#### 7. Electrostatics (APBS)

```python
vertex_charges = computeAPBS(regular_mesh.vertices, out_filename+".pdb", out_filename)
```

Computes Poisson-Boltzmann electrostatic potential:
- Uses APBS (Adaptive Poisson-Boltzmann Solver)
- Requires PDB2PQR for charge assignment
- Output: Electrostatic potential at each vertex
- **Note**: This is the slowest step (~30-60 seconds)

#### 8. Interface Labels (Optional)

```python
# Compute interface by comparing single chain to full complex surface
kdt = KDTree(v3)
d, r = kdt.query(regular_mesh.vertices)
iface_v = np.where(d >= 2.0)[0]
```

For training data, computes ground-truth interface labels:
- Compares single chain surface to full complex surface
- Vertices that are buried in the complex are marked as interface
- Distance threshold: 2.0 Å

#### 9. Save PLY File

```python
save_ply(out_filename+".ply", regular_mesh.vertices,
         regular_mesh.faces, normals=vertex_normal, charges=vertex_charges,
         normalize_charges=True, hbond=vertex_hbond, hphob=vertex_hphobicity,
         iface=iface)
```

Saves the surface as a PLY file with all computed features as vertex attributes.

### Output

- `data_preparation/01-benchmark_pdbs/{PDBID}_{CHAIN}.pdb` - Extracted chain
- `data_preparation/01-benchmark_surfaces/{PDBID}_{CHAIN}.ply` - Surface with features

---

## Step 4: Patch Precomputation

**Script**: `source/data_preparation/04-masif_precompute.py`

Decomposes the surface into overlapping radial patches and computes polar coordinates for each patch.

### Usage

```bash
python $masif_source/data_preparation/04-masif_precompute.py {masif_site|masif_ppi_search} PDBID_CHAIN

# Examples
python $masif_source/data_preparation/04-masif_precompute.py masif_site 4ZQK_A
python $masif_source/data_preparation/04-masif_precompute.py masif_ppi_search 1AKJ_AB_DE
```

### Processing Steps

#### 1. Read Surface Data

```python
input_feat, rho, theta, mask, neigh_indices, iface_labels, verts = read_data_from_surface(ply_file, params)
```

Reads the PLY file and extracts:
- Vertex coordinates
- All chemical features
- Interface labels (if present)

#### 2. Extract Patches

For each vertex on the surface:
- Find all vertices within the geodesic radius (9Å or 12Å)
- Compute geodesic distances using Dijkstra's algorithm
- Store vertex indices for each patch

#### 3. Compute Polar Coordinates

```
MDS (Multidimensional Scaling) Algorithm:
1. Compute pairwise geodesic distances within patch
2. Apply MDS to embed distances in 2D plane
3. Convert to polar coordinates (rho, theta)
```

**Note**: This is computationally expensive (~20-30 seconds per protein)

#### 4. Shape Complementarity (MaSIF-search only)

```python
p1_sc_labels, p2_sc_labels = compute_shape_complementarity(...)
```

For protein pairs, computes shape complementarity between interacting surfaces:
- Measures geometric fit between surface patches
- Used for training MaSIF-search

### Output Files

Saved to `data_preparation/04{a,b}-precomputation_{9,12}A/precomputation/{PDBID}_{CHAIN}/`:

| File | Description |
|------|-------------|
| `p1_rho_wrt_center.npy` | Radial coordinates for each patch |
| `p1_theta_wrt_center.npy` | Angular coordinates for each patch |
| `p1_input_feat.npy` | Chemical features array |
| `p1_mask.npy` | Valid vertex mask for each patch |
| `p1_list_indices.npy` | Vertex indices within each patch |
| `p1_iface_labels.npy` | Interface labels (ground truth) |
| `p1_X.npy`, `p1_Y.npy`, `p1_Z.npy` | Vertex coordinates |
| `p1_sc_labels.npy` | Shape complementarity (MaSIF-search only) |

---

## Application-Specific Steps

### MaSIF-ligand Additional Steps

#### 00b: Generate Biological Assembly

```bash
python $masif_source/data_preparation/00b-generate_assembly.py PDBID
```

Generates the biological assembly (oligomeric state) using StrBioInfo library.

#### 00c: Save Ligand Coordinates

```bash
python $masif_source/data_preparation/00c-save_ligand_coords.py PDBID_CHAIN_LIGAND
```

Extracts and saves ligand coordinates for training labels.

#### 04b: Make TFRecords

```bash
python $masif_source/data_preparation/04b-make_ligand_tfrecords.py
```

Converts precomputed data to TensorFlow record format for efficient training.

---

## Running the Pipeline

### Single Protein

Use the convenience script:

```bash
cd data/masif_site/
./data_prepare_one.sh 4ZQK_A
```

This runs all necessary steps automatically.

### Using a Custom PDB File

```bash
./data_prepare_one.sh --file /path/to/myprotein.pdb MYPDB_A
```

### Batch Processing

#### Sequential (Simple)

```bash
for pdb in $(cat lists/training.txt); do
    ./data_prepare_one.sh $pdb
done
```

#### Parallel (SLURM Cluster)

```bash
sbatch data_prepare.slurm
```

The SLURM script distributes processing across cluster nodes.

### Manual Step-by-Step

```bash
# Set up paths
export masif_root=$(git rev-parse --show-toplevel)
export masif_source=$masif_root/source/
export PYTHONPATH=$PYTHONPATH:$masif_source

# Step 0: Download PDB
python $masif_source/data_preparation/00-pdb_download.py 4ZQK

# Step 1: Triangulate
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py 4ZQK_A

# Step 4: Precompute patches
python $masif_source/data_preparation/04-masif_precompute.py masif_site 4ZQK_A
```

---

## Performance Considerations

### Time Benchmarks

| Step | Time per Protein | Bottleneck |
|------|------------------|------------|
| PDB Download | ~1 sec | Network |
| Protonation | ~2 sec | CPU |
| MSMS Surface | ~5 sec | CPU |
| Mesh Regularization | ~10 sec | CPU |
| APBS Electrostatics | ~30-60 sec | CPU |
| Polar Coordinates | ~20-30 sec | CPU (MDS) |
| **Total** | **~2 minutes** | |

### Storage Requirements

| Data Type | Size per Protein | Full Dataset |
|-----------|------------------|--------------|
| Raw PDB | ~0.5 MB | ~5 GB |
| PLY Surface | ~2 MB | ~20 GB |
| Precomputed Patches | ~20 MB | ~200 GB |
| **Total** | ~25 MB | ~400 GB |

### Optimization Tips

1. **Use Cluster Computing**: SLURM scripts distribute preprocessing
2. **SSD Storage**: Faster I/O for many small files
3. **Memory**: 16GB+ for large proteins
4. **Skip Steps**: Use precomputed data from [Zenodo](https://doi.org/10.5281/zenodo.2625420)

### Main Bottlenecks

1. **APBS Electrostatics**: Slowest single step, ~30-60 seconds
2. **MDS for Polar Coordinates**: Complex computation, ~20-30 seconds
3. **Mesh Regularization**: PyMesh operations, ~10 seconds

---

## Output File Reference

### Directory Structure

```
data_preparation/
├── 00-raw_pdbs/
│   └── {PDBID}.pdb
├── 00b-pdbs_assembly/          # MaSIF-ligand only
│   └── {PDBID}.pdb
├── 00c-ligand_coords/          # MaSIF-ligand only
│   └── {PDBID}_{CHAIN}_{LIGAND}.npy
├── 01-benchmark_pdbs/
│   └── {PDBID}_{CHAIN}.pdb
├── 01-benchmark_surfaces/
│   └── {PDBID}_{CHAIN}.ply
├── 04a-precomputation_9A/      # MaSIF-site
│   └── precomputation/
│       └── {PDBID}_{CHAIN}/
│           ├── p1_rho_wrt_center.npy
│           ├── p1_theta_wrt_center.npy
│           ├── p1_input_feat.npy
│           ├── p1_mask.npy
│           ├── p1_list_indices.npy
│           ├── p1_iface_labels.npy
│           ├── p1_X.npy
│           ├── p1_Y.npy
│           └── p1_Z.npy
├── 04b-precomputation_12A/     # MaSIF-search
│   └── precomputation/
│       └── {PDBID}_{CHAIN1}_{CHAIN2}/
│           ├── p1_*.npy          # First protein
│           ├── p2_*.npy          # Second protein
│           ├── p1_sc_labels.npy  # Shape complementarity
│           └── p2_sc_labels.npy
└── tfrecords/                   # MaSIF-ligand only
    └── *.tfrecord
```

### PLY File Format

The PLY surface files contain:

```
ply
format binary_little_endian 1.0
element vertex N
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float charge         # Electrostatic potential
property float hbond          # H-bond potential
property float hphob          # Hydrophobicity
property float iface          # Interface label
element face M
property list uchar int vertex_indices
end_header
[binary vertex data]
[binary face data]
```

### NumPy File Contents

| File | Shape | Description |
|------|-------|-------------|
| `*_rho_wrt_center.npy` | (N, max_neighbors) | Radial coordinates |
| `*_theta_wrt_center.npy` | (N, max_neighbors) | Angular coordinates |
| `*_input_feat.npy` | (N, max_neighbors, 5) | Features: [shape_idx, ddc, hphob, hbond, charge] |
| `*_mask.npy` | (N, max_neighbors) | Binary mask for valid neighbors |
| `*_list_indices.npy` | (N, max_neighbors) | Neighbor vertex indices |
| `*_iface_labels.npy` | (N,) | Interface labels (0 or 1) |
| `*_X/Y/Z.npy` | (N,) | Vertex coordinates |
| `*_sc_labels.npy` | (N,) | Shape complementarity scores |

Where N = number of vertices, max_neighbors = max vertices per patch (100 for site, 200 for search).
