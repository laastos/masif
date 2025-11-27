# Neural Network Architecture

This document describes the neural network architectures used in MaSIF for processing protein molecular surfaces.

## Overview

MaSIF uses geodesic convolutional neural networks that generalize classical convolution operations to non-Euclidean domains (molecular surfaces). The architecture processes surface patches to compute descriptors encoding local geometric and chemical patterns.

## Core Concepts

### Geodesic Polar Coordinates

Each surface patch is parameterized using geodesic polar coordinates:
- **Rho (ρ)**: Geodesic distance from the patch center
- **Theta (θ)**: Angular coordinate around the center

### Gaussian Kernels

The network uses soft Gaussian kernels positioned on a polar grid:
- Grid defined by `n_rhos` radial positions and `n_thetas` angular positions
- Each kernel computes weighted combinations of input features
- Rotation-invariant through multiple rotations (typically 16)

## Network Modules

### MaSIF_site

**Purpose**: Predict protein-protein interaction sites (per-vertex classification)

**Architecture**:
```
Input Features (5D) → Geodesic Conv → Geodesic Conv → FC Layers → Sigmoid
```

**Key Parameters**:
- Patch radius: 9Å
- n_thetas: 4
- n_rhos: 3
- n_rotations: 16
- n_features: 5 (shape index, distance-dependent curvature, hydrophobicity, hydrogen bonds, electrostatics)

**Output**: Per-vertex probability of being at an interaction site

### MaSIF_search (MaSIF-ppi-search)

**Purpose**: Compute surface fingerprint descriptors for protein-protein docking

**Architecture**:
```
Input Features → Geodesic Conv (2 layers) → FC Layers → Descriptor (80D)
```

**Key Parameters**:
- Patch radius: 12Å
- n_thetas: 16
- n_rhos: 5
- n_rotations: 16
- Descriptor dimension: 80

**Output**: 80-dimensional descriptor per surface patch, with complementary surfaces producing similar descriptors

### MaSIF_ligand

**Purpose**: Multi-class classification of ligand binding pockets

**Architecture**:
```
Input Features → Geodesic Conv → FC Layers → Softmax (8 classes)
```

**Key Parameters**:
- Patch radius: 12Å
- 7 ligand classes + background: ADP, COA, FAD, HEM, NAD, NAP, SAM

**Output**: Per-vertex classification of ligand binding pocket type

## Layer Details

### Geodesic Convolution Layer

The geodesic convolution computes:

```python
output[i] = Σ_k Σ_j G_k(ρ_j, θ_j) · input[j] · W_k
```

Where:
- `G_k` is the k-th Gaussian kernel
- `ρ_j, θ_j` are geodesic coordinates of vertex j
- `W_k` are learnable weights

**Implementation** (`source/masif_modules/MaSIF_site.py`):

```python
def inference(self, input_feat, rho_coords, theta_coords, mask, ...):
    # Compute Gaussian activations
    rho_activation = exp(-square(rho - mu_rho) / sigma_rho^2)
    theta_activation = exp(-square(theta - mu_theta) / sigma_theta^2)
    gauss_activation = rho_activation * theta_activation

    # Apply to input features
    gauss_desc = gauss_activation * input_feat

    # Convolve with learnable weights
    output = conv1d(gauss_desc, W_conv)
```

### Fully Connected Layers

Standard dense layers with ReLU activation:
- Uses Xavier/Glorot initialization
- Batch normalization optional
- Dropout for regularization during training

## Rotation Invariance

To achieve rotation invariance, the network:

1. Rotates input coordinates by k × (2π / n_rotations) for k = 0, 1, ..., n_rotations-1
2. Computes features for each rotation
3. Aggregates using max pooling across rotations

This ensures the descriptor is invariant to the arbitrary choice of θ=0 direction.

## Training Details

### Loss Functions

- **MaSIF-site**: Binary cross-entropy for interaction site classification
- **MaSIF-search**: Contrastive loss + regularization for descriptor learning
- **MaSIF-ligand**: Multi-class cross-entropy for pocket classification

### Optimization

- Optimizer: Adam
- Learning rate: Application-specific (typically 1e-4 to 1e-3)
- Batch size: 1 (due to variable patch sizes)
- Epochs: Until convergence (monitored via validation loss)

### Data Augmentation

- Random rotation of patches
- Dropout during training
- Class balancing for imbalanced datasets

## Parameter Counts

Approximate trainable parameters:
- MaSIF-site: ~50,000
- MaSIF-search: ~100,000
- MaSIF-ligand: ~80,000

## TensorFlow Implementation

The networks are implemented using TensorFlow 1.x compatibility mode:

```python
import tensorflow.compat.v1 as tf
tf.disable_eager_execution()
```

Key classes:
- `MaSIF_site` - Site prediction network
- `MaSIF_ppi_search` - Surface fingerprint network
- `MaSIF_ligand` - Ligand pocket classification network

## References

- Masci, J., et al. "Geodesic convolutional neural networks on Riemannian manifolds." ICCV 2015.
- Monti, F., et al. "Geometric deep learning on graphs and manifolds using mixture model CNNs." CVPR 2017.
- Gainza, P., et al. "Deciphering interaction fingerprints from protein molecular surfaces." Nature Methods 2020.
