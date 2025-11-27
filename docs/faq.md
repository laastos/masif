# Frequently Asked Questions

Common questions and answers about MaSIF.

## Table of Contents

- [General Questions](#general-questions)
- [Installation Questions](#installation-questions)
- [Usage Questions](#usage-questions)
- [Results Interpretation](#results-interpretation)
- [Performance Questions](#performance-questions)
- [Research Questions](#research-questions)

---

## General Questions

### What is MaSIF?

MaSIF (Molecular Surface Interaction Fingerprints) is a geometric deep learning framework that analyzes protein molecular surfaces to:
- Predict protein-protein interaction sites (MaSIF-site)
- Match complementary surfaces for docking (MaSIF-search)
- Identify ligand binding pockets (MaSIF-ligand)

### How does MaSIF differ from other methods?

Unlike sequence-based methods, MaSIF operates directly on 3D molecular surfaces, capturing geometric and chemical patterns that are difficult to encode in sequence. It uses geodesic convolutions that generalize classical image convolutions to curved surfaces.

### What are the main applications?

1. **Drug Discovery**: Identify druggable sites and design protein binders
2. **Structural Biology**: Predict protein complexes
3. **Protein Engineering**: Design interaction interfaces
4. **Computational Biology**: Large-scale interaction screening

### Is MaSIF accurate?

Performance varies by application:
- **MaSIF-site**: ~0.87 ROC AUC on transient interactions
- **MaSIF-search**: ~55% success rate (Top-10, CAPRI acceptable)
- **MaSIF-ligand**: Competitive with specialized ligand prediction methods

### What are the limitations?

- Requires high-quality structural data
- Preprocessing is computationally expensive (~2 min/protein)
- Training requires large datasets and GPU resources
- Limited to known ligand types for MaSIF-ligand

---

## Installation Questions

### What's the easiest way to install MaSIF?

Docker provides the easiest installation with GPU support:

```bash
cd docker/
docker build -t masif .
docker run --gpus all -it masif
```

### Do I need a GPU?

- **For inference**: CPU works, GPU is 10-15x faster
- **For training**: GPU strongly recommended (10-100x speedup)
- **For preprocessing**: CPU-bound, GPU doesn't help

The Docker container includes full GPU support with CUDA 12.6.

### Which Python version is required?

MaSIF requires Python 3.12. The code uses `tf.compat.v1` mode for compatibility with existing trained models.

### What TensorFlow version is used?

MaSIF uses TensorFlow 2.16.2 in `tf.compat.v1` compatibility mode with `tf.disable_eager_execution()`. This allows using GPU-enabled TensorFlow 2.x while maintaining compatibility with pre-trained models.

### Can I run MaSIF on Windows?

Yes, through:
1. WSL2 (Windows Subsystem for Linux)
2. Docker Desktop for Windows

Native Windows installation is not supported.

### How much disk space do I need?

- Software: ~10GB
- Per application dataset: ~400GB
- Per protein: ~25MB preprocessed data

---

## Usage Questions

### How do I run MaSIF on my own protein?

```bash
cd data/masif_site/
./data_prepare_one.sh --file /path/to/protein.pdb MYPDB_A
./predict_site.sh MYPDB_A
./color_site.sh MYPDB_A
```

### What's the naming convention for proteins?

| Format | Description | Example |
|--------|-------------|---------|
| `PDBID_CHAIN` | Single chain | `4ZQK_A` |
| `PDBID_CHAINS` | Multiple chains together | `4ZQK_AB` |
| `PDBID_CHAIN1_CHAIN2` | Protein pair | `1AKJ_AB_DE` |

### Can I process multiple proteins at once?

Yes, using batch processing:

```bash
# Sequential
for pdb in $(cat lists/my_proteins.txt); do
    ./data_prepare_one.sh $pdb
done

# Parallel (cluster)
sbatch data_prepare.slurm
```

### How long does preprocessing take?

~2 minutes per protein. Main bottlenecks:
- APBS electrostatics: ~30-60 sec
- Polar coordinate computation: ~20-30 sec
- Mesh regularization: ~10 sec

### Can I skip certain features?

Yes, modify the feature mask in configuration:

```python
# Use only geometric features
masif_opts["site"]["feat_mask"] = [1.0, 1.0, 0.0, 0.0, 0.0]
```

### How do I visualize results?

Use the PyMOL plugin:

```
# In PyMOL
loadply output/all_feat_3l/pred_surfaces/4ZQK_A.ply
```

Blue regions = high interaction probability

---

## Results Interpretation

### What do the prediction scores mean?

**MaSIF-site**: Per-vertex probability (0-1) of being in an interaction interface
- Score > 0.5: Likely interface
- Score < 0.3: Likely non-interface

**MaSIF-search**: 80-dimensional descriptor vectors
- Low Euclidean distance = complementary surfaces
- Distance < 1.5: Good match

**MaSIF-ligand**: Multi-class probability for 7 ligand types
- Highest probability class = predicted ligand type

### What's a good ROC AUC score?

- **0.9+**: Excellent prediction
- **0.8-0.9**: Good prediction
- **0.7-0.8**: Moderate prediction
- **<0.7**: Poor prediction

For MaSIF-site, expect ~0.85-0.92 on test proteins.

### Why is my ROC AUC low for new proteins?

The ROC AUC requires ground truth labels from the original complex structure. For truly unknown proteins, this metric isn't meaningful - use visual inspection instead.

### How do I interpret surface colors?

| Feature | Red | White | Blue |
|---------|-----|-------|------|
| Interface (iface) | Low probability | Medium | High probability |
| Electrostatics (pb) | Negative | Neutral | Positive |
| Hydrophobicity | Hydrophilic | Intermediate | Hydrophobic |
| Shape Index | Concave | Saddle | Convex |

### Can I trust predictions for any protein?

Best results for:
- Globular proteins with clear binding sites
- Proteins similar to training set
- High-quality structures (< 2.5Å resolution)

Be cautious with:
- Highly disordered regions
- Membrane proteins
- Very large complexes

---

## Performance Questions

### How can I speed up preprocessing?

1. **Use a cluster**: Distribute across multiple nodes
2. **Use precomputed data**: Download from Zenodo
3. **Reduce resolution**: Increase `mesh_res` (trades accuracy for speed)
4. **Skip features**: Disable APBS electrostatics if not needed

### How can I speed up training?

1. **Use GPU**: 10-100x faster than CPU
2. **Cache training data**: Use `cache_nn.sh` for MaSIF-search
3. **Use TFRecords**: Pre-convert to TensorFlow records
4. **Reduce dataset size**: Start with subset for testing

### Why is APBS so slow?

APBS solves the Poisson-Boltzmann equation numerically, which is computationally expensive. Options:
- Accept the delay (most accurate)
- Use precomputed data
- Disable electrostatics: `masif_opts["use_apbs"] = False`

### What GPU should I use?

MaSIF works with any NVIDIA GPU supporting CUDA 12.x:

- Minimum: GTX 1060 (6GB)
- Recommended: RTX 3080/4080 or Tesla A100
- For large batches: A100 or multi-GPU setup
- Tested on: NVIDIA RTX PRO 6000 Blackwell (98GB VRAM)

### How much memory do I need?

- **CPU RAM**: 16GB minimum, 32GB recommended
- **GPU VRAM**: 6GB minimum, 12GB+ for larger batches

---

## Research Questions

### Can I train on my own dataset?

Yes, follow these steps:
1. Prepare your protein list
2. Run data preparation on all proteins
3. Create training/validation/test splits
4. Run training scripts

See application-specific documentation for details.

### How do I add new features?

1. Create feature computation in `triangulation/computeNewFeature.py`
2. Modify `01-pdb_extract_and_triangulate.py` to compute feature
3. Update `masif_opts` with `use_new_feature` flag
4. Extend `feat_mask` to 6 elements
5. Retrain neural networks

### Can I modify the neural network architecture?

Yes, modify the `MaSIF_*.py` files in `source/masif_modules/`:
- Change number of layers
- Modify convolution parameters
- Add dropout or batch normalization
- Change descriptor dimensionality

### How do I cite MaSIF?

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

### Are there newer versions of MaSIF?

The version at github.com/LPDI-EPFL/masif is actively maintained. For exact paper reproduction, use the archived version at github.com/pablogainza/masif_paper.

### Can I use MaSIF for commercial purposes?

MaSIF is licensed under Apache 2.0, which allows commercial use with proper attribution. Consult with legal counsel for specific use cases.

### Where can I find training data?

- **Precomputed surfaces**: https://doi.org/10.5281/zenodo.2625420
- **PDB structures**: Download from RCSB PDB (www.rcsb.org)
- **Training lists**: Included in repository under `data/*/lists/`

---

## Still Have Questions?

- Check the [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/LPDI-EPFL/masif/issues)
- Read the [original paper](https://doi.org/10.1038/s41592-019-0666-6)
- Open a new issue with detailed information
