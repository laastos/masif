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
- Linux (Ubuntu 18.04+, RHEL 7+, CentOS 7+) - **Recommended**
- macOS (High Sierra 10.13+)
- Windows (via WSL2 or Docker)

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores, 2.6 GHz | 8+ cores |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB | 500 GB+ SSD |
| GPU | - | NVIDIA CUDA 10.0 compatible |

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

MaSIF requires Python 3.6 with specific package versions.

#### Create a Virtual Environment (Recommended)

```bash
# Using conda
conda create -n masif python=3.6
conda activate masif

# Or using venv
python3.6 -m venv masif_env
source masif_env/bin/activate
```

#### Install Python Packages

```bash
pip install numpy scipy scikit-learn
pip install tensorflow==1.9.0        # or tensorflow-gpu==1.9.0 for GPU support
pip install biopython==1.66
pip install open3d-python==0.5.0.0
pip install dask==2.2.0
pip install StrBioInfo
pip install ipython
```

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
# Download APBS 1.5
wget https://github.com/Electrostatics/apbs/releases/download/v1.5/APBS-1.5-linux64.tar.gz
tar xzf APBS-1.5-linux64.tar.gz -C ~/tools/

# Download PDB2PQR 2.1.1
wget https://github.com/Electrostatics/pdb2pqr/releases/download/v2.1.1/pdb2pqr-linux-bin64-2.1.1.tar.gz
tar xzf pdb2pqr-linux-bin64-2.1.1.tar.gz -C ~/tools/
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

export APBS_BIN=$HOME/tools/APBS-1.5-linux64/bin/apbs
export MULTIVALUE_BIN=$HOME/tools/APBS-1.5-linux64/share/apbs/tools/bin/multivalue
export PDB2PQR_BIN=$HOME/tools/pdb2pqr-linux-bin64-2.1.1/pdb2pqr

export PYMESH_PATH=$HOME/tools/PyMesh
```

Reload your shell configuration:

```bash
source ~/.bashrc
```

---

## Docker Installation

Docker provides the easiest installation path with all dependencies pre-configured.

### Build from Source (Recommended)

```bash
# Navigate to docker directory
cd masif/docker/

# Build the image (takes 15-30 minutes)
docker build -t masif .

# Run the container
docker run -it masif
```

### Pull Pre-built Image (Alternative)

```bash
# Pull the pre-built image if available
docker pull pablogainza/masif:latest

# Run the container
docker run -it pablogainza/masif

# Inside container, update to latest version
git pull
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

### GPU Support

The current Docker container (v2.0) is CPU-only. For GPU support, either:

1. Use the legacy GPU image: `docker pull pablogainza/masif:latest` with `--gpus all`
2. Use native installation with TensorFlow-GPU (see below)

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
