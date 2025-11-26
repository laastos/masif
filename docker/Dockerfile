# MaSIF Docker Container (CPU-Only)
# Includes all tools: MaSIF-site, MaSIF-search, MaSIF-ligand, MaSIF-peptides
#
# Build: docker build -t masif .
# Run:   docker run -it masif

FROM ubuntu:20.04

LABEL maintainer="MaSIF Team"
LABEL description="MaSIF - Molecular Surface Interaction Fingerprints"
LABEL version="2.0"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 1. Install system dependencies
# ============================================================================
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    unzip \
    cmake \
    vim \
    build-essential \
    swig \
    libgl1-mesa-glx \
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
    python2.7 \
    python2.7-dev \
    python3.8 \
    python3.8-dev \
    python3-pip \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 2.7 (python-pip not available in Ubuntu 20.04)
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o /tmp/get-pip.py && \
    python2.7 /tmp/get-pip.py && \
    rm /tmp/get-pip.py

# Set Python alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# ============================================================================
# 2. Install Python 2.7 packages (required for MaSIF-ligand SBI library)
# ============================================================================
# Use python2.7 -m pip to ensure we're using Python 2.7's pip, not Python 3's
# Note: Ubuntu 20.04 uses python2.7, not python2
RUN python2.7 -m pip install --upgrade pip setuptools && \
    python2.7 -m pip install \
    numpy \
    scipy \
    biopython==1.76

# Install SBI library for biological assembly generation (MaSIF-ligand)
# PyPI versions 0.2.1 and 0.2.2 support Python 2.7 (GitHub master has been updated to Python 3 only)
# Install from PyPI, not GitHub
RUN python2.7 -m pip install -v 'StrBioInfo==0.2.2' && \
    cd / && \
    python2.7 -c "from SBI.structure import PDB; print('SBI installed successfully')"

# ============================================================================
# 3. Install Python 3.8 packages
# ============================================================================
# Note: TensorFlow 2.x with compat.v1 mode for Python 3.8 compatibility
# Pin setuptools<71 to avoid strict version parsing issues with some packages
RUN pip3 install --upgrade "pip<24" "setuptools<71" && \
    pip3 install \
    tensorflow==2.4.0 \
    numpy \
    scipy \
    matplotlib \
    ipython \
    biopython==1.79 \
    scikit-learn \
    networkx \
    open3d==0.13.0 \
    dask \
    packaging \
    plyfile

# ============================================================================
# 4. Install MSMS (Molecular Surface Computation)
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
RUN echo '#!/usr/bin/env python\n\
import sys\n\
import os\n\
from Bio.PDB import PDBParser\n\
\n\
radii = {"N": "1.540000", "O": "1.400000", "C": "1.740000", "H": "1.200000", "S": "1.800000", "P": "1.800000", "Z": "1.390000", "X": "0.770000"}\n\
polarHydrogens = {"ALA": ["H"], "GLY": ["H"], "SER": ["H", "HG"], "THR": ["H", "HG1"], "LEU": ["H"], "ILE": ["H"], "VAL": ["H"], "ASN": ["H", "HD21", "HD22"], "GLN": ["H", "HE21", "HE22"], "ARG": ["H", "HH11", "HH12", "HH21", "HH22", "HE"], "HIS": ["H", "HD1", "HE2"], "TRP": ["H", "HE1"], "PHE": ["H"], "TYR": ["H", "HH"], "GLU": ["H"], "ASP": ["H"], "LYS": ["H", "HZ1", "HZ2", "HZ3"], "PRO": [], "CYS": ["H"], "MET": ["H"]}\n\
\n\
def get_type(atom_name, res_name):\n\
    if atom_name[0] in radii:\n\
        return atom_name[0]\n\
    elif atom_name[0:2] == "CL":\n\
        return "C"\n\
    else:\n\
        return "X"\n\
\n\
if len(sys.argv) < 2:\n\
    print("Usage: pdb_to_xyzrn <pdb_file>")\n\
    sys.exit(1)\n\
\n\
pdb_file = sys.argv[1]\n\
parser = PDBParser(QUIET=True)\n\
structure = parser.get_structure("protein", pdb_file)\n\
\n\
for model in structure:\n\
    for chain in model:\n\
        for residue in chain:\n\
            res_name = residue.get_resname()\n\
            for atom in residue:\n\
                atom_name = atom.get_name()\n\
                coords = atom.get_coord()\n\
                atom_type = get_type(atom_name, res_name)\n\
                radius = radii.get(atom_type, "1.500000")\n\
                print("{:.6f} {:.6f} {:.6f} {} 1 {}_{}_{}".format(coords[0], coords[1], coords[2], radius, res_name, residue.get_id()[1], atom_name))\n\
' > /opt/msms/pdb_to_xyzrn && chmod +x /opt/msms/pdb_to_xyzrn

ENV MSMS_BIN=/opt/msms/msms
ENV PDB2XYZRN=/opt/msms/pdb_to_xyzrn

# ============================================================================
# 5. Install APBS (Poisson-Boltzmann Electrostatics)
# ============================================================================
# Download pre-built APBS 3.4.1 from GitHub (includes multivalue binary)
# APBS 1.5 on SourceForge is no longer reliably available
RUN curl -L -o /tmp/APBS-3.4.1.Linux.zip \
    "https://github.com/Electrostatics/apbs/releases/download/v3.4.1/APBS-3.4.1.Linux.zip" && \
    unzip -q /tmp/APBS-3.4.1.Linux.zip -d /opt && \
    rm /tmp/APBS-3.4.1.Linux.zip && \
    chmod +x /opt/APBS-3.4.1.Linux/bin/apbs && \
    chmod +x /opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue

ENV APBS_BIN=/opt/APBS-3.4.1.Linux/bin/apbs
ENV MULTIVALUE_BIN=/opt/APBS-3.4.1.Linux/share/apbs/tools/bin/multivalue

# ============================================================================
# 6. Install PDB2PQR
# ============================================================================
# Install PDB2PQR via pip (Python 3 version)
RUN pip3 install pdb2pqr

# Create wrapper script for compatibility with MaSIF's expected path
RUN mkdir -p /opt/pdb2pqr-linux-bin64-2.1.1 && \
    echo '#!/bin/bash\npdb2pqr30 "$@"' > /opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr && \
    chmod +x /opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr

ENV PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr

# ============================================================================
# 7. Install Reduce (Protonation)
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
# 8. Install PyMesh (Mesh Operations)
# ============================================================================
# Build PyMesh using its official build system and install via pip
# Skip requirements.txt (numpy/scipy already installed, nose is only for testing)
WORKDIR /opt
ENV PYMESH_PATH=/opt/PyMesh
RUN git clone --depth 1 https://github.com/PyMesh/PyMesh.git && \
    cd PyMesh && \
    git submodule update --init --recursive && \
    python3 setup.py bdist_wheel && \
    pip3 install dist/pymesh2-*.whl && \
    python3 -c "import pymesh; print('PyMesh installed successfully')" && \
    cd / && rm -rf /opt/PyMesh

# ============================================================================
# 9. Clone MaSIF repository (modernized fork with Python 3.8+/TF 2.x compatibility)
# ============================================================================
WORKDIR /
# Using modernized fork with all compatibility fixes pre-applied:
# - Python 3.8+ compatibility (time.clock -> time.perf_counter)
# - TensorFlow 2.x compatibility (compat.v1 mode)
# - NumPy/sklearn compatibility (.todense -> .toarray, np.int -> np.int64)
# - PDB2PQR 3.x compatibility (--ff=PARSE, --apbs-input= syntax)
# - RCSB server for PDB downloads
# - Removed hardcoded developer paths from shell scripts
RUN git clone https://github.com/laastos/masif.git

# Set Python path for MaSIF
ENV PYTHONPATH="/masif/source"

# ============================================================================
# 10. Create helper scripts for running MaSIF applications
# ============================================================================

# Create masif-site runner script
RUN echo '#!/bin/bash\n\
cd /masif/data/masif_site\n\
if [ "$1" == "prepare" ]; then\n\
    shift\n\
    ./data_prepare_one.sh "$@"\n\
elif [ "$1" == "predict" ]; then\n\
    shift\n\
    ./predict_site.sh "$@"\n\
elif [ "$1" == "color" ]; then\n\
    shift\n\
    ./color_site.sh "$@"\n\
else\n\
    echo "Usage: masif-site <prepare|predict|color> <PDB_CHAIN>"\n\
    echo "Example: masif-site prepare 4ZQK_A"\n\
fi\n\
' > /usr/local/bin/masif-site && chmod +x /usr/local/bin/masif-site

# Create masif-search runner script
RUN echo '#!/bin/bash\n\
cd /masif/data/masif_ppi_search\n\
if [ "$1" == "prepare" ]; then\n\
    shift\n\
    ./data_prepare_one.sh "$@"\n\
elif [ "$1" == "descriptors" ]; then\n\
    shift\n\
    ./compute_descriptors.sh "$@"\n\
elif [ "$1" == "gif" ]; then\n\
    shift\n\
    ./compute_gif_descriptors.sh "$@"\n\
else\n\
    echo "Usage: masif-search <prepare|descriptors|gif> <PDB_CHAIN>"\n\
    echo "Example: masif-search prepare 4ZQK_A_B"\n\
fi\n\
' > /usr/local/bin/masif-search && chmod +x /usr/local/bin/masif-search

# Create masif-ligand runner script
RUN echo '#!/bin/bash\n\
cd /masif/data/masif_ligand\n\
if [ "$1" == "prepare" ]; then\n\
    shift\n\
    ./data_prepare_one.sh "$@"\n\
elif [ "$1" == "evaluate" ]; then\n\
    ./evaluate_test.sh\n\
else\n\
    echo "Usage: masif-ligand <prepare|evaluate> [PDB_CHAIN]"\n\
    echo "Example: masif-ligand prepare 1ABC_A_ADP"\n\
fi\n\
' > /usr/local/bin/masif-ligand && chmod +x /usr/local/bin/masif-ligand

# Create masif-peptides runner script
RUN echo '#!/bin/bash\n\
cd /masif/data/masif_peptides\n\
if [ "$1" == "extract" ]; then\n\
    shift\n\
    ./data_extract_helix_one.sh "$@"\n\
elif [ "$1" == "precompute" ]; then\n\
    shift\n\
    ./data_precompute_patches_one.sh "$@"\n\
elif [ "$1" == "predict" ]; then\n\
    shift\n\
    ./predict_site.sh "$@"\n\
else\n\
    echo "Usage: masif-peptides <extract|precompute|predict> <PDB_CHAIN>"\n\
    echo "Example: masif-peptides extract 1ABC_A"\n\
fi\n\
' > /usr/local/bin/masif-peptides && chmod +x /usr/local/bin/masif-peptides

# ============================================================================
# 11. Set working directory and default command
# ============================================================================
WORKDIR /masif

# Expose common ports (for Jupyter notebooks if needed)
EXPOSE 8888

CMD ["bash"]
