# Docker Setup Guide

Docker provides the easiest way to run MaSIF with all dependencies pre-installed.

## Table of Contents

- [Quick Start](#quick-start)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Helper Commands](#helper-commands)
- [Working with Data](#working-with-data)
- [Running Applications](#running-applications)
- [Container Contents](#container-contents)
- [Environment Variables](#environment-variables)
- [Jupyter Notebook Support](#jupyter-notebook-support)
- [Building Custom Images](#building-custom-images)
- [Best Practices](#best-practices)
- [GPU Support](#gpu-support)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Navigate to the docker directory
cd docker/

# Build the image (takes 15-30 minutes)
docker build -t masif .

# Run the container with GPU support
docker run --gpus all -it masif

# Or run without GPU (CPU-only)
docker run -it masif

# Inside container, run MaSIF-site on example protein
masif-site prepare 4ZQK_A
masif-site predict 4ZQK_A
masif-site color 4ZQK_A
```

---

## Building the Image

### Standard Build

```bash
cd docker/
docker build -t masif .
```

### Build Options

```bash
# Build with a specific tag
docker build -t masif:v3.0 .

# Build without cache (for fresh builds)
docker build --no-cache -t masif .

# Build with progress output
docker build --progress=plain -t masif .
```

Build time: approximately 15-30 minutes depending on network speed and system performance.

### Alternative: Pull Pre-built Image

If available, you can pull a pre-built image:

```bash
docker pull pablogainza/masif:latest
```

---

## Running the Container

### Interactive Shell

```bash
docker run -it masif
```

### With Volume Mounting

Mount local directories to persist data:

```bash
# Mount a local directory for data
docker run -it \
    -v /path/to/local/data:/data \
    masif

# Mount for both input (read-only) and output
docker run -it \
    -v /path/to/pdbs:/input:ro \
    -v /path/to/output:/output \
    masif
```

### With Increased Memory

For large proteins:

```bash
docker run -it --memory=16g masif
```

---

## Helper Commands

The container includes convenient wrapper scripts for each MaSIF application. These can be run from anywhere inside the container.

### masif-site

Predict protein-protein interaction sites:

```bash
# Prepare data for a protein
masif-site prepare 4ZQK_A

# Run prediction
masif-site predict 4ZQK_A

# Generate colored surface for visualization
masif-site color 4ZQK_A
```

### masif-search

Compute surface descriptors for protein-protein complex prediction:

```bash
# Prepare data for a protein pair
masif-search prepare 4ZQK_A_B

# Compute neural network descriptors
masif-search descriptors 4ZQK_A

# Compute GIF descriptors (faster alternative)
masif-search gif 4ZQK_A
```

### masif-ligand

Predict ligand binding pockets:

```bash
# Prepare data for ligand binding prediction
masif-ligand prepare 1ABC_A_ADP

# Evaluate test set
masif-ligand evaluate
```

### masif-peptides

Analyze helical peptide binding sites:

```bash
# Extract helical peptides from structure
masif-peptides extract 1ABC_A

# Precompute surface patches
masif-peptides precompute 1ABC_A

# Run site prediction
masif-peptides predict 1ABC_A
```

---

## Working with Data

### Mounting Local Directories

```bash
# Mount input data directory
docker run -it \
    -v /path/to/local/pdbs:/masif/data/masif_site/data_preparation/00-raw_pdbs \
    masif

# Mount output directory
docker run -it \
    -v /path/to/output:/masif/data/masif_site/output \
    masif

# Mount both input and output
docker run -it \
    -v /path/to/input:/input \
    -v /path/to/output:/output \
    masif
```

### Copying Files from Container

```bash
# Get container ID
docker ps

# Copy file from container to host
docker cp <container_id>:/masif/data/masif_site/output/all_feat_3l/pred_surfaces/4ZQK_A.ply ./

# Copy entire directory
docker cp <container_id>:/masif/data/masif_site/output ./local_output/
```

### Using Pre-computed Data

Inside the container:

```bash
cd /masif/data/masif_ppi_search/
wget https://www.dropbox.com/s/09fwtic1095z9z6/masif_ppi_search_precomputed_data.tar.gz
tar xzf masif_ppi_search_precomputed_data.tar.gz
```

### Persistent Data Storage

Create a Docker volume for persistent storage:

```bash
# Create volume
docker volume create masif_data

# Run with volume
docker run -it \
    -v masif_data:/masif/data \
    masif

# Data persists between container runs
```

---

## Running Applications

### MaSIF-site (Traditional Method)

```bash
cd /masif/data/masif_site/

# Single protein
./data_prepare_one.sh 4ZQK_A
./predict_site.sh 4ZQK_A
./color_site.sh 4ZQK_A

# Using your own PDB file (mounted)
./data_prepare_one.sh --file /input/myprotein.pdb MYPDB_A
```

### MaSIF-search (Traditional Method)

```bash
cd /masif/data/masif_ppi_search/

# Prepare and compute descriptors
./data_prepare_one.sh 1AKJ_AB_DE
./compute_descriptors.sh 1AKJ_AB
./compute_descriptors.sh 1AKJ_DE

# Run benchmark
cd ../../comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100
```

### MaSIF-ligand (Traditional Method)

```bash
cd /masif/data/masif_ligand/

# Prepare data
./data_prepare_one.sh 1MBN_A_HEM

# Evaluate
./evaluate_test.sh
```

### Long-Running Jobs

For jobs that may take hours:

```bash
# Run in detached mode
docker run -d \
    --name masif_job \
    -v /path/to/output:/output \
    masif \
    bash -c "cd /masif/data/masif_site && ./reproduce_transient_benchmark.sh"

# Check logs
docker logs -f masif_job

# Attach to running container
docker attach masif_job

# Stop job
docker stop masif_job
```

---

## Container Contents

### Base Image

The container is built on `nvidia/cuda:12.6.3-base-ubuntu24.04` for full GPU support.

### Scientific Tools

| Tool | Version | Purpose |
|------|---------|---------|
| APBS | 3.4.1 | Poisson-Boltzmann electrostatics |
| MSMS | 2.6.1 | Molecular surface computation |
| PDB2PQR | 3.x (pip) | PDB to PQR conversion |
| Reduce | latest | Protonation |
| PyMesh | latest | Mesh operations |
| DSSP | System package | Secondary structure assignment |

### Python 3.12 Packages

| Package | Version | Purpose |
|---------|---------|---------|
| TensorFlow | 2.16.2 | Neural networks (GPU-enabled) |
| BioPython | latest | PDB file handling |
| Open3D | latest | RANSAC alignment |
| NumPy | latest | Numerical operations |
| SciPy | latest | Scientific computing |
| scikit-learn | latest | Machine learning utilities |
| NetworkX | latest | Graph operations |
| Dask | latest | Parallel computing |
| plyfile | latest | PLY file I/O |
| SBILib | latest | Biological assembly generation |

### Pre-trained Models

All pre-trained models are included:

| Application | Model | Description |
|-------------|-------|-------------|
| masif_site | all_feat_3l | 3-layer model with all features |
| masif_ligand | all_feat | Ligand binding pocket prediction |
| masif_ppi_search | sc05/all_feat | Protein-protein interaction search |
| masif_ppi_search_ub | sc05/all_feat | Unbound protein search |
| masif_pdl1_benchmark | sc05 + all_feat_3l | PD-L1:PD1 benchmark |
| masif_peptides | sc05 + all_feat_3l | Helical peptide analysis |

---

## Environment Variables

The container automatically sets all required environment variables:

```bash
# Tool paths
MSMS_BIN=/opt/msms/msms
PDB2XYZRN=/opt/msms/pdb_to_xyzrn
APBS_BIN=/opt/APBS-3.4.1.Linux/bin/apbs
MULTIVALUE_BIN=/opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue
PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr
REDUCE_HET_DICT=/usr/local/share/reduce_wwPDB_het_dict.txt
PYMESH_PATH=/opt/PyMesh
PYTHONPATH=/masif/source

# GPU optimization variables
XLA_FLAGS="--xla_gpu_enable_triton_gemm=false"
XLA_PYTHON_CLIENT_PREALLOCATE=true
XLA_CLIENT_MEM_FRACTION=0.95
TF_FORCE_GPU_ALLOW_GROWTH=true
TF_CPP_MIN_LOG_LEVEL=2
TF_ENABLE_ONEDNN_OPTS=0
```

---

## Jupyter Notebook Support

The container exposes port 8888 for Jupyter notebooks:

```bash
# Run with Jupyter
docker run -it \
    -p 8888:8888 \
    masif \
    jupyter notebook --ip=0.0.0.0 --allow-root --no-browser

# Access at http://localhost:8888
```

You may need to install Jupyter first:

```bash
# Inside container
pip3 install jupyter
```

---

## Building Custom Images

### Extending the Base Image

Create a custom Dockerfile:

```dockerfile
FROM masif:latest

# Add your modifications
RUN pip3 install your-package

# Add custom scripts
COPY my_script.py /masif/source/

# Set custom environment
ENV MY_VARIABLE=value
```

Build and run:

```bash
docker build -t masif:custom .
docker run -it masif:custom
```

### Dockerfile Structure Overview

The MaSIF Dockerfile (v3.0) includes these main sections:

1. **Base**: NVIDIA CUDA 12.6.3 on Ubuntu 24.04
2. **System dependencies**: Build tools, libraries
3. **Python virtual environment**: Python 3.12 venv (AlphaFold3 pattern)
4. **Python packages**: TensorFlow 2.16.2 with GPU support, BioPython, Open3D, etc.
5. **GPU environment variables**: XLA, TensorFlow GPU optimization
6. **MSMS**: Molecular surface computation
7. **APBS**: Electrostatics calculation (v3.4.1)
8. **PDB2PQR**: PDB to PQR conversion (pip)
9. **Reduce**: Protonation
10. **PyMesh**: Mesh operations
11. **MaSIF repository**: Cloned from GitHub
12. **Helper scripts**: masif-site, masif-search, masif-ligand, masif-peptides

---

## Best Practices

### Memory Management

```bash
# Increase container memory for large proteins
docker run --memory=16g -it masif

# Monitor memory usage
docker stats
```

### Resource Limits

```bash
# Limit CPU usage
docker run --cpus=4 -it masif

# Limit both CPU and memory
docker run --cpus=4 --memory=16g -it masif
```

### Container Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove everything unused
docker system prune
```

### Keeping Updated

Inside the container:

```bash
cd /masif
git pull
```

---

## GPU Support

The current Docker container (v3.0) includes full GPU support with CUDA 12.6 and TensorFlow 2.16.2.

### Requirements

- NVIDIA GPU with CUDA 12.x support
- NVIDIA Driver 525+ (recommended 580+)
- nvidia-container-toolkit installed on host

### Running with GPU

```bash
# Run with all available GPUs
docker run --gpus all -it masif

# Run with specific GPU
docker run --gpus '"device=0"' -it masif

# Run with multiple specific GPUs
docker run --gpus '"device=0,1"' -it masif
```

### Verify GPU Access

Inside the container:

```bash
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
# Expected: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU'), ...]
```

### CPU-Only Mode

The container also works without GPU:

```bash
docker run -it masif  # No --gpus flag
```

### Performance Comparison

| Task | CPU Time | GPU Time | Speedup |
|------|----------|----------|---------|
| Data preparation | ~2 min | ~2 min | 1x (CPU-bound) |
| MaSIF-site inference | ~30 sec | ~2 sec | 15x |
| MaSIF-search descriptors | ~45 sec | ~3 sec | 15x |
| Training (1 epoch) | ~hours | ~minutes | 10-20x |

### Installing nvidia-container-toolkit

If you don't have nvidia-container-toolkit installed:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check Docker daemon
sudo systemctl status docker

# Check for errors
docker logs <container_id>
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

### Memory Issues

For large proteins, increase container memory:

```bash
docker run -it --memory=16g masif
```

### Disk Space Issues

```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### MSMS or APBS Errors

If external tools fail, verify they're installed correctly:

```bash
# Inside container
$MSMS_BIN -h
$APBS_BIN --version
reduce -h
```

### Image Size

The full image is approximately 4-5 GB due to scientific dependencies. Ensure you have sufficient disk space before building.
