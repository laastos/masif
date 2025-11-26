# Quick Start Tutorial

This guide walks you through running your first MaSIF analysis in minutes.

## Prerequisites

- MaSIF installed (see [Installation Guide](installation.md))
- Or Docker installed for the containerized version

---

## Quick Start with Docker (Easiest)

### Step 1: Build and Start the Container

```bash
# Navigate to docker directory and build
cd docker/
docker build -t masif .

# Run the container
docker run -it masif
```

Alternatively, pull a pre-built image if available:
```bash
docker pull pablogainza/masif:latest
docker run -it pablogainza/masif
```

### Step 2: Run MaSIF-site on a Single Protein

The container includes convenient helper commands that can be run from anywhere:

```bash
# Prepare the protein (downloads PDB, computes surface and features)
masif-site prepare 4ZQK_A

# Run the neural network prediction
masif-site predict 4ZQK_A

# Generate colored surface for visualization
masif-site color 4ZQK_A
```

Or use the traditional method:
```bash
cd /masif/data/masif_site/
./data_prepare_one.sh 4ZQK_A
./predict_site.sh 4ZQK_A
./color_site.sh 4ZQK_A
```

### Step 3: View Results

The predictions are saved in:
- `output/all_feat_3l/pred_data/pred_4ZQK_A.npy` - Raw predictions
- `output/all_feat_3l/pred_surfaces/4ZQK_A.ply` - Colored surface file

Copy the surface file to your local machine:
```bash
# From your local terminal (not inside Docker)
docker cp <container_id>:/masif/data/masif_site/output/all_feat_3l/pred_surfaces/4ZQK_A.ply .
```

---

## Quick Start with Native Installation

### Step 1: Set Up Environment

```bash
# Activate your environment
conda activate masif  # or source masif_env/bin/activate

# Set up Python path (done automatically by scripts)
export masif_root=/path/to/masif
export PYTHONPATH=$PYTHONPATH:$masif_root/source
```

### Step 2: Navigate to Application Directory

```bash
cd $masif_root/data/masif_site/
```

### Step 3: Run the Analysis

```bash
# Prepare a single protein
./data_prepare_one.sh 4ZQK_A

# Run prediction
./predict_site.sh 4ZQK_A

# Generate visualization
./color_site.sh 4ZQK_A
```

---

## Understanding the Output

### Terminal Output Explained

```
Downloading PDB structure '4ZQK'...     # Downloads from RCSB PDB
Removing degenerated triangles          # MSMS surface cleanup
4ZQK_A
Reading data from input ply surface files.
Dijkstra took 2.28s                     # Geodesic distance computation
Only MDS time: 18.26s                   # Multidimensional scaling
Full loop time: 28.54s
MDS took 28.54s                         # Total coordinate computation
```

### Output Files

| File | Description |
|------|-------------|
| `data_preparation/00-raw_pdbs/4ZQK.pdb` | Downloaded PDB file |
| `data_preparation/01-benchmark_pdbs/4ZQK_A.pdb` | Extracted and protonated chain |
| `data_preparation/01-benchmark_surfaces/4ZQK_A.ply` | Triangulated surface with features |
| `data_preparation/04a-precomputation_9A/precomputation/4ZQK_A/` | Precomputed patches |
| `output/all_feat_3l/pred_data/pred_4ZQK_A.npy` | Neural network predictions |
| `output/all_feat_3l/pred_surfaces/4ZQK_A.ply` | Colored prediction surface |

---

## Example Workflows

### Workflow 1: Predict Interaction Sites (MaSIF-site)

```bash
cd data/masif_site/

# For a single chain
./data_prepare_one.sh 1ABC_A
./predict_site.sh 1ABC_A
./color_site.sh 1ABC_A

# For multiple chains (e.g., a complex)
./data_prepare_one.sh 1ABC_AB
./predict_site.sh 1ABC_AB
./color_site.sh 1ABC_AB
```

### Workflow 2: Compute Surface Descriptors (MaSIF-search)

```bash
cd data/masif_ppi_search/

# Prepare the protein pair
./data_prepare_one.sh 1AKJ_AB_DE

# Compute descriptors
./compute_descriptors.sh 1AKJ_AB

# Descriptors saved to descriptors/ directory
```

### Workflow 3: Using Your Own PDB File

```bash
cd data/masif_site/

# Use --file flag to specify a local PDB file
./data_prepare_one.sh --file /path/to/your/protein.pdb MYPDB_A

# Then run prediction as usual
./predict_site.sh MYPDB_A
```

---

## Naming Conventions

MaSIF uses a specific naming format for protein identifiers:

| Format | Description | Example |
|--------|-------------|---------|
| `PDBID_CHAIN` | Single chain | `4ZQK_A` |
| `PDBID_CHAINS` | Multiple chains as one surface | `4ZQK_AB` |
| `PDBID_CHAIN1_CHAIN2` | Protein pair | `1AKJ_AB_DE` |

### Examples

```bash
# Single chain A of PDB 4ZQK
./data_prepare_one.sh 4ZQK_A

# Chains A and B together as one surface
./data_prepare_one.sh 4ZQK_AB

# Protein pair: chains A,B interact with chains D,E
./data_prepare_one.sh 1AKJ_AB_DE
```

---

## Processing Multiple Proteins

### Sequential Processing

```bash
# Using a list file
for pdb in $(cat lists/testing.txt); do
    ./data_prepare_one.sh $pdb
done
```

### Parallel Processing (Cluster)

For large datasets, use the provided SLURM scripts:

```bash
# Submit batch job
sbatch data_prepare.slurm

# Monitor progress
squeue -u $USER
```

---

## Visualization with PyMOL

### Install the Plugin

1. Open PyMOL
2. Go to Plugin → Plugin Manager → Install New Plugin
3. Select `source/masif_pymol_plugin.zip`
4. Restart PyMOL

### Load a Surface

```
# In PyMOL command line
loadply 4ZQK_A.ply
```

### Viewing Different Features

After loading, multiple objects are created:
- `iface_4ZQK_A` - Interface predictions (most useful)
- `pb_4ZQK_A` - Electrostatics
- `hphobic_4ZQK_A` - Hydrophobicity
- `si_4ZQK_A` - Shape index

Toggle objects on/off to view different features.

---

## Next Steps

- Learn about [MaSIF-site](applications/masif-site.md) for interaction site prediction
- Explore [MaSIF-search](applications/masif-search.md) for surface matching
- Try [MaSIF-ligand](applications/masif-ligand.md) for binding pocket prediction
- Understand the [Data Preparation Pipeline](data-preparation.md)
- See all [Configuration Options](configuration.md)

---

## Common Issues

### "Command not found"

Ensure you're in the correct directory:
```bash
cd $masif_root/data/masif_site/
```

### "Module not found"

Check your Python path:
```bash
export PYTHONPATH=$PYTHONPATH:$masif_root/source
```

### Slow Processing

Data preparation is CPU-bound and takes ~2 minutes per protein. Use:
- Cluster computing for large datasets
- Precomputed data from [Zenodo](https://doi.org/10.5281/zenodo.2625420)
