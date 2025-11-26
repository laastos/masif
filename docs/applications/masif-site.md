# MaSIF-site: Protein-Protein Interaction Site Prediction

MaSIF-site predicts which regions of a protein surface are likely to participate in protein-protein interactions (PPIs).

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Complete Workflow](#complete-workflow)
- [Training Your Own Model](#training-your-own-model)
- [Output Interpretation](#output-interpretation)
- [Benchmarking](#benchmarking)
- [Configuration](#configuration)

---

## Overview

### What MaSIF-site Does

MaSIF-site takes a protein structure and predicts the probability that each point on the molecular surface will participate in a protein-protein interaction.

### Applications

- **Drug Discovery**: Identify potential binding sites for therapeutic intervention
- **Protein Engineering**: Guide mutations to modulate protein interactions
- **Structural Biology**: Predict interaction interfaces before experimental determination
- **Network Biology**: Map potential protein-protein interaction networks

### Performance

On the transient interaction benchmark:
- **ROC AUC**: ~0.87
- **Comparison**: Outperforms SPPIDER and other sequence-based methods

---

## How It Works

### Architecture

```
Surface Patch (9Å radius)
         │
         ▼
┌─────────────────────────┐
│ Input Features          │
│ - Shape index           │
│ - Distance-dep. curv.   │
│ - Hydrophobicity        │
│ - H-bond potential      │
│ - Electrostatics        │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Geodesic Convolution    │
│ (3 layers)              │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Dense Layers            │
└─────────────────────────┘
         │
         ▼
Interface Probability (0-1)
```

### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Patch radius | 9 Å | Geodesic radius around each vertex |
| Max vertices | 100 | Maximum vertices per patch |
| Conv layers | 3 | Number of geodesic convolution layers |
| Features | 5 | Shape, DDC, hydrophob., H-bond, electrostatics |

---

## Quick Start

### Predict Interaction Sites

```bash
cd data/masif_site/

# Step 1: Prepare the protein
./data_prepare_one.sh 4ZQK_A

# Step 2: Run prediction
./predict_site.sh 4ZQK_A

# Step 3: Generate colored surface
./color_site.sh 4ZQK_A
```

### View Results

The output PLY file can be visualized in PyMOL:

```
# In PyMOL
loadply output/all_feat_3l/pred_surfaces/4ZQK_A.ply
```

Red regions = low interaction probability
Blue regions = high interaction probability

---

## Complete Workflow

### Step 1: Data Preparation

Prepare a single protein:

```bash
./data_prepare_one.sh 4ZQK_A
```

This runs:
1. Downloads PDB structure
2. Extracts and protonates the chain
3. Computes molecular surface
4. Calculates chemical features
5. Decomposes into patches

For multiple chains as one surface:

```bash
./data_prepare_one.sh 4ZQK_AB
```

Using your own PDB file:

```bash
./data_prepare_one.sh --file /path/to/protein.pdb MYPDB_A
```

### Step 2: Neural Network Prediction

```bash
./predict_site.sh 4ZQK_A
```

The script:
1. Loads the trained model from `nn_models/all_feat_3l/model_data/`
2. Extracts patches from the precomputed data
3. Runs each patch through the neural network
4. Outputs per-vertex interaction probabilities

### Step 3: Visualization

Generate a colored surface file:

```bash
./color_site.sh 4ZQK_A
```

This creates a PLY file colored by prediction scores.

### Batch Processing

For multiple proteins:

```bash
# Using a list file
for pdb in $(cat lists/testing.txt); do
    ./data_prepare_one.sh $pdb
    ./predict_site.sh $pdb
    ./color_site.sh $pdb
done

# Or using SLURM
sbatch prepare_data.slurm
```

---

## Training Your Own Model

### Step 1: Prepare Training Data

Prepare all proteins in the training list:

```bash
# Sequential (slow)
./data_prepare_all.sh

# Or with SLURM (fast, parallel)
sbatch prepare_data.slurm
```

This requires ~400GB of disk space.

### Step 2: Train the Neural Network

```bash
./train_nn.sh
```

Or submit to cluster:

```bash
sbatch masif_site_train.slurm
```

Training details:
- **Duration**: ~40 hours recommended
- **GPU**: Strongly recommended
- **Validation**: Model saved when validation ROC AUC improves

### Step 3: Monitor Training

Training output includes:
- Loss values per epoch
- Validation ROC AUC
- Best model checkpoint saved automatically

### Custom Training Configuration

Create a custom configuration in `nn_models/custom_params.py`:

```python
# Custom parameters
custom_params = {}
custom_params['n_conv_layers'] = 3
custom_params['out_pred_dir'] = 'output/my_model/pred_data/'
custom_params['out_surf_dir'] = 'output/my_model/pred_surfaces/'
custom_params['model_dir'] = 'nn_models/my_model/model_data/'
```

---

## Output Interpretation

### Prediction Files

| File | Location | Description |
|------|----------|-------------|
| `pred_{PDB}_{CHAIN}.npy` | `output/all_feat_3l/pred_data/` | Raw predictions (NumPy) |
| `{PDB}_{CHAIN}.ply` | `output/all_feat_3l/pred_surfaces/` | Colored surface |

### Understanding Predictions

```python
import numpy as np

# Load predictions
pred = np.load('output/all_feat_3l/pred_data/pred_4ZQK_A.npy')

# pred shape: (N,) where N = number of vertices
# Values: probability of interaction (0.0 - 1.0)

# High confidence interface: pred > 0.5
interface_vertices = np.where(pred > 0.5)[0]
```

### ROC AUC Scores

When running `color_site.sh`, a ROC AUC score is printed:

```
ROC AUC score for protein 4ZQK_A : 0.91
```

This compares predictions to ground truth (interface labels from the complex structure). Only meaningful for proteins in the original dataset.

---

## Benchmarking

### Reproduce Paper Results

Run the transient interaction benchmark:

```bash
./reproduce_transient_benchmark.sh
```

This:
1. Prepares ~60 proteins (~2 hours)
2. Runs predictions on all
3. Computes ROC AUC scores
4. Generates comparison statistics

### Compare with SPPIDER

```bash
cd $masif_root/comparison/masif_site/masif_vs_sppider/

# Open the Jupyter notebook
jupyter notebook masif_sppider_comp.ipynb
```

The notebook contains:
- ROC curve comparisons
- Statistical tests
- Visualization of results

### Benchmark Datasets

| Dataset | Purpose | Location |
|---------|---------|----------|
| Training | Model training | `lists/training.txt` |
| Testing | Final evaluation | `lists/testing.txt` |
| Full list | All proteins | `lists/full_list.txt` |

---

## Configuration

### Default Parameters

From `source/default_config/masif_opts.py`:

```python
masif_opts["site"] = {}
masif_opts["site"]["training_list"] = "lists/training.txt"
masif_opts["site"]["testing_list"] = "lists/testing.txt"
masif_opts["site"]["max_shape_size"] = 100        # Max vertices per patch
masif_opts["site"]["n_conv_layers"] = 3           # Convolution layers
masif_opts["site"]["max_distance"] = 9.0          # Patch radius (Å)
masif_opts["site"]["masif_precomputation_dir"] = "data_preparation/04a-precomputation_9A/precomputation/"
masif_opts["site"]["range_val_samples"] = 0.9     # Validation split
masif_opts["site"]["model_dir"] = "nn_models/all_feat_3l/model_data/"
masif_opts["site"]["out_pred_dir"] = "output/all_feat_3l/pred_data/"
masif_opts["site"]["out_surf_dir"] = "output/all_feat_3l/pred_surfaces/"
masif_opts["site"]["feat_mask"] = [1.0, 1.0, 1.0, 1.0, 1.0]  # All features
```

### Feature Ablation Models

Pre-trained models with different feature combinations:

| Model | Features | Directory |
|-------|----------|-----------|
| All features (3 layers) | All | `nn_models/all_feat_3l/` |
| All features (1 layer) | All | `nn_models/all_feat_1l/` |
| Shape only | Shape index + DDC | `nn_models/shape_only/` |
| H-bond only | H-bond potential | `nn_models/hbond_only/` |
| Hydrophobicity only | Hydrophobicity | `nn_models/hphob_only/` |
| Electrostatics only | PB charges | `nn_models/pb_only/` |

### Using Different Models

Modify `predict_site.sh` or pass custom parameters:

```bash
# Edit nn_models/all_feat_3l/custom_params.py
# Or create new parameter file
python $masif_source/masif_site/masif_site_predict.py nn_models.shape_only.custom_params 4ZQK_A
```

---

## Directory Structure

```
data/masif_site/
├── lists/
│   ├── training.txt
│   ├── testing.txt
│   └── full_list.txt
├── nn_models/
│   ├── all_feat_3l/
│   │   ├── custom_params.py
│   │   └── model_data/
│   ├── all_feat_1l/
│   ├── shape_only/
│   ├── hbond_only/
│   ├── hphob_only/
│   └── pb_only/
├── output/
│   └── all_feat_3l/
│       ├── pred_data/
│       └── pred_surfaces/
├── data_prepare_one.sh
├── data_prepare.slurm
├── train_nn.sh
├── predict_site.sh
├── color_site.sh
└── reproduce_transient_benchmark.sh
```

---

## Tips and Best Practices

### For Best Predictions

1. **Use complete structures**: Missing residues affect surface computation
2. **Protonate properly**: Ensure all hydrogens are added
3. **Consider biological assembly**: Some interfaces require oligomeric context

### Performance Optimization

1. **GPU usage**: Predictions are ~10x faster on GPU
2. **Batch processing**: Process multiple proteins in parallel
3. **Precomputed data**: Download from Zenodo for large datasets

### Common Issues

| Issue | Solution |
|-------|----------|
| Low ROC AUC | Normal for proteins not in training set |
| Missing predictions | Check preprocessing completed |
| Memory errors | Reduce batch size or use smaller proteins |

---

## API Reference

### Main Scripts

#### predict_site.sh

```bash
./predict_site.sh PDB_CHAIN [MODEL_PARAMS]
```

Arguments:
- `PDB_CHAIN`: Protein identifier (e.g., `4ZQK_A`)
- `MODEL_PARAMS`: Optional custom parameter module

#### color_site.sh

```bash
./color_site.sh PDB_CHAIN [MODEL_PARAMS]
```

Generates colored PLY file for visualization.

### Python Modules

```python
from masif_site.masif_site_predict import predict_site
from masif_site.masif_site_label_surface import label_surface

# Predict interaction sites
predict_site(params, pdb_id)

# Generate colored surface
label_surface(params, pdb_id)
```
