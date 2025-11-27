# MaSIF Docker GPU Update Plan

## Status: IMPLEMENTED

All changes described in this plan have been applied to the codebase.

---

## Target Environment

- **GPUs**: 2x NVIDIA RTX PRO 6000 Blackwell (CC 12.0, 98GB VRAM each)
- **Driver**: 580.76.05
- **CUDA**: 13.0
- **Reference**: AlphaFold3 Dockerfile (`nvidia/cuda:12.6.3-base-ubuntu24.04`)

## Migration Summary

| Component | Previous | Current |
|-----------|----------|---------|
| Base Image | `ubuntu:20.04` | `nvidia/cuda:12.6.3-base-ubuntu24.04` |
| Python | 3.8 | 3.12 (Ubuntu 24.04 default) |
| TensorFlow | 2.4.0 (CPU) | 2.16.2 (GPU) |
| CUDA | None | 12.6 |

---

## Part 1: Dockerfile Changes

### Base Image (AlphaFold3 pattern)

```dockerfile
FROM nvidia/cuda:12.6.3-base-ubuntu24.04
```

### Python Virtual Environment

```dockerfile
RUN python3 -m venv /masif_venv
ENV PATH="/masif_venv/bin:$PATH"
```

### GPU-Enabled TensorFlow

```dockerfile
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    "tensorflow[and-cuda]==2.16.2" \
    numpy scipy matplotlib ipython \
    biopython scikit-learn networkx \
    open3d dask packaging plyfile SBILib
```

### GPU Environment Variables

```dockerfile
ENV XLA_FLAGS="--xla_gpu_enable_triton_gemm=false"
ENV XLA_PYTHON_CLIENT_PREALLOCATE=true
ENV XLA_CLIENT_MEM_FRACTION=0.95
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV TF_ENABLE_ONEDNN_OPTS=0
```

---

## Part 2: TensorFlow Code Fixes Applied

### Fix 1: Replace `tf.disable_v2_behavior()` with `tf.disable_eager_execution()`

**Files updated (6 files)**:
- `source/masif_modules/MaSIF_site.py`
- `source/masif_modules/MaSIF_ligand.py`
- `source/masif_modules/MaSIF_ppi_search.py`
- `source/masif_ligand/masif_ligand_train.py`
- `source/masif_modules/read_ligand_tfrecords.py`
- `source/data_preparation/04b-make_ligand_tfrecords.py`

### Fix 2: Update `dim.value` access

**Files updated**: `MaSIF_site.py`, `MaSIF_ligand.py`, `MaSIF_ppi_search.py`

```python
# Changed from:
variable_parameters *= dim.value

# To:
variable_parameters *= dim if isinstance(dim, int) else int(dim)
```

### Fix 3: Update `make_one_shot_iterator()`

**File updated**: `source/masif_ligand/masif_ligand_train.py`

```python
# Changed from:
training_iterator = training_data.make_one_shot_iterator()

# To:
training_iterator = tf.compat.v1.data.make_one_shot_iterator(training_data)
```

---

## Part 3: External Tools (Unchanged)

These tools remain configured as before:
- MSMS 2.6.1 (multiple fallback sources)
- APBS 3.4.1 (GitHub release)
- PDB2PQR (pip install)
- Reduce (build from source)
- PyMesh (build from source)

---

## Part 4: Files Modified

| File | Changes |
|------|---------|
| `docker/Dockerfile` | GPU base image, Python 3.12, TF 2.16.2 |
| `source/masif_modules/MaSIF_site.py` | TF import + dim.value fix |
| `source/masif_modules/MaSIF_ligand.py` | TF import + dim.value fix |
| `source/masif_modules/MaSIF_ppi_search.py` | TF import + dim.value fix |
| `source/masif_ligand/masif_ligand_train.py` | TF import + iterator fix |
| `source/masif_modules/read_ligand_tfrecords.py` | TF import fix |
| `source/data_preparation/04b-make_ligand_tfrecords.py` | TF import fix |

**Total: 7 files modified**

---

## Part 5: Building and Running

### Build the Docker Image

```bash
cd docker/
docker build -t masif .
```

### Run with GPU Support

```bash
docker run --gpus all -it masif
```

### With Volume Mounting

```bash
docker run --gpus all -it -v /path/to/data:/data masif
```

---

## Part 6: Testing

### GPU Detection

```bash
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
# Expected: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU'), ...]
```

### MaSIF-site Test

```bash
cd /masif/data/masif_site
./data_prepare_one.sh 4ZQK_A
./predict_site.sh 4ZQK_A
```

### MaSIF-search Test

```bash
cd /masif/data/masif_ppi_search
./data_prepare_one.sh 4ZQK_A_B
./compute_descriptors.sh 4ZQK_A_B
```

---

## Sources

- [AlphaFold3 Installation](https://github.com/google-deepmind/alphafold3/blob/main/docs/installation.md)
- [AlphaFold3 Dockerfile](https://github.com/google-deepmind/alphafold3/blob/main/docker/Dockerfile)
- [NVIDIA CUDA Docker Hub](https://hub.docker.com/r/nvidia/cuda)
