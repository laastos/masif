# MaSIF Docker Container (GPU-Enabled with Blackwell Support)

This directory contains the Dockerfile for building a comprehensive MaSIF container with GPU support. The container includes all MaSIF applications (site, search, ligand, peptides) along with pre-trained models.

## GPU Support

This container uses **NVIDIA NGC TensorFlow 25.01** as its base, providing:
- TensorFlow 2.17.1 with Blackwell GPU optimizations
- CUDA 12.8.0 and cuDNN 9.7.0
- Support for compute capability 12.0 (Blackwell architecture)
- Compatible with NVIDIA RTX 5000 series and RTX PRO 6000 Blackwell GPUs

## Prerequisites

- Docker installed on your system
- NVIDIA Container Toolkit (`nvidia-container-toolkit`)
- NVIDIA Driver 570 or later (580+ for Blackwell GPUs)
- At least 8GB of RAM recommended for large proteins

### Installing NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Building the Image

```bash
# Navigate to the docker directory
cd docker/

# Build the image (takes 20-40 minutes due to PyMesh compilation)
docker build -t masif .

# Or with a specific tag
docker build -t masif:v3.1-blackwell .
```

### Build Options

```bash
# Build without cache (for fresh builds)
docker build --no-cache -t masif .

# Build with progress output
docker build --progress=plain -t masif .
```

## Running the Container

For Blackwell GPUs, use the recommended flags for optimal performance:

```bash
# Interactive shell with GPU support (recommended for Blackwell)
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it masif

# Simpler command (may work but less optimal)
docker run --gpus all -it masif
```

### With Volume Mounting

Mount local directories to persist data:

```bash
# Mount a local directory for output
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it \
    -v /path/to/local/data:/data \
    masif

# Mount for both input and output
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it \
    -v /path/to/pdbs:/input:ro \
    -v /path/to/output:/output \
    masif
```

### With Jupyter Notebook

```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it \
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
| APBS | 3.4.1 | Poisson-Boltzmann electrostatics |
| MSMS | 2.6.1 | Molecular surface computation |
| PDB2PQR | 3.x | PDB to PQR conversion |
| Reduce | latest | Protonation |
| PyMesh | latest | Mesh operations |

### Python Packages

**Python 3.12 (NGC TensorFlow 25.01):**

- TensorFlow 2.17.1 (Blackwell optimized)
- CUDA 12.8.0, cuDNN 9.7.0
- BioPython
- Open3D
- NumPy, SciPy, scikit-learn
- NetworkX, Dask

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
APBS_BIN=/opt/APBS-3.4.1.Linux/bin/apbs
MULTIVALUE_BIN=/opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue
PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr
REDUCE_HET_DICT=/usr/local/share/reduce_wwPDB_het_dict.txt
PYTHONPATH=/masif/source
TF_FORCE_GPU_ALLOW_GROWTH=true
TF_CPP_MIN_LOG_LEVEL=2
```

## Troubleshooting

### GPU Not Detected

```bash
# Verify NVIDIA Container Toolkit is working
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi

# If you see your GPU, the toolkit is working correctly
```

### Memory Issues

For large proteins, you may need to increase container memory:

```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it --memory=16g masif
```

### Permission Errors with Mounted Volumes

```bash
# Run as current user
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it \
    --user $(id -u):$(id -g) \
    -v /path/to/data:/data \
    masif
```

### TensorFlow Warnings

TensorFlow logging is set to level 2 (warnings only) by default. To see more verbose output:

```bash
docker run --gpus all -it -e TF_CPP_MIN_LOG_LEVEL=0 masif
```

### Multi-GPU Systems

To use a specific GPU:

```bash
# Use only GPU 0
docker run --gpus '"device=0"' --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it masif

# Use GPUs 0 and 1
docker run --gpus '"device=0,1"' --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it masif
```

## Updating the Repository

Inside the container:

```bash
cd /masif
git pull
```

## Image Size

The full image is approximately 15-20 GB due to NGC TensorFlow base image and scientific dependencies.

## License

MaSIF is released under the Apache License 2.0.
