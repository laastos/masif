# MaSIF Docker Container & Documentation Update Plan

## Status: COMPLETED (CPU-Only)

This plan has been implemented as a **CPU-only** Docker container. GPU support was removed due to compatibility issues with modern NVIDIA GPUs (Blackwell architecture, CUDA 12+).

**For future GPU support**, see `CUDA_UPDATE_PLAN.md` which contains a detailed migration plan for TensorFlow 2.x with CUDA 12.6.

---

## Objective

Create a comprehensive Docker container that includes ALL MaSIF tools (site, search, ligand, peptides) with pre-trained models, and update documentation to cover all features.

---

## Part 1: Dockerfile (COMPLETED)

### Location

File: `docker/Dockerfile`

### Base Image

Ubuntu 18.04 (CPU-only):

```dockerfile
FROM ubuntu:18.04
```

### Dependencies Installed

#### System Packages

- wget, git, unzip, cmake, vim
- libgl1-mesa-glx, libglu1-mesa, libxrender1, libxcursor1, libxft2, libxinerama1
- dssp, libboost-all-dev, libeigen3-dev, libgmp-dev, libmpfr-dev, libcgal-dev
- libopenblas-dev, liblapack-dev
- python2.7, python2.7-dev, python-pip
- python3.6, python3.6-dev, python3-pip

#### Python 3.6 Packages

- tensorflow==1.12.0 (CPU version)
- numpy, scipy, matplotlib, ipython
- biopython==1.73
- scikit-learn, networkx
- open3d==0.8.0.0
- dask==1.2.2, packaging, plyfile
- pdb2pqr

#### Python 2.7 Packages (for MaSIF-ligand)

- numpy, scipy
- SBI library (from GitHub with README.rst fix)

#### External Scientific Tools

| Tool | Version | Installation Method |
|------|---------|---------------------|
| APBS | system | Ubuntu apt repository |
| MSMS | 2.6.1 | Downloaded from Scripps CCSB |
| PDB2PQR | 3.x | pip (with wrapper script) |
| Reduce | latest | Built from source (GitHub) |
| PyMesh | latest | pip (pymesh2) |

### Environment Variables

```bash
ENV MSMS_BIN=/opt/msms/msms
ENV PDB2XYZRN=/opt/msms/pdb_to_xyzrn
ENV APBS_BIN=/opt/APBS-1.5-linux64/bin/apbs
ENV MULTIVALUE_BIN=/opt/APBS-1.5-linux64/share/apbs/tools/bin/multivalue
ENV PDB2PQR_BIN=/opt/pdb2pqr-linux-bin64-2.1.1/pdb2pqr
ENV REDUCE_HET_DICT=/usr/local/share/reduce_wwPDB_het_dict.txt
ENV PYTHONPATH=/masif/source
```

### Pre-trained Models Included (~55MB total)

| Application | Model | Size |
|-------------|-------|------|
| masif_site | all_feat_3l | 2.5M |
| masif_ligand | all_feat | 11M |
| masif_ppi_search | sc05/all_feat | 6.6M |
| masif_ppi_search_ub | sc05/all_feat | 6.6M |
| masif_pdl1_benchmark | sc05/all_feat + all_feat_3l | 9.1M |
| masif_peptides | sc05/all_feat + all_feat_3l | 19M |

---

## Part 2: Documentation Updates (COMPLETED)

### Files Updated

| File | Changes |
|------|---------|
| `docker/README.md` | Created with build/run instructions (CPU-only) |
| `docker_tutorial.md` | Added MaSIF-ligand, peptides, GIF, PyMOL, comparison sections |

### Sections Added to docker_tutorial.md

1. **MaSIF-ligand** - Ligand binding pocket prediction (ADP, COA, FAD, HEM, NAD, NAP, SAM)
2. **MaSIF-peptides** - Helical peptide analysis
3. **GIF Descriptors** - Fast alternative to neural network descriptors
4. **Comparison/Benchmark Tools** - ZDOCK, PatchDock, ZRANK, SPPIDER comparisons
5. **PyMOL Plugin** - Detailed visualization features and color schemes
6. **Dockerfile** - Building from source instructions

### Sections Removed (GPU not supported)

- GPU Installation section
- GPU Usage section
- TensorFlow GPU configuration

---

## Part 3: Helper Scripts (COMPLETED)

The container includes wrapper scripts in `/usr/local/bin/`:

| Script | Usage |
|--------|-------|
| `masif-site` | `masif-site prepare|predict|color <PDB_CHAIN>` |
| `masif-search` | `masif-search prepare|descriptors|gif <PDB_CHAIN>` |
| `masif-ligand` | `masif-ligand prepare|evaluate <PDB_CHAIN_LIGAND>` |
| `masif-peptides` | `masif-peptides extract|precompute|predict <PDB_CHAIN>` |

---

## Build & Run

### Build

```bash
cd docker/
docker build -t masif .
```

### Run

```bash
docker run -it masif
```

### With Volume Mounting

```bash
docker run -it -v /path/to/data:/data masif
```

---

## Known Issues & Workarounds

### 1. SBI Library (FIXED)

The upstream SBI repository has a broken setup.py (missing README.rst). Fixed by cloning, creating the file, then installing.

### 2. MSMS Download (FIXED)

Primary download sources often fail. Using multiple fallback sources (Scripps CCSB, GitHub mirrors).

### 3. APBS/PDB2PQR Downloads (FIXED)

GitHub releases and SourceForge links unreliable. Using Ubuntu apt for APBS and pip for PDB2PQR.

### 4. PDB Download Server (FIXED)

The default wwpdb.org FTP server in BioPython's PDBList is unreliable, causing "Desired structure doesn't exist" errors even for valid PDB IDs. Fixed by patching `00-pdb_download.py` to use `https://files.rcsb.org` instead.

### 5. Hardcoded Developer Paths (FIXED)

Shell scripts contained hardcoded paths from the original development environment (`/work/upcorreia/`, `/home/gainza/`). Fixed by removing these source commands from all `.sh` files.

### 6. PDB2PQR 3.x Compatibility (FIXED)

pdb2pqr 3.x changed command-line syntax:
- `--ff=parse` → `--ff=PARSE` (uppercase)
- `--apbs-input pdbname filename` → `--apbs-input=filename.in pdbname filename`

Fixed by patching `computeAPBS.py` to use the new syntax.

---

## Testing Checklist

After building the Docker image, run these tests to verify all components work correctly.

### Quick Verification (Run inside container)

```bash
docker run -it masif
```

### 1. Environment Tests

```bash
# Test Python versions
python2 --version    # Should show Python 2.7.x
python3 --version    # Should show Python 3.6.x

# Test TensorFlow
python3 -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
# Expected: TensorFlow: 1.12.0

# Test PyMesh
python3 -c "import pymesh; print('PyMesh:', pymesh.__version__)"

# Test Open3D
python3 -c "import open3d; print('Open3D:', open3d.__version__)"

# Test BioPython
python3 -c "from Bio.PDB import PDBParser; print('BioPython OK')"

# Test SBI library (Python 2.7)
python2 -c "from SBI.structure import PDB; print('SBI OK')"
```

### 2. External Tools Tests

```bash
# Test MSMS
$MSMS_BIN -h 2>&1 | head -1
# Expected: MSMS 2.6.1 started on...

# Test APBS
$APBS_BIN --version
# Expected: APBS version info

# Test PDB2PQR
$PDB2PQR_BIN --help | head -3
# Expected: usage information

# Test Reduce
reduce -h 2>&1 | head -3
# Expected: reduce help info

# Test multivalue
$MULTIVALUE_BIN 2>&1 | head -1
# Expected: usage info or "multivalue not available"
```

### 3. MaSIF-site Test

```bash
cd /masif/data/masif_site

# Data preparation (downloads PDB, computes surface, ~2 min)
./data_prepare_one.sh 4ZQK_A

# Run prediction (~30 sec)
./predict_site.sh 4ZQK_A

# Generate colored surface
./color_site.sh 4ZQK_A

# Verify output files exist
ls -la output/all_feat_3l/pred_data/pred_4ZQK_A.npy
ls -la output/all_feat_3l/pred_surfaces/4ZQK_A.ply
```

### 4. MaSIF-search Test

```bash
cd /masif/data/masif_ppi_search

# Data preparation for a protein pair (~3 min)
./data_prepare_one.sh 4ZQK_A_B

# Compute neural network descriptors
./compute_descriptors.sh 4ZQK_A_B

# Verify output
ls -la descriptors/
```

### 5. MaSIF-ligand Test (Optional - requires Python 2.7)

```bash
cd /masif/data/masif_ligand

# Test data preparation (requires SBI library)
./data_prepare_one.sh 1MBN_A_HEM

# Verify biological assembly was generated
ls -la data_preparation/00-raw_pdbs/
```

### 6. Helper Scripts Test

```bash
# Test helper commands are accessible
which masif-site
which masif-search
which masif-ligand
which masif-peptides

# Test help output
masif-site
masif-search
masif-ligand
masif-peptides
```

### 7. Full Pipeline Test Script

Create and run this test script inside the container:

```bash
#!/bin/bash
# Save as /tmp/test_masif.sh and run with: bash /tmp/test_masif.sh

echo "=== MaSIF Docker Container Test Suite ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

echo "1. Testing Python environments..."
python2 --version 2>/dev/null && pass "Python 2.7" || fail "Python 2.7"
python3 --version 2>/dev/null && pass "Python 3.6" || fail "Python 3.6"

echo ""
echo "2. Testing Python packages..."
python3 -c "import tensorflow" 2>/dev/null && pass "TensorFlow" || fail "TensorFlow"
python3 -c "import pymesh" 2>/dev/null && pass "PyMesh" || fail "PyMesh"
python3 -c "import open3d" 2>/dev/null && pass "Open3D" || fail "Open3D"
python3 -c "from Bio.PDB import PDBParser" 2>/dev/null && pass "BioPython" || fail "BioPython"
python2 -c "from SBI.structure import PDB" 2>/dev/null && pass "SBI (Python 2)" || fail "SBI (Python 2)"

echo ""
echo "3. Testing external tools..."
[ -x "$MSMS_BIN" ] && pass "MSMS binary" || fail "MSMS binary"
[ -x "$APBS_BIN" ] && pass "APBS binary" || fail "APBS binary"
[ -x "$PDB2PQR_BIN" ] && pass "PDB2PQR binary" || fail "PDB2PQR binary"
which reduce >/dev/null 2>&1 && pass "Reduce" || fail "Reduce"

echo ""
echo "4. Testing environment variables..."
[ -n "$PYTHONPATH" ] && pass "PYTHONPATH set" || fail "PYTHONPATH not set"
[ -n "$MSMS_BIN" ] && pass "MSMS_BIN set" || fail "MSMS_BIN not set"
[ -n "$APBS_BIN" ] && pass "APBS_BIN set" || fail "APBS_BIN not set"

echo ""
echo "5. Testing MaSIF source..."
[ -d "/masif/source" ] && pass "MaSIF source directory" || fail "MaSIF source directory"
[ -f "/masif/source/default_config/masif_opts.py" ] && pass "MaSIF config" || fail "MaSIF config"

echo ""
echo "=== Test Suite Complete ==="
```

### Expected Test Results

| Test | Expected Result |
|------|-----------------|
| Python 2.7 | Version 2.7.x available |
| Python 3.6 | Version 3.6.x available |
| TensorFlow | Version 1.12.0 |
| PyMesh | Importable, version displayed |
| Open3D | Version 0.8.0.0 |
| BioPython | PDBParser importable |
| SBI | PDB class importable (Python 2) |
| MSMS | Executable, shows version |
| APBS | Executable, shows version |
| PDB2PQR | Executable, shows help |
| Reduce | Executable, shows help |
| MaSIF-site | Prediction completes, PLY file generated |
| MaSIF-search | Descriptors computed |

---

## Future GPU Support

For GPU support with modern NVIDIA GPUs (Blackwell, CUDA 12+), see `CUDA_UPDATE_PLAN.md` which outlines:

- Migration from TensorFlow 1.12 to TensorFlow 2.16
- CUDA 12.6 base image
- tf.compat.v1 wrapper for backward compatibility
- Updates to 15+ Python files for TF2 compatibility

---

## Technical Notes

### SBI Library

- GitHub: https://github.com/structuralbioinformatics/SBI
- Requires Python 2.7
- Used for: `PDB.apply_biomolecule_matrices()` to generate biological assemblies
- Only needed for MaSIF-ligand data preparation

### Model Checkpoint Format

- TensorFlow 1.x format: `.meta`, `.data-00000-of-00001`, `.index` files
- All models use geodesic convolution architecture
- Feature mask: `[1.0, 1.0, 1.0, 1.0, 1.0]` for 5 surface features
