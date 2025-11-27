# Installation Guide

This guide covers the complete installation of MaSIF and all its dependencies.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Native Installation](#native-installation)
  - [Installing Python Dependencies](#installing-python-dependencies)
  - [Installing External Tools](#installing-external-tools)
  - [Environment Configuration](#environment-configuration)
- [Docker Installation](#docker-installation)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Operating System

- Linux (Ubuntu 22.04+, RHEL 8+) - **Recommended**
- macOS (Monterey 12+)
- Windows (via WSL2 or Docker)

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores, 2.6 GHz | 8+ cores |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB | 500 GB+ SSD |
| GPU | - | NVIDIA GPU with CUDA 12.x support |

### Software Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12 |
| TensorFlow | 2.16.2 |
| CUDA | 12.6 (for GPU) |
| NVIDIA Driver | 525+ (for GPU) |

### Storage Considerations

MaSIF preprocessing generates large amounts of data due to overlapping patch storage:
- ~400GB per complete application dataset
- ~2MB per preprocessed protein
- Precomputed data can be downloaded from [Zenodo](https://doi.org/10.5281/zenodo.2625420)

---

## Installation Methods

Choose one of these methods:

| Method | Ease | Flexibility | Recommended For |
|--------|------|-------------|-----------------|
| [Docker](#docker-installation) | Easy | Limited | Quick testing, reproducibility |
| [Native](#native-installation) | Complex | Full | Production, development |

---

## Native Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/lpdi-epfl/masif.git
cd masif/
```

### Step 2: Installing Python Dependencies

MaSIF requires Python 3.12 with TensorFlow 2.16.

#### Create a Virtual Environment (Recommended)

```bash
# Using conda
conda create -n masif python=3.12
conda activate masif

# Or using venv
python3 -m venv masif_env
source masif_env/bin/activate
```

#### Install Python Packages

```bash
pip install --upgrade pip setuptools wheel

# TensorFlow with GPU support (includes CUDA libraries)
pip install "tensorflow[and-cuda]==2.16.2"

# Or CPU-only TensorFlow
pip install tensorflow==2.16.2

# Other dependencies
pip install numpy scipy scikit-learn
pip install biopython
pip install open3d
pip install dask
pip install SBILib
pip install ipython networkx plyfile packaging
```

**Note**: The code uses `tf.compat.v1` mode with `tf.disable_eager_execution()` for compatibility with existing trained models.

#### Installing PyMesh

PyMesh requires separate installation:

```bash
# Prerequisites
sudo apt-get install libeigen3-dev libgmp-dev libgmpxx4ldbl libmpfr-dev \
    libboost-dev libboost-thread-dev libtbb-dev python3-dev

# Clone and build PyMesh
git clone https://github.com/PyMesh/PyMesh.git
cd PyMesh
git submodule update --init
export PYMESH_PATH=$(pwd)

# Build
python setup.py build
python setup.py install

cd ..
```

### Step 3: Installing External Tools

MaSIF requires several external bioinformatics tools:

#### MSMS (Molecular Surface)

```bash
# Download MSMS 2.6.1
wget http://mgltools.scripps.edu/downloads/tars/releases/MSMSRELEASE/REL2.6.1/msms_i86_64Linux2_2.6.1.tar.gz
mkdir -p ~/tools/msms
tar xzf msms_i86_64Linux2_2.6.1.tar.gz -C ~/tools/msms

# Set permissions
chmod +x ~/tools/msms/msms
chmod +x ~/tools/msms/pdb_to_xyzrn
```

#### Reduce (Protonation)

```bash
# Clone and build reduce
git clone https://github.com/rlabduke/reduce.git
cd reduce
make
cd ..

# Or download pre-built binary
wget http://kinemage.biochem.duke.edu/downloads/software/reduce31/reduce.3.23.130521.linuxi386
chmod +x reduce.3.23.130521.linuxi386
mv reduce.3.23.130521.linuxi386 ~/tools/reduce/reduce
```

#### APBS and PDB2PQR (Electrostatics)

```bash
# Download APBS 3.4.1
wget https://github.com/Electrostatics/apbs/releases/download/v3.4.1/APBS-3.4.1.Linux.zip
unzip APBS-3.4.1.Linux.zip -d ~/tools/
chmod +x ~/tools/APBS-3.4.1.Linux/bin/apbs
chmod +x ~/tools/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue

# Install PDB2PQR via pip
pip install pdb2pqr
```

### Step 4: Environment Configuration

Add these environment variables to your `~/.bashrc` or `~/.bash_profile`:

```bash
# MaSIF External Tools Configuration
export MSMS_BIN=$HOME/tools/msms/msms
export PDB2XYZRN=$HOME/tools/msms/pdb_to_xyzrn

export REDUCE_BIN=$HOME/tools/reduce/reduce
export PATH=$PATH:$HOME/tools/reduce/
export REDUCE_HET_DICT=$HOME/tools/reduce/reduce_wwPDB_het_dict.txt

export APBS_BIN=$HOME/tools/APBS-3.4.1.Linux/bin/apbs
export MULTIVALUE_BIN=$HOME/tools/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue
export PDB2PQR_BIN=$(which pdb2pqr30)  # or create wrapper script

export PYMESH_PATH=$HOME/tools/PyMesh

# GPU optimization (optional, for TensorFlow GPU)
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_CPP_MIN_LOG_LEVEL=2
```

Reload your shell configuration:

```bash
source ~/.bashrc
```

---

## Docker Installation

Docker provides the easiest installation path with all dependencies pre-configured, including GPU support.

### Build from Source (Recommended)

```bash
# Navigate to docker directory
cd masif/docker/

# Build the image (takes 15-30 minutes)
docker build -t masif .

# Run the container with GPU support
docker run --gpus all -it masif

# Or run CPU-only
docker run -it masif
```

### GPU Requirements

For GPU support in Docker:

- NVIDIA GPU with CUDA 12.x support
- NVIDIA Driver 525+ installed on host
- nvidia-container-toolkit installed

```bash
# Install nvidia-container-toolkit (Ubuntu)
sudo apt-get install nvidia-container-toolkit
sudo systemctl restart docker
```

### Using Helper Commands

The Docker container includes convenient helper scripts:

```bash
# MaSIF-site
masif-site prepare 4ZQK_A
masif-site predict 4ZQK_A
masif-site color 4ZQK_A

# MaSIF-search
masif-search prepare 4ZQK_A_B
masif-search descriptors 4ZQK_A

# MaSIF-ligand
masif-ligand prepare 1ABC_A_ADP

# MaSIF-peptides
masif-peptides extract 1ABC_A
```

### Verify GPU Access in Docker

```bash
docker run --gpus all -it masif python3 -c \
    "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Docker Volume Mounting

To access local files from within Docker:

```bash
# Mount a local directory
docker run -it -v /path/to/local/data:/data masif

# Inside container, access files at /data
```

To copy files from container to host:

```bash
# Get container ID
docker ps

# Copy file out
docker cp <container_id>:/masif/data/masif_site/output/all_feat_3l/pred_surfaces/4ZQK_A.ply .
```

See the [Docker Setup Guide](docker.md) for comprehensive Docker documentation.

---

## Verifying Installation

### Test External Tools

```bash
# Test MSMS
$MSMS_BIN -h

# Test Reduce
reduce -h

# Test APBS
$APBS_BIN --version

# Test PDB2PQR
$PDB2PQR_BIN --help
```

### Test Python Environment

```python
# Test imports
python3 << 'EOF'
import numpy as np
import tensorflow as tf
import Bio
import pymesh
import open3d

print("NumPy:", np.__version__)
print("TensorFlow:", tf.__version__)
print("BioPython:", Bio.__version__)
print("All imports successful!")
EOF
```

### Run a Test Prediction

```bash
cd masif/data/masif_site/

# Prepare a single protein
./data_prepare_one.sh 4ZQK_A

# If successful, you should see:
# "Reading data from input ply surface files."
# "Dijkstra took X.XXs"
# "MDS took X.XXs"
```

---

## Troubleshooting

### Common Issues

#### ImportError: No module named 'pymesh'

PyMesh installation failed. Try:
```bash
cd $PYMESH_PATH
python setup.py clean
python setup.py build
python setup.py install
```

#### MSMS produces empty output

Check file permissions:
```bash
chmod +x $MSMS_BIN
chmod +x $PDB2XYZRN
```

#### APBS: "Unable to open file"

Ensure the path to APBS is correct and the binary has execute permissions:
```bash
ls -la $APBS_BIN
chmod +x $APBS_BIN
```

#### TensorFlow GPU not detected

Check CUDA installation:
```bash
nvidia-smi
nvcc --version
```

Ensure CUDA paths are set:
```bash
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/cuda/bin:$PATH
```

#### Memory errors during preprocessing

Increase available memory or process proteins sequentially:
```bash
# Reduce parallel workers in cluster jobs
# Or increase memory allocation in SLURM
#SBATCH --mem=32G
```

### Getting Help

1. Check the [GitHub Issues](https://github.com/LPDI-EPFL/masif/issues)
2. Review the [Troubleshooting Guide](troubleshooting.md)
3. Open a new issue with:
   - Operating system and version
   - Python version
   - Error message (full traceback)
   - Steps to reproduce
