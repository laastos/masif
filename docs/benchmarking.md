# Benchmarking Tools

This document describes the benchmarking tools and comparisons included with MaSIF for evaluating performance against other methods.

## Overview

The `comparison/` directory contains scripts and data for reproducing the benchmarks presented in the MaSIF paper:

> Gainza, P., Sverrisson, F., Monti, F., Rodola, E., Bronstein, M. M., & Correia, B. E. (2020).
> Deciphering interaction fingerprints from protein molecular surfaces. Nature Methods.

## Benchmark Structure

```
comparison/
├── masif_site/           # MaSIF-site benchmarks
├── masif_ppi_search/     # MaSIF-search benchmarks (bound)
├── masif_ppi_search_ub/  # MaSIF-search benchmarks (unbound)
└── masif_ligand/         # MaSIF-ligand benchmarks
```

## MaSIF-site Benchmarks

### Compared Methods

| Method | Description |
|--------|-------------|
| **SPPIDER** | Solvent accessibility-based site prediction |
| **PSIVER** | Position-specific interface propensity |
| **IntPred** | Interface residue prediction using random forests |

### Running the Benchmark

```bash
cd comparison/masif_site/masif_vs_sppider/
python compare_predictions.py
```

### Metrics

- Area Under ROC Curve (AUC)
- Precision-Recall curves
- Per-residue accuracy

## MaSIF-search Benchmarks

### Compared Methods

| Method | Description |
|--------|-------------|
| **PatchDock** | Geometric shape complementarity docking |
| **ZDOCK** | FFT-based rigid-body docking |
| **ZDOCK+ZRANK2** | ZDOCK with energy-based re-scoring |

### Benchmark Datasets

1. **Bound (holo) structures** (`masif_ppi_search/`)
   - Uses crystal structure conformations
   - Tests pure shape complementarity matching

2. **Unbound structures** (`masif_ppi_search_ub/`)
   - Uses unbound protein conformations
   - Tests robustness to conformational changes

### Running the Benchmark

```bash
cd comparison/masif_ppi_search/

# Compute MaSIF descriptors
./masif_descriptors_nn/second_stage_masif.sh

# Compute GIF descriptors (for comparison)
./gif_descriptors/second_stage_gif.sh

# Run PatchDock
cd patchdock/
./run_all.sh
./eval_all.sh
```

### Output Files

- `results_masif.txt`: MaSIF prediction results
- `data.txt`: Comparison metrics across methods

### Evaluation Metrics

- **Success rate**: Fraction of targets with correct prediction in top-N
- **RMSD**: Root Mean Square Deviation from native structure
- **Interface RMSD (i-RMSD)**: RMSD of interface residues only
- **Ligand RMSD (l-RMSD)**: RMSD of the smaller binding partner

## MaSIF-ligand Benchmarks

### Compared Methods

| Method | Description |
|--------|-------------|
| **ProBiS** | Protein Binding Sites detection by local similarity |
| **KRIPO** | Key Representation of Interaction in Pockets |

### Running the Benchmark

```bash
cd comparison/masif_ligand/

# Generate ProBiS surfaces
python make_probis_srfs.py

# Run ProBiS comparison
./run_probis.sh

# Generate Kripo fingerprints
cd Kripo/test_set/
python generate_fingerprints_multithreaded.py

# Generate ROC curves
jupyter notebook make_ROC.ipynb
```

### Datasets

- **Full benchmark set**: `benchmark_set_full.txt`
- **Reduced benchmark set**: `benchmark_set.txt`
- **Pocket similarity splits**: Based on TM-score thresholds (0.25, 0.40, 0.50)

### Pocket-to-Pocket Alignment

The `data/pocket_to_pocket_align/` directory contains tools for structural alignment of binding pockets:

```bash
cd data/pocket_to_pocket_align/
python pocket_to_pocket_align.py
python get_split.py
```

### Output Files

- `masif_*.npy`: MaSIF prediction arrays (TPR, FPR)
- `probis_*.npy`: ProBiS prediction arrays
- `kripo_*.npy`: KRIPO prediction arrays
- `ROCs_*.pdf`: Generated ROC curve plots

### Evaluation Metrics

- **ROC-AUC**: Area Under the Receiver Operating Characteristic curve
- **True Positive Rate (TPR)** at various False Positive Rate thresholds
- **Pocket similarity scores** based on structural alignment

## Reproducing Paper Results

### Step 1: Download Precomputed Data

Download the benchmark datasets from Zenodo:
```bash
# See data/README for download links
wget https://doi.org/10.5281/zenodo.2625420
```

### Step 2: Run All Benchmarks

```bash
# MaSIF-site
cd comparison/masif_site/
./run_all_benchmarks.sh

# MaSIF-search
cd comparison/masif_ppi_search/
./run_all.sh

# MaSIF-ligand
cd comparison/masif_ligand/
./run_all.sh
```

### Step 3: Generate Figures

Each benchmark directory contains Jupyter notebooks for generating figures:
- `make_ROC.ipynb`: ROC curves
- `analysis.ipynb`: Detailed analysis

## Adding Custom Benchmarks

### Custom Dataset Structure

```
my_benchmark/
├── lists/
│   ├── training.txt
│   └── testing.txt
├── data/
│   └── preprocessed surfaces
└── results/
    └── prediction outputs
```

### Evaluation Script Template

```python
from sklearn.metrics import roc_auc_score, precision_recall_curve
import numpy as np

# Load predictions and ground truth
predictions = np.load('predictions.npy')
labels = np.load('labels.npy')

# Calculate metrics
auc = roc_auc_score(labels, predictions)
precision, recall, _ = precision_recall_curve(labels, predictions)

print(f"ROC-AUC: {auc:.3f}")
```

## Performance Notes

- MaSIF-search achieves >90% success rate on bound benchmark
- MaSIF-site outperforms SPPIDER by ~10% AUC
- MaSIF-ligand shows superior pocket classification vs. ProBiS/KRIPO

## References

1. Gainza et al. "Deciphering interaction fingerprints..." Nature Methods 2020
2. Chen et al. "ZDOCK: An initial-stage protein-docking algorithm." Proteins 2003
3. Schneidman-Duhovny et al. "PatchDock and SymmDock." NAR 2005
4. Konc & Janezic. "ProBiS algorithm for detection of structurally similar protein binding sites." Bioinformatics 2010
