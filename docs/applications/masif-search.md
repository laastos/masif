# MaSIF-search: Ultrafast Surface Scanning for Complex Configuration

MaSIF-search enables ultrafast scanning of protein surfaces to predict protein-protein complex configurations by matching complementary surface fingerprints.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Complete Workflow](#complete-workflow)
- [Computing Descriptors](#computing-descriptors)
- [Second Stage Alignment](#second-stage-alignment)
- [Training Your Own Model](#training-your-own-model)
- [Benchmarking](#benchmarking)
- [GIF Descriptors](#gif-descriptors)
- [Configuration](#configuration)

---

## Overview

### What MaSIF-search Does

MaSIF-search computes surface fingerprints (descriptors) that encode local geometric and chemical patterns. Complementary patches on interacting proteins have similar fingerprints, enabling:

1. **Fast Screening**: Match millions of patches in seconds
2. **Complex Prediction**: Predict how two proteins bind together
3. **Database Search**: Find potential binding partners from large databases

### Applications

- **Protein Docking**: Predict protein-protein complex structures
- **Interface Design**: Design proteins with specific binding properties
- **Drug Discovery**: Screen for therapeutic targets
- **Proteomics**: Large-scale interaction screening

### Performance

- **Bound Docking**: ~55% success rate (Top-10, CAPRI acceptable)
- **Speed**: Processes ~10,000 protein pairs per hour
- **PD-L1 Benchmark**: Correctly identifies PD-1 among 11,000 candidates

---

## How It Works

### Two-Stage Pipeline

```
Stage 1: Fingerprint Matching (Fast)
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Protein A                    Protein B                 │
│     │                            │                      │
│     ▼                            ▼                      │
│  Surface Patches             Surface Patches            │
│     │                            │                      │
│     ▼                            ▼                      │
│  Neural Network              Neural Network             │
│     │                            │                      │
│     ▼                            ▼                      │
│  Descriptors (80-dim)       Descriptors (80-dim)        │
│     │                            │                      │
│     └──────────┬─────────────────┘                      │
│                │                                        │
│                ▼                                        │
│        Distance Comparison                              │
│                │                                        │
│                ▼                                        │
│        Top-K Candidates                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
                │
                ▼
Stage 2: RANSAC Alignment (Accurate)
┌─────────────────────────────────────────────────────────┐
│  For each candidate pair:                               │
│  1. Extract corresponding patches                       │
│  2. RANSAC geometric alignment                          │
│  3. Neural network scoring                              │
│  4. Rank by alignment score                             │
└─────────────────────────────────────────────────────────┘
                │
                ▼
        Final Complex Prediction
```

### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Patch radius | 12 Å | Geodesic radius around each vertex |
| Max vertices | 200 | Maximum vertices per patch |
| Descriptor size | 80 | Fingerprint vector dimension |
| SC threshold | 0.5 | Minimum shape complementarity for training |

---

## Quick Start

### Compute Descriptors for a Protein Pair

```bash
cd data/masif_ppi_search/

# Step 1: Prepare the protein pair
./data_prepare_one.sh 1AKJ_AB_DE

# Step 2: Compute descriptors
./compute_descriptors.sh 1AKJ_AB
./compute_descriptors.sh 1AKJ_DE
```

### Run Docking Benchmark

```bash
cd comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100  # Top-100 decoys
```

---

## Complete Workflow

### Step 1: Data Preparation

Prepare a protein pair for analysis:

```bash
./data_prepare_one.sh 1AKJ_AB_DE
```

The identifier format `PDBID_CHAIN1_CHAIN2` specifies:
- `1AKJ`: PDB identifier
- `AB`: First binding partner (chains A and B)
- `DE`: Second binding partner (chains D and E)

### Step 2: Compute Descriptors

Generate fingerprints for each protein:

```bash
# For a single protein
./compute_descriptors.sh 1AKJ_AB

# For a list of proteins
./compute_descriptors.sh -l lists/testing.txt
```

Output saved to: `descriptors/sc05/all_feat/`

### Step 3: Match Descriptors

Compare descriptors between two proteins to find complementary patches:

```python
import numpy as np

# Load descriptors
desc_A = np.load('descriptors/sc05/all_feat/1AKJ_AB.npy')
desc_B = np.load('descriptors/sc05/all_feat/1AKJ_DE.npy')

# Compute pairwise distances
from scipy.spatial.distance import cdist
distances = cdist(desc_A, desc_B)

# Find matching patches (low distance = similar fingerprints)
matches = np.where(distances < 1.5)
```

### Step 4: Second Stage Alignment

Refine matches using RANSAC alignment:

```bash
cd comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100  # Number of decoys
```

---

## Computing Descriptors

### compute_descriptors.sh

The main script for generating surface fingerprints:

```bash
# Single protein
./compute_descriptors.sh 4ZQK_A

# Multiple proteins from list
./compute_descriptors.sh -l lists/testing.txt

# With custom parameters
./compute_descriptors.sh nn_models.sc05.custom_params 4ZQK_A
```

### Output Format

Descriptors are saved as NumPy arrays:

```python
import numpy as np

# Load descriptor file
desc = np.load('descriptors/sc05/all_feat/4ZQK_A.npy')

# Shape: (N, 80) where N = number of vertices
print(desc.shape)  # e.g., (2500, 80)

# Each row is an 80-dimensional fingerprint vector
# for one surface vertex
```

### Descriptor Properties

| Property | Value |
|----------|-------|
| Dimensionality | 80 |
| Normalization | L2 normalized |
| Comparison metric | Euclidean distance |
| Matching threshold | ~1.5-2.0 |

---

## Second Stage Alignment

### Overview

After fingerprint matching identifies candidate patch pairs, the second stage refines the prediction using geometric alignment.

### RANSAC Algorithm

1. **Sample**: Select 3 corresponding point pairs
2. **Estimate**: Compute rigid transformation
3. **Evaluate**: Count inliers (points that agree)
4. **Iterate**: Repeat to find best transformation
5. **Refine**: Final alignment on inliers

### Running Second Stage

```bash
cd comparison/masif_ppi_search/masif_descriptors_nn/

# Run with specific number of decoys
./second_stage_masif.sh 100    # Top-100
./second_stage_masif.sh 2000   # Top-2000 (paper benchmark)
```

### Neural Network Scoring

After RANSAC alignment, a neural network scores the quality of the predicted interface:

```python
# Score interpretation
score > 0.5   # Likely correct interface
score < 0.3   # Likely incorrect
```

---

## Training Your Own Model

### Step 1: Prepare All Training Data

```bash
# This takes several days on a cluster
sbatch prepare_data.slurm

# Requires ~400GB disk space
```

### Step 2: Cache Training Data

Filter patch pairs by shape complementarity:

```bash
./cache_nn.sh nn_models.sc05.custom_params
```

This creates balanced training data:
- Positive pairs: Patches from actual interfaces with SC > 0.5
- Negative pairs: Random non-interacting patches

Cache saved to: `nn_models/sc05/cache/`

### Step 3: Train Neural Network

```bash
./train_nn.sh nn_models.sc05.custom_params
```

Training details:
- **Duration**: ~40 hours (GPU recommended)
- **Checkpoint**: Saved when validation ROC AUC improves
- **Output**: `nn_models/sc05/all_feat/model_data/`

### Shape Complementarity Threshold

The `sc05` in model names refers to the minimum shape complementarity (0.5) for positive training examples. Different thresholds can be used:

```python
# In custom_params.py
custom_params['min_sc_filt'] = 0.5  # Default
custom_params['min_sc_filt'] = 0.3  # More permissive
custom_params['min_sc_filt'] = 0.7  # More stringent
```

---

## Benchmarking

### Bound Docking Benchmark

```bash
cd data/masif_ppi_search/

# Option 1: Download precomputed data (fastest)
wget https://www.dropbox.com/s/09fwtic1095z9z6/masif_ppi_search_precomputed_data.tar.gz
tar xzf masif_ppi_search_precomputed_data.tar.gz

# Option 2: Recompute from scratch
./recompute_data_docking_benchmark.sh

# Run benchmark
cd ../../comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100
```

### Unbound Docking Benchmark

```bash
cd data/masif_ppi_search_ub/

# Download precomputed data
wget https://www.dropbox.com/s/5w46ankuk3y2edo/masif_ppi_search_ub_precomputed_data.tar.gz
tar xzf masif_ppi_search_ub_precomputed_data.tar.gz

# Run benchmark
cd ../../comparison/masif_ppi_search_ub/masif_descriptors_nn/
./second_stage_masif.sh 2000
```

### PD-L1 Large-Scale Benchmark

This benchmark screens PD-L1 against ~11,000 proteins to find PD-1:

```bash
cd data/masif_pdl1_benchmark/

# Download data (~30GB)
wget https://www.dropbox.com/s/aaf5nt6smbrx8p7/masif_pdl1_benchmark_precomputed_data.tar
tar xf masif_pdl1_benchmark_precomputed_data.tar

# Run benchmark
./run_benchmark_nn.sh

# Sort results
cat log.txt | sort -k 2 -n
```

### Benchmark Results Format

```
# results_masif.txt
Protein_Pair  RMSD  Score  Rank
1AKJ_AB_DE    1.23  0.85   1
2ABC_A_B      2.45  0.72   3
...
```

Success metrics:
- **CAPRI Acceptable**: RMSD < 10Å, interface accuracy > 0.1
- **Top-K**: Correct prediction in top K candidates

---

## GIF Descriptors

GIF (Geometric Invariant Fingerprints) are a faster alternative to neural network descriptors.

### Computing GIF Descriptors

```bash
cd data/masif_ppi_search/

# For a list
./compute_gif_descriptors.sh lists/ransac_benchmark_list.txt

# For a single protein
./compute_gif_descriptors.sh 4ZQK_A
```

### Evaluating GIF Descriptors

```bash
cd comparison/masif_ppi_search/gif_descriptors/
./second_stage_gif.sh 100
```

### Comparison: NN vs GIF

| Feature | Neural Network | GIF |
|---------|----------------|-----|
| Accuracy | Higher | Lower |
| Speed | Requires GPU | CPU only |
| Training | Required | None |
| Use case | Best results | Quick testing |

---

## Configuration

### Default Parameters

```python
masif_opts["ppi_search"] = {}
masif_opts["ppi_search"]["training_list"] = "lists/training.txt"
masif_opts["ppi_search"]["testing_list"] = "lists/testing.txt"
masif_opts["ppi_search"]["max_shape_size"] = 200
masif_opts["ppi_search"]["max_distance"] = 12.0  # Patch radius (Å)
masif_opts["ppi_search"]["masif_precomputation_dir"] = "data_preparation/04b-precomputation_12A/precomputation/"
masif_opts["ppi_search"]["feat_mask"] = [1.0, 1.0, 1.0, 1.0, 1.0]
masif_opts["ppi_search"]["max_sc_filt"] = 1.0
masif_opts["ppi_search"]["min_sc_filt"] = 0.5
masif_opts["ppi_search"]["cache_dir"] = "nn_models/sc05/cache/"
masif_opts["ppi_search"]["model_dir"] = "nn_models/sc05/all_feat/model_data/"
masif_opts["ppi_search"]["desc_dir"] = "descriptors/sc05/all_feat/"

# Shape complementarity parameters
masif_opts["ppi_search"]["sc_radius"] = 12.0
masif_opts["ppi_search"]["sc_interaction_cutoff"] = 1.5
masif_opts["ppi_search"]["sc_w"] = 0.25
```

### Descriptor Distance Threshold

The fingerprint matching threshold affects results:

| Threshold | Candidates | Accuracy |
|-----------|------------|----------|
| 1.5 | Few | Higher |
| 1.7 | Medium | Medium |
| 2.0 | Many | Lower |

Adjust in benchmark scripts or custom parameters.

---

## Directory Structure

```
data/masif_ppi_search/
├── lists/
│   ├── training.txt
│   ├── testing.txt
│   └── ransac_benchmark_list.txt
├── nn_models/
│   └── sc05/
│       ├── custom_params.py
│       ├── cache/                    # Cached training data
│       └── all_feat/
│           └── model_data/           # Trained model
├── descriptors/
│   └── sc05/
│       └── all_feat/                 # Computed descriptors
├── gif_descriptors/                  # GIF descriptors
├── data_prepare_one.sh
├── data_prepare.slurm
├── cache_nn.sh
├── train_nn.sh
├── compute_descriptors.sh
├── compute_gif_descriptors.sh
└── recompute_data_docking_benchmark.sh
```

---

## Tips and Best Practices

### For Best Results

1. **Use bound structures**: Unbound structures have lower accuracy
2. **Complete surfaces**: Missing regions affect matching
3. **Sufficient patches**: Larger interfaces are easier to predict

### Performance Optimization

1. **GPU acceleration**: ~10x faster descriptor computation
2. **Precomputed data**: Download from Zenodo for benchmarks
3. **Parallel processing**: Use cluster for large-scale screening

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty descriptors | Check preprocessing completed |
| Poor matches | Try adjusting distance threshold |
| RANSAC failures | Ensure sufficient matching patches |
| Memory errors | Reduce number of concurrent proteins |

---

## API Reference

### Shell Scripts

```bash
# Compute descriptors
./compute_descriptors.sh [PARAMS] PDB_CHAIN
./compute_descriptors.sh -l lists/file.txt

# Cache training data
./cache_nn.sh nn_models.sc05.custom_params

# Train model
./train_nn.sh nn_models.sc05.custom_params
```

### Python Modules

```python
from masif_ppi_search.masif_ppi_search_comp_desc import compute_descriptors
from masif_ppi_search.second_stage_alignment import run_ransac

# Compute descriptors
compute_descriptors(params, pdb_id)

# Run RANSAC alignment
poses = run_ransac(desc1, desc2, coords1, coords2)
```
