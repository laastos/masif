# Troubleshooting Guide

Solutions to common issues encountered when using MaSIF.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Preprocessing Errors](#preprocessing-errors)
- [Neural Network Issues](#neural-network-issues)
- [Memory and Performance](#memory-and-performance)
- [Docker Issues](#docker-issues)
- [Visualization Issues](#visualization-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### Python Import Errors

#### ImportError: No module named 'pymesh'

**Cause**: PyMesh not properly installed.

**Solution**:
```bash
cd $PYMESH_PATH
python setup.py clean
python setup.py build
python setup.py install

# Verify installation
python -c "import pymesh; print(pymesh.__version__)"
```

#### ImportError: No module named 'default_config'

**Cause**: Python path not set correctly.

**Solution**:
```bash
export masif_root=$(git rev-parse --show-toplevel)
export PYTHONPATH=$PYTHONPATH:$masif_root/source

# Verify
python -c "from default_config.masif_opts import masif_opts; print('OK')"
```

#### ImportError: No module named 'tensorflow'

**Cause**: TensorFlow not installed or wrong version.

**Solution**:
```bash
# Install TensorFlow with GPU support
pip install "tensorflow[and-cuda]==2.16.2"

# Or CPU-only
pip install tensorflow==2.16.2

# Verify
python -c "import tensorflow as tf; print(tf.__version__)"
```

### External Tool Errors

#### MSMS: Command not found

**Cause**: MSMS binary not in path or not executable.

**Solution**:
```bash
# Check the path
echo $MSMS_BIN
ls -la $MSMS_BIN

# Make executable
chmod +x $MSMS_BIN
chmod +x $PDB2XYZRN

# Test
$MSMS_BIN -h
```

#### APBS: Unable to open file

**Cause**: APBS path incorrect or missing dependencies.

**Solution**:
```bash
# Verify path
ls -la $APBS_BIN

# Check dependencies
ldd $APBS_BIN

# Test
$APBS_BIN --version
```

#### Reduce: reduce_wwPDB_het_dict.txt not found

**Cause**: REDUCE_HET_DICT environment variable not set.

**Solution**:
```bash
# Find the file
find /path/to/reduce -name "reduce_wwPDB_het_dict.txt"

# Set the variable
export REDUCE_HET_DICT=/path/to/reduce/reduce_wwPDB_het_dict.txt

# Verify
ls -la $REDUCE_HET_DICT
```

---

## Preprocessing Errors

### PDB Download Failures

#### HTTPError: 404 Not Found

**Cause**: PDB ID does not exist or was superseded.

**Solution**:
```bash
# Check if PDB exists
wget https://files.rcsb.org/download/XXXX.pdb

# Use the superseding entry if applicable
# Check https://www.rcsb.org for the correct ID
```

#### SSL Certificate Error

**Cause**: System SSL certificates outdated.

**Solution**:
```bash
# Update certificates
sudo apt-get update
sudo apt-get install ca-certificates

# Or use HTTP instead of HTTPS in the download script
```

### Surface Computation Failures

#### MSMS: No output generated

**Cause**: Invalid PDB file or atoms too close together.

**Solution**:
```python
# Check PDB file validity
from Bio.PDB import PDBParser
parser = PDBParser(QUIET=True)
structure = parser.get_structure('test', 'protein.pdb')
print(f"Chains: {[c.id for c in structure.get_chains()]}")
print(f"Atoms: {len(list(structure.get_atoms()))}")
```

Alternative: Try with different parameters:
```bash
$MSMS_BIN -if input.xyzrn -of output -probe_radius 1.5 -density 1.0
```

#### MSMS: Degenerate triangles error

**Cause**: Surface has problematic geometry (common warning).

**Solution**: This is usually a warning, not an error. The fix_mesh function handles this:
```python
from triangulation.fixmesh import fix_mesh
import pymesh

mesh = pymesh.form_mesh(vertices, faces)
regular_mesh = fix_mesh(mesh, 1.0)  # Regularize to 1.0 Å
```

### Electrostatics Failures

#### APBS: pdb2pqr failed

**Cause**: PDB2PQR cannot process the input file.

**Solution**:
```bash
# Test PDB2PQR directly
$PDB2PQR_BIN --ff=PARSE protein.pdb protein.pqr

# Common fixes:
# 1. Remove HETATM records
grep -v "^HETATM" protein.pdb > protein_clean.pdb

# 2. Add missing atoms
# Use external tools like Modeller or Swiss-Model
```

#### APBS: Grid dimensions too large

**Cause**: Protein too large for default grid.

**Solution**: Increase grid limits in APBS input file or split into domains.

### Precomputation Failures

#### MDS timeout or hang

**Cause**: Protein too large, MDS computation takes too long.

**Solution**:
```python
# Reduce the number of vertices by increasing mesh resolution
masif_opts["mesh_res"] = 1.5  # Instead of 1.0

# Or process smaller domains separately
```

#### Memory error during geodesic computation

**Cause**: Insufficient memory for distance matrices.

**Solution**:
```bash
# Increase available memory
ulimit -v unlimited

# Or reduce protein size
# Or use cluster with more memory per node
```

---

## Neural Network Issues

### Training Failures

#### CUDA out of memory

**Cause**: Batch size too large for GPU memory.

**Solution**:
```python
# Reduce batch size in training script
batch_size = 16  # Instead of 32 or 64

# Or use memory growth (set in environment or code)
import os
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# Or in TensorFlow:
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

#### GPU not detected

**Cause**: CUDA not installed or TensorFlow not built with GPU support.

**Solution**:
```bash
# Check if GPU is visible
nvidia-smi

# Check TensorFlow GPU support
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Expected output: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]

# If empty, ensure tensorflow[and-cuda] was installed:
pip install "tensorflow[and-cuda]==2.16.2"
```

#### CUDA version mismatch

**Cause**: TensorFlow expects different CUDA version.

**Solution**:
```bash
# Check CUDA version
nvcc --version

# For TensorFlow 2.16.2, CUDA 12.x is required
# Install nvidia-container-toolkit for Docker GPU support
sudo apt-get install nvidia-container-toolkit
sudo systemctl restart docker
```

#### NaN loss values

**Cause**: Learning rate too high or data issues.

**Solution**:
```python
# Reduce learning rate
learning_rate = 0.0001  # Instead of 0.001

# Check for NaN in input data
import numpy as np
data = np.load('precomputation/protein/p1_input_feat.npy')
print(f"NaN count: {np.isnan(data).sum()}")
print(f"Inf count: {np.isinf(data).sum()}")
```

#### Model not improving

**Cause**: Various reasons including data imbalance.

**Solution**:
1. Check training/validation split
2. Ensure positive/negative balance
3. Try different random seeds
4. Increase training duration

### Prediction Failures

#### Empty predictions

**Cause**: Precomputed data not found.

**Solution**:
```bash
# Verify precomputation exists
ls data_preparation/04a-precomputation_9A/precomputation/4ZQK_A/

# Should contain:
# p1_rho_wrt_center.npy
# p1_theta_wrt_center.npy
# p1_input_feat.npy
# etc.
```

#### Model checkpoint not found

**Cause**: Model not trained or path incorrect.

**Solution**:
```bash
# Check model directory
ls nn_models/all_feat_3l/model_data/

# Should contain checkpoint files
# If empty, retrain or download pre-trained model
```

---

## Memory and Performance

### Out of Memory Errors

#### During preprocessing

```bash
# Process fewer proteins at a time
for pdb in $(head -10 lists/training.txt); do
    ./data_prepare_one.sh $pdb
done

# Or increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### During training

```python
# Use smaller batch sizes
batch_size = 8

# Enable memory growth
config = tf.ConfigProto()
config.gpu_options.allow_growth = True

# Limit GPU memory
config.gpu_options.per_process_gpu_memory_fraction = 0.7
```

### Slow Performance

#### Preprocessing bottlenecks

| Bottleneck | Solution |
|------------|----------|
| APBS (slowest) | Use cluster parallelization |
| MDS computation | Reduce mesh resolution |
| Disk I/O | Use SSD storage |

#### Training speed

| Issue | Solution |
|-------|----------|
| CPU training | Use GPU (10-100x faster) |
| Slow data loading | Use TFRecords (MaSIF-ligand) |
| I/O bottleneck | Cache data in memory |

### Disk Space Issues

#### Precomputation uses too much space

**Cause**: Overlapping patches create redundant data.

**Solution**:
```bash
# Clean up temporary files
rm -rf $masif_opts["tmp_dir"]/*

# Remove intermediate files
rm data_preparation/00-raw_pdbs/*.pdb  # Keep only processed data

# Use compressed storage
gzip data_preparation/04a-precomputation_9A/precomputation/*/*.npy
```

---

## Docker Issues

### Container Won't Start

#### Permission denied

**Cause**: Docker not running or user not in docker group.

**Solution**:
```bash
# Start docker daemon
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### GPU not accessible

**Cause**: nvidia-container-toolkit not installed.

**Solution**:
```bash
# Install nvidia-container-toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test
docker run --gpus all nvidia/cuda:10.0-base nvidia-smi
```

### Docker Volume Issues

#### Files not accessible

**Cause**: Volume mount path incorrect.

**Solution**:
```bash
# Use absolute paths
docker run -it -v /absolute/path/to/data:/data pablogainza/masif

# Check permissions
ls -la /path/to/data
```

#### Changes not persisted

**Cause**: Files created inside container without volume mount.

**Solution**:
```bash
# Mount output directory
docker run -it \
    -v /path/to/input:/masif/data/masif_site/data_preparation/00-raw_pdbs \
    -v /path/to/output:/masif/data/masif_site/output \
    pablogainza/masif
```

---

## Visualization Issues

### PyMOL Plugin

#### Plugin not loading

**Cause**: Plugin not installed correctly.

**Solution**:
1. Open PyMOL → Plugin → Plugin Manager
2. Go to "Settings" tab
3. Add directory: `masif/source/masif_pymol_plugin/`
4. Restart PyMOL

#### loadply command not found

**Cause**: Plugin initialization failed.

**Solution**:
```python
# In PyMOL, try manual import
import sys
sys.path.append('/path/to/masif/source/masif_pymol_plugin')
from loadply import loadply
```

#### Surface colors not showing

**Cause**: Wrong object selected or attribute missing.

**Solution**:
```
# In PyMOL
# List all objects
get_names

# Enable the interface object
enable iface_4ZQK_A
disable mesh_4ZQK_A

# Check attributes
iterate 4ZQK_A, print(name, b)
```

### PLY File Issues

#### Empty or corrupted PLY file

**Cause**: Preprocessing failed silently.

**Solution**:
```python
# Check PLY file
from input_output.read_ply import read_ply

try:
    mesh = read_ply('protein.ply')
    print(f"Vertices: {len(mesh['vertices'])}")
    print(f"Faces: {len(mesh['faces'])}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Getting Help

### Before Asking for Help

1. **Check this guide**: Search for your error message
2. **Check GitHub Issues**: Your problem may already be solved
3. **Update MaSIF**: `git pull` to get latest fixes
4. **Try Docker**: Rules out installation issues

### Reporting Issues

When opening a GitHub issue, include:

```markdown
## Environment
- OS: Ubuntu 20.04
- Python: 3.6.9
- TensorFlow: 1.9.0
- GPU: NVIDIA RTX 3080 (if applicable)
- Docker: Yes/No

## Error Message
```
[Full error traceback]
```

## Steps to Reproduce
1. cd data/masif_site
2. ./data_prepare_one.sh 4ZQK_A
3. [Error occurs]

## Expected Behavior
[What should happen]

## Additional Context
[Any other relevant information]
```

### Resources

- **GitHub Issues**: https://github.com/LPDI-EPFL/masif/issues
- **Paper**: https://doi.org/10.1038/s41592-019-0666-6
- **Precomputed Data**: https://doi.org/10.5281/zenodo.2625420

---

## Quick Reference

### Common Commands

```bash
# Reset environment
source ~/.bashrc
export PYTHONPATH=$PYTHONPATH:$(pwd)/source

# Clean temporary files
rm -rf /tmp/masif_*

# Test external tools
$MSMS_BIN -h
$APBS_BIN --version
reduce -h

# Test Python imports
python -c "import tensorflow, pymesh, Bio; print('OK')"

# Check GPU
python -c "import tensorflow as tf; print(tf.test.gpu_device_name())"
```

### Error Code Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `ModuleNotFoundError` | PYTHONPATH | Export PYTHONPATH |
| `FileNotFoundError` | Missing input | Check file paths |
| `PermissionError` | File permissions | chmod +x |
| `MemoryError` | Out of RAM | Reduce batch size |
| `CUDA OOM` | GPU memory full | Reduce batch size |
| `NaN in loss` | Learning rate | Reduce learning rate |
