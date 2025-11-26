# MaSIF-ligand: Ligand Binding Pocket Prediction

MaSIF-ligand predicts ligand binding pockets on protein surfaces and classifies them according to the type of ligand they can bind.

## Table of Contents

- [Overview](#overview)
- [Supported Ligands](#supported-ligands)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Complete Workflow](#complete-workflow)
- [Training Your Own Model](#training-your-own-model)
- [Output Interpretation](#output-interpretation)
- [Benchmarking](#benchmarking)
- [Configuration](#configuration)

---

## Overview

### What MaSIF-ligand Does

MaSIF-ligand analyzes protein surfaces to:
1. Identify regions that form binding pockets
2. Classify pockets by the type of ligand they bind
3. Provide confidence scores for each prediction

### Applications

- **Drug Discovery**: Identify druggable pockets on target proteins
- **Ligand Prediction**: Predict what cofactors a protein might bind
- **Enzyme Annotation**: Identify catalytic sites
- **Protein Engineering**: Design binding pockets for specific ligands

### Performance

- **Multi-class Classification**: 7 ligand types
- **Comparison**: Outperforms Kripo and ProBiS methods

---

## Supported Ligands

MaSIF-ligand is trained to recognize binding pockets for seven common biological cofactors:

| Ligand | Full Name | Function |
|--------|-----------|----------|
| **ADP** | Adenosine Diphosphate | Energy transfer, signaling |
| **COA** | Coenzyme A | Acyl group transfer |
| **FAD** | Flavin Adenine Dinucleotide | Redox reactions |
| **HEM** | Heme | Oxygen transport, electron transfer |
| **NAD** | Nicotinamide Adenine Dinucleotide | Redox reactions |
| **NAP** | NADP | Biosynthetic reactions |
| **SAM** | S-Adenosyl Methionine | Methyl group transfer |

---

## How It Works

### Architecture

```
Protein Surface
       │
       ▼
┌─────────────────────────┐
│ Identify Pocket Patches │
│ (12Å radius)            │
└─────────────────────────┘
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
│ Neural Network          │
└─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Multi-class Softmax     │
│ (7 ligand classes)      │
└─────────────────────────┘
       │
       ▼
Ligand Type Prediction
+ Confidence Score
```

### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Patch radius | 12 Å | Geodesic radius around pocket center |
| Max vertices | 200 | Maximum vertices per patch |
| Classes | 7 | Number of ligand types |
| Features | 5 | Shape, DDC, hydrophob., H-bond, electrostatics |

---

## Quick Start

### Predict Ligand Binding Sites

```bash
cd data/masif_ligand/

# Step 1: Prepare the protein (with ligand info)
./data_prepare_one.sh 1MBN_A_HEM

# Step 2: Evaluate predictions
./evaluate_test.sh
```

### Naming Convention

MaSIF-ligand uses a special naming format:

```
{PDBID}_{CHAIN}_{LIGAND}
```

Examples:
- `1MBN_A_HEM` - Myoglobin chain A with Heme
- `3PFN_A_NAD` - Protein with NAD binding site
- `5LXM_AD_FAD` - Protein chains A,D with FAD

---

## Complete Workflow

### Step 1: Generate Biological Assembly

MaSIF-ligand requires the biological assembly (oligomeric state):

```bash
python $masif_source/data_preparation/00b-generate_assembly.py PDBID
```

This uses the StrBioInfo library (Python 2.7) to generate the correct oligomeric state.

### Step 2: Save Ligand Coordinates

Extract and save the ligand coordinates for training labels:

```bash
python $masif_source/data_preparation/00c-save_ligand_coords.py PDBID_CHAIN_LIGAND
```

### Step 3: Surface Triangulation

Compute the molecular surface with chemical features:

```bash
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py PDBID_CHAIN masif_ligand
```

### Step 4: Precompute Patches

Decompose the surface into patches:

```bash
python $masif_source/data_preparation/04-masif_precompute.py masif_ligand PDBID_CHAIN
```

### Convenience Script

For a single protein:

```bash
./data_prepare_one.sh 1MBN_A_HEM
```

This runs all steps automatically.

### Batch Processing

```bash
# Submit to cluster
sbatch prepare_data.slurm
```

---

## Training Your Own Model

### Step 1: Prepare All Training Data

```bash
# Sequential (slow)
./data_prepare_all.sh

# Or with SLURM (fast)
sbatch prepare_data.slurm
```

### Step 2: Create TensorFlow Records

Convert precomputed data to TFRecord format for efficient training:

```bash
python $masif_source/masif_ligand/masif_ligand_make_tfrecord.py

# Or using SLURM
sbatch make_tfrecord.slurm
```

TFRecords are saved to: `data_preparation/tfrecords/`

### Step 3: Train the Neural Network

```bash
python $masif_source/masif_ligand/masif_ligand_train.py

# Or using SLURM
sbatch train_model.slurm
```

Training configuration:
- **Data split**: 72% train, 8% validation, 20% test
- **Cost function**: D-prime (dprime) by default
- **Duration**: Several hours on GPU

### Step 4: Evaluate on Test Set

```bash
python $masif_source/masif_ligand/masif_ligand_evaluate_test.py

# Or using SLURM
sbatch evaluate_test.slurm
```

---

## Output Interpretation

### Prediction Files

Output saved to `test_set_predictions/`:

```
5LXM_AD_labels.npy   # Ground truth labels
5LXM_AD_logits.npy   # Prediction logits
```

### Understanding Output

```python
import numpy as np

# Load predictions
labels = np.load('test_set_predictions/5LXM_AD_labels.npy')
logits = np.load('test_set_predictions/5LXM_AD_logits.npy')

# Convert logits to probabilities
from scipy.special import softmax
probs = softmax(logits, axis=-1)

# Get predicted class
predicted_class = np.argmax(probs)

# Class mapping
ligand_classes = ['ADP', 'COA', 'FAD', 'HEM', 'NAD', 'NAP', 'SAM']
predicted_ligand = ligand_classes[predicted_class]

print(f"Predicted ligand: {predicted_ligand}")
print(f"Confidence: {probs[predicted_class]:.2%}")
```

### Class Labels

| Index | Ligand |
|-------|--------|
| 0 | ADP |
| 1 | COA |
| 2 | FAD |
| 3 | HEM |
| 4 | NAD |
| 5 | NAP |
| 6 | SAM |

---

## Benchmarking

### Comparison with Other Methods

MaSIF-ligand is compared with:
- **Kripo**: Pharmacophore-based pocket comparison
- **ProBiS**: Local structural alignment method

### Running Comparisons

```bash
cd comparison/masif_ligand/

# Run ProBiS comparison
./run_probis.sh

# Run all comparisons
./run_all.sh
```

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Accuracy | Overall classification accuracy |
| Per-class AUC | ROC AUC for each ligand type |
| Confusion Matrix | Predicted vs actual classes |
| D-prime | Signal detection metric |

---

## Configuration

### Default Parameters

```python
masif_opts["ligand"] = {}
masif_opts["ligand"]["assembly_dir"] = "data_preparation/00b-pdbs_assembly"
masif_opts["ligand"]["ligand_coords_dir"] = "data_preparation/00c-ligand_coords"
masif_opts["ligand"]["masif_precomputation_dir"] = "data_preparation/04a-precomputation_12A/precomputation/"
masif_opts["ligand"]["max_shape_size"] = 200
masif_opts["ligand"]["feat_mask"] = [1.0, 1.0, 1.0, 1.0, 1.0]
masif_opts["ligand"]["train_fract"] = 0.72   # 90% * 80%
masif_opts["ligand"]["val_fract"] = 0.08     # 10% * 80%
masif_opts["ligand"]["test_fract"] = 0.20
masif_opts["ligand"]["tfrecords_dir"] = "data_preparation/tfrecords"
masif_opts["ligand"]["max_distance"] = 12.0
masif_opts["ligand"]["n_classes"] = 7
masif_opts["ligand"]["costfun"] = "dprime"
masif_opts["ligand"]["model_dir"] = "nn_models/all_feat/"
masif_opts["ligand"]["test_set_out_dir"] = "test_set_predictions/"
```

### Data Split

The dataset is split as follows:
- **Training**: 72% (0.9 × 0.8)
- **Validation**: 8% (0.1 × 0.8)
- **Testing**: 20%

### Cost Function Options

| Function | Description | Use Case |
|----------|-------------|----------|
| `dprime` | D-prime (signal detection) | Default, balanced classes |
| `crossent` | Cross-entropy | Standard classification |

---

## Directory Structure

```
data/masif_ligand/
├── lists/
│   ├── train_pdbs_sequence.npy    # Training set
│   ├── val_pdbs_sequence.npy      # Validation set
│   └── test_pdbs_sequence.npy     # Test set
├── nn_models/
│   └── all_feat/
│       └── model_data/            # Trained model
├── test_set_predictions/          # Output predictions
├── data_preparation/
│   ├── 00b-pdbs_assembly/         # Biological assemblies
│   ├── 00c-ligand_coords/         # Ligand coordinates
│   └── tfrecords/                 # TensorFlow records
├── data_prepare_one.sh
├── data_prepare.slurm
├── make_tfrecord.slurm
├── train_model.slurm
└── evaluate_test.slurm
```

---

## Special Requirements

### Python 2.7 for Assembly Generation

The biological assembly generation requires Python 2.7 with the StrBioInfo library. This is pre-installed in the GPU Docker container.

```bash
# Check Python 2.7 availability
python2.7 --version

# Install StrBioInfo (if needed)
pip2.7 install StrBioInfo
```

### TensorFlow Records

MaSIF-ligand uses TFRecords for efficient data loading during training:

```python
# Reading TFRecords
from masif_modules.read_ligand_tfrecords import read_tfrecord

dataset = read_tfrecord(tfrecord_path, params)
```

---

## Tips and Best Practices

### For Best Predictions

1. **Use biological assembly**: Oligomeric state affects pocket shape
2. **Complete structures**: Missing residues affect pocket boundaries
3. **Known ligand position**: For training, ligand coordinates define the pocket center

### Common Issues

| Issue | Solution |
|-------|----------|
| Assembly generation fails | Check Python 2.7 and StrBioInfo |
| No pocket found | Verify ligand is within detection range |
| Low accuracy | Ensure proper preprocessing |

### Limitations

- Limited to 7 trained ligand types
- Requires known pocket center for training
- May not generalize to novel ligand types

---

## API Reference

### Shell Scripts

```bash
# Prepare single protein
./data_prepare_one.sh PDBID_CHAIN_LIGAND

# Create TFRecords
sbatch make_tfrecord.slurm

# Train model
sbatch train_model.slurm

# Evaluate
sbatch evaluate_test.slurm
```

### Python Modules

```python
from masif_ligand.masif_ligand_train import train_model
from masif_ligand.masif_ligand_evaluate_test import evaluate_test

# Train model
train_model(params)

# Evaluate on test set
evaluate_test(params)
```
