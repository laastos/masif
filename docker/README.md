# MaSIF Docker Container

This directory contains the Dockerfile for building a comprehensive MaSIF container. The container includes all MaSIF applications (site, search, ligand, peptides) along with pre-trained models.

**Note:** This is a CPU-only container. For GPU support with modern NVIDIA GPUs (Blackwell architecture, CUDA 12+), see the migration plan in `CUDA_UPDATE_PLAN.md`.

## Prerequisites

- Docker installed on your system
- At least 8GB of RAM recommended for large proteins

## Building the Image

```bash
# Navigate to the docker directory
cd docker/

# Build the image (takes 15-30 minutes)
docker build -t masif .

# Or with a specific tag
docker build -t masif:v2.0 .
```

### Build Options

```bash
# Build without cache (for fresh builds)
docker build --no-cache -t masif .

# Build with progress output
docker build --progress=plain -t masif .
```

## Running the Container

```bash
# Interactive shell
docker run -it masif
```

### With Volume Mounting

Mount local directories to persist data:

```bash
# Mount a local directory for output
docker run -it \
    -v /path/to/local/data:/data \
    masif

# Mount for both input and output
docker run -it \
    -v /path/to/pdbs:/input:ro \
    -v /path/to/output:/output \
    masif
```

### With Jupyter Notebook

```bash
docker run -it \
    -p 8888:8888 \
    masif \
    jupyter notebook --ip=0.0.0.0 --allow-root --no-browser
```

## Using Helper Commands

The container includes convenient wrapper scripts for each MaSIF application:

### MaSIF-site

```bash
# Prepare data for a protein
masif-site prepare 4ZQK_A

# Run prediction
masif-site predict 4ZQK_A

# Generate colored surface for visualization
masif-site color 4ZQK_A
```

### MaSIF-search

```bash
# Prepare data for a protein pair
masif-search prepare 4ZQK_A_B

# Compute neural network descriptors
masif-search descriptors 4ZQK_A

# Compute GIF descriptors (faster alternative)
masif-search gif 4ZQK_A
```

### MaSIF-ligand

```bash
# Prepare data for ligand binding prediction
masif-ligand prepare 1ABC_A_ADP

# Evaluate test set
masif-ligand evaluate
```

### MaSIF-peptides

```bash
# Extract helical peptides
masif-peptides extract 1ABC_A

# Precompute patches
masif-peptides precompute 1ABC_A

# Run site prediction
masif-peptides predict 1ABC_A
```

## Included Components

### Scientific Tools

| Tool | Version | Purpose |
|------|---------|---------|
| APBS | 1.5 | Poisson-Boltzmann electrostatics |
| MSMS | 2.6.1 | Molecular surface computation |
| PDB2PQR | 2.1.1 | PDB to PQR conversion |
| Reduce | latest | Protonation |
| PyMesh | latest | Mesh operations |

### Python Packages

**Python 3.6:**

- TensorFlow 1.12.0
- BioPython 1.73
- Open3D 0.8.0.0
- NumPy, SciPy, scikit-learn
- NetworkX, Dask

**Python 2.7:**

- SBI library (for biological assembly generation)
- NumPy, SciPy

### Pre-trained Models

All pre-trained models are included in the repository:

| Application | Model | Description |
|-------------|-------|-------------|
| masif_site | all_feat_3l | 3-layer model with all features |
| masif_ligand | all_feat | Ligand binding pocket prediction |
| masif_ppi_search | sc05/all_feat | Protein-protein interaction search |
| masif_ppi_search_ub | sc05/all_feat | Unbound protein search |
| masif_pdl1_benchmark | sc05 + all_feat_3l | PD-L1:PD1 benchmark |
| masif_peptides | sc05 + all_feat_3l | Helical peptide analysis |

## Environment Variables

The container sets up all required environment variables:

```bash
MSMS_BIN=/opt/msms/msms
PDB2XYZRN=/opt/msms/pdb_to_xyzrn
APBS_BIN=/opt/APBS-1.5-linux64/bin/apbs
MULTIVALUE_BIN=/opt/APBS-1.5-linux64/share/apbs/tools/bin/multivalue
PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr
REDUCE_HET_DICT=/usr/local/share/reduce_wwPDB_het_dict.txt
PYTHONPATH=/masif/source:$PYTHONPATH
```

## Troubleshooting

### Memory Issues

For large proteins, you may need to increase container memory:

```bash
docker run -it --memory=16g masif
```

### Permission Errors with Mounted Volumes

```bash
# Run as current user
docker run -it \
    --user $(id -u):$(id -g) \
    -v /path/to/data:/data \
    masif
```

### TensorFlow Warnings

TensorFlow may show warnings about CPU optimizations. These can be safely ignored or suppressed:

```bash
docker run -it -e TF_CPP_MIN_LOG_LEVEL=2 masif
```

## Updating the Repository

Inside the container:

```bash
cd /masif
git pull
```

## Image Size

The full image is approximately 4-5 GB due to scientific dependencies.

## License

MaSIF is released under the Apache License 2.0.
