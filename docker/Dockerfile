# MaSIF Docker Container (GPU-Enabled with Blackwell Support)
# Includes all tools: MaSIF-site, MaSIF-search, MaSIF-ligand, MaSIF-peptides
#
# Build: docker build -t masif .
# Run:   docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it masif
#
# Blackwell GPU Support: Uses NVIDIA NGC TensorFlow 25.01 container with
# CUDA 12.8 and cuDNN 9.7 for compute capability 12.0 support.

# ============================================================================
# STAGE 1: Build PyMesh in Ubuntu 22.04 (GCC 11 compatible)
# ============================================================================
# PyMesh's bundled third-party libraries (mmg, tbb, draco) have GCC 13+
# incompatibilities. Ubuntu 22.04's default GCC 11 works reliably.
# We install Python 3.12 via deadsnakes PPA to ensure wheel compatibility.
FROM ubuntu:22.04 AS pymesh-builder

ENV DEBIAN_FRONTEND=noninteractive

# Install PyMesh build dependencies and Python 3.12 from deadsnakes PPA
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    libboost-all-dev \
    libeigen3-dev \
    libgmp-dev \
    libgmpxx4ldbl \
    libmpfr-dev \
    libcgal-dev \
    libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

# Create Python 3.12 venv and install build tools
RUN python3.12 -m venv /build_venv
ENV PATH="/build_venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel numpy

# Build PyMesh with Python 3.12
# Note: draco header patches needed for Python 3.12 compatibility
# Note: mmg has global variable definitions in headers causing multiple definition
#       linker errors. We allow multiple definitions as a workaround.
# Note: BOOST_BIND_GLOBAL_PLACEHOLDERS silences deprecation warning
# Note: PyMesh's bundled pybind11 (2.2.x) is too old for Python 3.11+.
#       We replace it with pybind11 2.11+ which supports Python 3.12.
WORKDIR /opt
ENV LDFLAGS="-Wl,--allow-multiple-definition"
ENV CXXFLAGS="-DBOOST_BIND_GLOBAL_PLACEHOLDERS"
RUN git clone --depth 1 https://github.com/PyMesh/PyMesh.git && \
    cd PyMesh && \
    git submodule update --init --recursive && \
    # Fix missing C++ headers in draco (required for Python 3.12)
    sed -i '/#include <functional>/a #include <cstddef>' \
        third_party/draco/src/draco/core/hash_utils.h && \
    sed -i '/#include <cctype>/a #include <limits>' \
        third_party/draco/src/draco/io/parser_utils.cc && \
    # Update pybind11 to version 2.11.1 (supports Python 3.12)
    rm -rf third_party/pybind11 && \
    git clone --depth 1 --branch v2.11.1 https://github.com/pybind/pybind11.git third_party/pybind11 && \
    python setup.py bdist_wheel && \
    cp dist/pymesh2-*.whl /tmp/ && \
    python -c "import sys; print(f'PyMesh wheel built for Python {sys.version_info.major}.{sys.version_info.minor}')"

# ============================================================================
# STAGE 2: Final MaSIF container with Blackwell GPU support
# ============================================================================
# Use NVIDIA NGC TensorFlow 25.01 container which has native Blackwell support
# - TensorFlow 2.17.1 with Blackwell optimizations
# - CUDA 12.8.0 and cuDNN 9.7.0 (supports compute capability 12.0)
# - Python 3.12.3
# - Ubuntu 24.04.1 LTS base
FROM nvcr.io/nvidia/tensorflow:25.01-tf2-py3

LABEL maintainer="MaSIF Team"
LABEL description="MaSIF - Molecular Surface Interaction Fingerprints (GPU with Blackwell support)"
LABEL version="3.1"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 1. Install system dependencies
# ============================================================================
# NGC container is based on Ubuntu 24.04, install additional dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    unzip \
    cmake \
    vim \
    build-essential \
    swig \
    libgl1 \
    libglu1-mesa \
    libxrender1 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    dssp \
    libboost-all-dev \
    libeigen3-dev \
    libgmp-dev \
    libgmpxx4ldbl \
    libmpfr-dev \
    libcgal-dev \
    libopenblas-dev \
    liblapack-dev \
    libtbb-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 2. Install additional Python packages (TensorFlow is pre-installed in NGC)
# ============================================================================
# NGC container already has TensorFlow, numpy, scipy, etc.
# Install additional packages needed by MaSIF
RUN pip install --no-cache-dir \
    biopython \
    scikit-learn \
    networkx \
    open3d \
    dask \
    packaging \
    plyfile \
    SBILib

# ============================================================================
# 3. GPU Environment Variables for Blackwell
# ============================================================================
# NGC container handles most CUDA setup, but we add MaSIF-specific settings
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV TF_ENABLE_ONEDNN_OPTS=0

# ============================================================================
# 5. Install MSMS (Molecular Surface Computation)
# ============================================================================
WORKDIR /opt
# Primary source often fails, try alternative sources
RUN mkdir msms && \
    (wget -q -O msms.tar.gz https://ccsb.scripps.edu/msms/download/933/ || \
     wget -q -O msms.tar.gz "https://github.com/openbabel/openbabel/raw/master/external/msms/msms_i86_64Linux2_2.6.1.tar.gz" || \
     wget -q -O msms.tar.gz http://mgltools.scripps.edu/downloads/tars/releases/MSMSRELEASE/REL2.6.1/msms_i86_64Linux2_2.6.1.tar.gz) && \
    tar -xzf msms.tar.gz -C msms && \
    rm msms.tar.gz && \
    chmod +x msms/msms.x86_64Linux2.2.6.1 && \
    ln -s /opt/msms/msms.x86_64Linux2.2.6.1 /opt/msms/msms

# Create pdb_to_xyzrn script
RUN cat > /opt/msms/pdb_to_xyzrn << 'SCRIPT'
#!/usr/bin/env python
import sys
import os
from Bio.PDB import PDBParser

radii = {"N": "1.540000", "O": "1.400000", "C": "1.740000", "H": "1.200000", "S": "1.800000", "P": "1.800000", "Z": "1.390000", "X": "0.770000"}
polarHydrogens = {"ALA": ["H"], "GLY": ["H"], "SER": ["H", "HG"], "THR": ["H", "HG1"], "LEU": ["H"], "ILE": ["H"], "VAL": ["H"], "ASN": ["H", "HD21", "HD22"], "GLN": ["H", "HE21", "HE22"], "ARG": ["H", "HH11", "HH12", "HH21", "HH22", "HE"], "HIS": ["H", "HD1", "HE2"], "TRP": ["H", "HE1"], "PHE": ["H"], "TYR": ["H", "HH"], "GLU": ["H"], "ASP": ["H"], "LYS": ["H", "HZ1", "HZ2", "HZ3"], "PRO": [], "CYS": ["H"], "MET": ["H"]}

def get_type(atom_name, res_name):
    if atom_name[0] in radii:
        return atom_name[0]
    elif atom_name[0:2] == "CL":
        return "C"
    else:
        return "X"

if len(sys.argv) < 2:
    print("Usage: pdb_to_xyzrn <pdb_file>")
    sys.exit(1)

pdb_file = sys.argv[1]
parser = PDBParser(QUIET=True)
structure = parser.get_structure("protein", pdb_file)

for model in structure:
    for chain in model:
        for residue in chain:
            res_name = residue.get_resname()
            for atom in residue:
                atom_name = atom.get_name()
                coords = atom.get_coord()
                atom_type = get_type(atom_name, res_name)
                radius = radii.get(atom_type, "1.500000")
                print("{:.6f} {:.6f} {:.6f} {} 1 {}_{}_{}".format(coords[0], coords[1], coords[2], radius, res_name, residue.get_id()[1], atom_name))
SCRIPT
RUN chmod +x /opt/msms/pdb_to_xyzrn

ENV MSMS_BIN=/opt/msms/msms
ENV PDB2XYZRN=/opt/msms/pdb_to_xyzrn

# ============================================================================
# 6. Install APBS (Poisson-Boltzmann Electrostatics)
# ============================================================================
# Download pre-built APBS 3.4.1 from GitHub (includes multivalue binary)
RUN curl -L -o /tmp/APBS-3.4.1.Linux.zip \
    "https://github.com/Electrostatics/apbs/releases/download/v3.4.1/APBS-3.4.1.Linux.zip" && \
    unzip -q /tmp/APBS-3.4.1.Linux.zip -d /opt && \
    rm /tmp/APBS-3.4.1.Linux.zip && \
    chmod +x /opt/APBS-3.4.1.Linux/bin/apbs && \
    chmod +x /opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue

ENV APBS_BIN=/opt/APBS-3.4.1.Linux/bin/apbs
ENV MULTIVALUE_BIN=/opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue

# ============================================================================
# 7. Install PDB2PQR
# ============================================================================
# Install PDB2PQR via pip (Python 3 version)
RUN pip install pdb2pqr

# Create wrapper script for compatibility with MaSIF's expected path
RUN mkdir -p /opt/pdb2pqr-linux-bin64-2.1.1 && \
    printf '#!/bin/bash\npdb2pqr30 "$@"\n' > /opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr && \
    chmod +x /opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr

ENV PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr

# ============================================================================
# 8. Install Reduce (Protonation)
# ============================================================================
RUN git clone https://github.com/rlabduke/reduce.git && \
    cd reduce && \
    mkdir build && cd build && \
    cmake .. && \
    make -j4 && \
    make install && \
    cd ../.. && \
    rm -rf reduce

# Download reduce het dictionary
RUN wget -q -O /usr/local/share/reduce_wwPDB_het_dict.txt \
    https://raw.githubusercontent.com/rlabduke/reduce/master/reduce_wwPDB_het_dict.txt

ENV REDUCE_HET_DICT=/usr/local/share/reduce_wwPDB_het_dict.txt
ENV PATH="/usr/local/bin:${PATH}"

# ============================================================================
# 9. Install PyMesh (Mesh Operations)
# ============================================================================
# PyMesh wheel was built in Stage 1 using Ubuntu 22.04 (GCC 11) with Python 3.12.
# NGC container uses Python 3.12.3 which is compatible.
WORKDIR /opt

# Copy PyMesh wheel from builder stage
COPY --from=pymesh-builder /tmp/pymesh2-*.whl /tmp/

# Install PyMesh into NGC's Python environment
# Patch pymesh's __init__.py to fix NumPy 2.0 compatibility
# (numpy.testing.Tester was removed in NumPy 2.0)
# Note: Must patch before importing since numpy.testing.Tester was removed in NumPy 2.0
RUN pip install /tmp/pymesh2-*.whl && \
    PYMESH_LOC=$(pip show pymesh2 | grep Location | awk '{print $2}') && \
    PYMESH_INIT="$PYMESH_LOC/pymesh/__init__.py" && \
    sed -i '/from numpy.testing import Tester/d' "$PYMESH_INIT" && \
    sed -i '/test = Tester().test/d' "$PYMESH_INIT" && \
    python -c "import pymesh; print('PyMesh installed successfully')" && \
    rm /tmp/pymesh2-*.whl

# ============================================================================
# 10. Clone MaSIF repository (modernized fork with Python 3/TF 2.x compatibility)
# ============================================================================
WORKDIR /
# Using modernized fork with all compatibility fixes pre-applied:
# - Python 3+ compatibility (time.clock -> time.perf_counter)
# - TensorFlow 2.x compatibility (compat.v1 mode)
# - NumPy/sklearn compatibility (.todense -> .toarray, np.int -> np.int64)
# - PDB2PQR 3.x compatibility (--ff=PARSE, --apbs-input= syntax)
# - RCSB server for PDB downloads
# - Removed hardcoded developer paths from shell scripts
RUN git clone https://github.com/laastos/masif.git

# Apply GPU configuration for MaSIF with NGC TensorFlow
# NGC container already has Blackwell support, we just need TF v1 compat mode
RUN cat > /masif/source/gpu_setup.py << 'SCRIPT'
import os
# Reduce TensorFlow logging verbosity
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import tensorflow.compat.v1 as tf
tf.disable_eager_execution()

# Configure GPU memory growth to avoid OOM errors
try:
    gpus = tf.config.experimental.list_physical_devices("GPU")
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"Configured {len(gpus)} GPU(s) with memory growth")
except Exception as e:
    pass  # GPU configuration may fail on CPU-only systems
SCRIPT

# Add import to MaSIF modules (prepend import statement)
RUN for f in /masif/source/masif_modules/MaSIF_site.py \
             /masif/source/masif_modules/MaSIF_ppi_search.py \
             /masif/source/masif_modules/MaSIF_ligand.py; do \
        if [ -f "$f" ]; then \
            sed -i '1i import gpu_setup  # GPU configuration for NGC TensorFlow' "$f"; \
        fi; \
    done

# Set Python path for MaSIF
ENV PYTHONPATH="/masif/source"

# ============================================================================
# 11. Create helper scripts for running MaSIF applications
# ============================================================================

# Create masif-site runner script
RUN cat > /usr/local/bin/masif-site << 'SCRIPT'
#!/bin/bash
cd /masif/data/masif_site
if [ "$1" == "prepare" ]; then
    shift
    ./data_prepare_one.sh "$@"
elif [ "$1" == "predict" ]; then
    shift
    ./predict_site.sh "$@"
elif [ "$1" == "color" ]; then
    shift
    ./color_site.sh "$@"
else
    echo "Usage: masif-site <prepare|predict|color> <PDB_CHAIN>"
    echo "Example: masif-site prepare 4ZQK_A"
fi
SCRIPT
RUN chmod +x /usr/local/bin/masif-site

# Create masif-search runner script
RUN cat > /usr/local/bin/masif-search << 'SCRIPT'
#!/bin/bash
cd /masif/data/masif_ppi_search
if [ "$1" == "prepare" ]; then
    shift
    ./data_prepare_one.sh "$@"
elif [ "$1" == "descriptors" ]; then
    shift
    ./compute_descriptors.sh "$@"
elif [ "$1" == "gif" ]; then
    shift
    ./compute_gif_descriptors.sh "$@"
else
    echo "Usage: masif-search <prepare|descriptors|gif> <PDB_CHAIN>"
    echo "Example: masif-search prepare 4ZQK_A_B"
fi
SCRIPT
RUN chmod +x /usr/local/bin/masif-search

# Create masif-ligand runner script
RUN cat > /usr/local/bin/masif-ligand << 'SCRIPT'
#!/bin/bash
cd /masif/data/masif_ligand
if [ "$1" == "prepare" ]; then
    shift
    ./data_prepare_one.sh "$@"
elif [ "$1" == "evaluate" ]; then
    ./evaluate_test.sh
else
    echo "Usage: masif-ligand <prepare|evaluate> [PDB_CHAIN]"
    echo "Example: masif-ligand prepare 1ABC_A_ADP"
fi
SCRIPT
RUN chmod +x /usr/local/bin/masif-ligand

# Create masif-peptides runner script
RUN cat > /usr/local/bin/masif-peptides << 'SCRIPT'
#!/bin/bash
cd /masif/data/masif_peptides
if [ "$1" == "extract" ]; then
    shift
    ./data_extract_helix_one.sh "$@"
elif [ "$1" == "precompute" ]; then
    shift
    ./data_precompute_patches_one.sh "$@"
elif [ "$1" == "predict" ]; then
    shift
    ./predict_site.sh "$@"
else
    echo "Usage: masif-peptides <extract|precompute|predict> <PDB_CHAIN>"
    echo "Example: masif-peptides extract 1ABC_A"
fi
SCRIPT
RUN chmod +x /usr/local/bin/masif-peptides

# ============================================================================
# 12. Set working directory and default command
# ============================================================================
WORKDIR /masif

# Expose common ports (for Jupyter notebooks if needed)
EXPOSE 8888

CMD ["bash"]
