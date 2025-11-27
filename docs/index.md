# MaSIF Documentation

**Molecular Surface Interaction Fingerprints: Geometric Deep Learning for Protein Surface Analysis**

MaSIF is a computational framework that uses geometric deep learning to decipher patterns in protein molecular surfaces. It enables the prediction of protein-protein interactions, ligand binding sites, and ultrafast surface matching for complex configuration prediction.

## Quick Navigation

### Getting Started
- [Installation Guide](installation.md) - System requirements, dependencies, and setup instructions
- [Quick Start Tutorial](quickstart.md) - Run your first MaSIF analysis in minutes
- [Docker Setup](docker.md) - Simplified installation using Docker containers (GPU-enabled with CUDA 12.6)

### Applications
- [MaSIF-site](applications/masif-site.md) - Protein-protein interaction site prediction
- [MaSIF-search](applications/masif-search.md) - Ultrafast surface scanning for complex configuration
- [MaSIF-ligand](applications/masif-ligand.md) - Ligand binding pocket prediction

### Technical Documentation
- [Data Preparation Pipeline](data-preparation.md) - Complete preprocessing workflow
- [Configuration Reference](configuration.md) - All configuration parameters explained
- [Source Code Architecture](architecture.md) - Understanding the codebase structure
- [Neural Network Architecture](neural-networks.md) - Deep learning components

### Tools & Visualization
- [PyMOL Plugin](pymol-plugin.md) - Visualizing molecular surfaces
- [Benchmarking Tools](benchmarking.md) - Comparison with other methods

### Reference
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [API Reference](api-reference.md) - Python module documentation
- [File Formats](file-formats.md) - Input/output file specifications

---

## What is MaSIF?

MaSIF (Molecular Surface Interaction Fingerprints) is a proof-of-concept method that deciphers patterns in protein surfaces important for specific biomolecular interactions. It exploits techniques from the field of geometric deep learning.

### How It Works

1. **Surface Decomposition**: MaSIF decomposes a protein surface into overlapping radial patches with a fixed geodesic radius (9Å or 12Å)

2. **Feature Computation**: Each point on the surface is assigned geometric and chemical features:
   - Shape index (curvature-based)
   - Distance-dependent curvature
   - Hydrophobicity
   - Hydrogen bond potential
   - Poisson-Boltzmann electrostatics

3. **Descriptor Computation**: A neural network computes a descriptor (feature vector) for each surface patch, encoding local patterns

4. **Application-Specific Processing**: The descriptors are processed by task-specific neural network layers for classification or matching

### Applications Overview

| Application | Purpose | Patch Radius | Output |
|-------------|---------|--------------|--------|
| MaSIF-site | Predict protein-protein interaction sites | 9Å | Per-vertex interaction probability |
| MaSIF-search | Find complementary protein surfaces | 12Å | Surface fingerprint descriptors |
| MaSIF-ligand | Predict ligand binding pockets | 12Å | Multi-class pocket classification |

---

## System Requirements

### Minimum Requirements

- **CPU**: Intel Xeon or equivalent (2+ cores)
- **RAM**: 16GB
- **Storage**: 50GB for software, 400GB+ per application dataset
- **OS**: Linux (Ubuntu 22.04+) or macOS
- **Python**: 3.12

### Recommended for Training

- **GPU**: NVIDIA GPU with CUDA 12.x support (RTX 3000 series or better)
- **RAM**: 32GB+
- **Storage**: SSD for faster I/O
- **TensorFlow**: 2.16.2 with GPU support

### Processing Times

- Data preparation: ~2 minutes per protein (CPU-bound)
- Neural network inference: ~2 seconds per protein (GPU)
- Full training: ~40 hours (GPU recommended)

---

## Citation

If you use MaSIF in your research, please cite:

```bibtex
@article{gainza2020deciphering,
  title={Deciphering interaction fingerprints from protein molecular surfaces
         using geometric deep learning},
  author={Gainza, Pablo and Sverrisson, Freyr and Monti, Federico and
          Rodola, Emanuele and Boscaini, Davide and Bronstein, Michael M and
          Correia, Bruno E},
  journal={Nature Methods},
  volume={17},
  pages={184--192},
  year={2020},
  doi={10.1038/s41592-019-0666-6}
}
```

---

## License

MaSIF is released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/LPDI-EPFL/masif/issues)
- **Documentation**: This documentation
- **Paper**: [Nature Methods article](https://doi.org/10.1038/s41592-019-0666-6)
- **Precomputed Data**: [Zenodo repository](https://doi.org/10.5281/zenodo.2625420)
