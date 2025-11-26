# Configuration Reference

Complete reference for all MaSIF configuration parameters.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Global Parameters](#global-parameters)
- [MaSIF-site Parameters](#masif-site-parameters)
- [MaSIF-search Parameters](#masif-search-parameters)
- [MaSIF-ligand Parameters](#masif-ligand-parameters)
- [Environment Variables](#environment-variables)
- [Custom Parameters](#custom-parameters)

---

## Configuration Overview

### Configuration File Location

Main configuration: `source/default_config/masif_opts.py`

### Configuration Structure

```python
masif_opts = {
    # Global parameters
    "raw_pdb_dir": "...",
    "mesh_res": 1.0,
    ...

    # Application-specific parameters
    "site": {...},
    "ppi_search": {...},
    "ligand": {...}
}
```

### Loading Configuration

```python
from default_config.masif_opts import masif_opts

# Access global parameter
mesh_resolution = masif_opts["mesh_res"]

# Access application-specific parameter
site_radius = masif_opts["site"]["max_distance"]
```

---

## Global Parameters

### Directory Paths

| Parameter | Default | Description |
|-----------|---------|-------------|
| `raw_pdb_dir` | `data_preparation/00-raw_pdbs/` | Downloaded PDB files |
| `pdb_chain_dir` | `data_preparation/01-benchmark_pdbs/` | Extracted chain PDBs |
| `ply_chain_dir` | `data_preparation/01-benchmark_surfaces/` | PLY surface files |
| `tmp_dir` | System temp dir | Temporary files |
| `ply_file_template` | `{ply_chain_dir}/{}_{}.ply` | Surface file naming |

### Surface Feature Flags

| Parameter | Default | Description |
|-----------|---------|-------------|
| `use_hbond` | `True` | Compute hydrogen bond features |
| `use_hphob` | `True` | Compute hydrophobicity features |
| `use_apbs` | `True` | Compute APBS electrostatics |
| `compute_iface` | `True` | Compute interface labels |

### Mesh Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mesh_res` | `1.0` | Target mesh resolution (Å) |
| `feature_interpolation` | `True` | Interpolate features on regularized mesh |

### Coordinate Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `radius` | `12.0` | Default geodesic patch radius (Å) |

---

## MaSIF-site Parameters

Parameters for protein-protein interaction site prediction.

### File Paths

```python
masif_opts["site"]["training_list"] = "lists/training.txt"
masif_opts["site"]["testing_list"] = "lists/testing.txt"
masif_opts["site"]["masif_precomputation_dir"] = "data_preparation/04a-precomputation_9A/precomputation/"
masif_opts["site"]["model_dir"] = "nn_models/all_feat_3l/model_data/"
masif_opts["site"]["out_pred_dir"] = "output/all_feat_3l/pred_data/"
masif_opts["site"]["out_surf_dir"] = "output/all_feat_3l/pred_surfaces/"
```

### Network Architecture

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_shape_size` | `100` | Maximum vertices per patch |
| `max_distance` | `9.0` | Patch radius (Å) |
| `n_conv_layers` | `3` | Number of geodesic convolution layers |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `range_val_samples` | `0.9` | Validation split point (0.9 to 1.0) |
| `feat_mask` | `[1.0, 1.0, 1.0, 1.0, 1.0]` | Feature importance weights |

### Feature Mask Explanation

The `feat_mask` array controls which features are used:

| Index | Feature | Description |
|-------|---------|-------------|
| 0 | Shape index | Local surface curvature |
| 1 | DDC | Distance-dependent curvature |
| 2 | Hydrophobicity | Kyte-Doolittle scale |
| 3 | H-bond | Hydrogen bond potential |
| 4 | Charges | Electrostatic potential |

Set to `0.0` to disable a feature:

```python
# Use only geometric features
masif_opts["site"]["feat_mask"] = [1.0, 1.0, 0.0, 0.0, 0.0]
```

---

## MaSIF-search Parameters

Parameters for surface fingerprint matching.

### File Paths

```python
masif_opts["ppi_search"]["training_list"] = "lists/training.txt"
masif_opts["ppi_search"]["testing_list"] = "lists/testing.txt"
masif_opts["ppi_search"]["masif_precomputation_dir"] = "data_preparation/04b-precomputation_12A/precomputation/"
masif_opts["ppi_search"]["cache_dir"] = "nn_models/sc05/cache/"
masif_opts["ppi_search"]["model_dir"] = "nn_models/sc05/all_feat/model_data/"
masif_opts["ppi_search"]["desc_dir"] = "descriptors/sc05/all_feat/"
masif_opts["ppi_search"]["gif_descriptors_out"] = "gif_descriptors/"
```

### Network Architecture

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_shape_size` | `200` | Maximum vertices per patch |
| `max_distance` | `12.0` | Patch radius (Å) |

### Shape Complementarity

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_sc_filt` | `1.0` | Maximum SC for filtering |
| `min_sc_filt` | `0.5` | Minimum SC for positive pairs |
| `sc_radius` | `12.0` | Radius for SC computation (Å) |
| `sc_interaction_cutoff` | `1.5` | Distance cutoff for interface (Å) |
| `sc_w` | `0.25` | SC weighting factor |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pos_surf_accept_probability` | `1.0` | Positive sample rate |
| `pos_interface_cutoff` | `1.0` | Interface distance cutoff |
| `range_val_samples` | `0.9` | Validation split point |
| `feat_mask` | `[1.0, 1.0, 1.0, 1.0, 1.0]` | Feature weights |

---

## MaSIF-ligand Parameters

Parameters for ligand binding pocket prediction.

### File Paths

```python
masif_opts["ligand"]["assembly_dir"] = "data_preparation/00b-pdbs_assembly"
masif_opts["ligand"]["ligand_coords_dir"] = "data_preparation/00c-ligand_coords"
masif_opts["ligand"]["masif_precomputation_dir"] = "data_preparation/04a-precomputation_12A/precomputation/"
masif_opts["ligand"]["tfrecords_dir"] = "data_preparation/tfrecords"
masif_opts["ligand"]["model_dir"] = "nn_models/all_feat/"
masif_opts["ligand"]["test_set_out_dir"] = "test_set_predictions/"
```

### Network Architecture

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_shape_size` | `200` | Maximum vertices per patch |
| `max_distance` | `12.0` | Patch radius (Å) |
| `n_classes` | `7` | Number of ligand classes |

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `train_fract` | `0.72` | Training set fraction |
| `val_fract` | `0.08` | Validation set fraction |
| `test_fract` | `0.20` | Test set fraction |
| `costfun` | `"dprime"` | Cost function (dprime/crossent) |
| `feat_mask` | `[1.0, 1.0, 1.0, 1.0, 1.0]` | Feature weights |

---

## Environment Variables

Required environment variables for external tools.

### Tool Binaries

| Variable | Description | Example Path |
|----------|-------------|--------------|
| `MSMS_BIN` | MSMS executable | `/tools/msms/msms` |
| `PDB2XYZRN` | PDB to XYZRN converter | `/tools/msms/pdb_to_xyzrn` |
| `APBS_BIN` | APBS executable | `/tools/APBS-1.5/bin/apbs` |
| `MULTIVALUE_BIN` | APBS multivalue tool | `/tools/APBS-1.5/share/apbs/tools/bin/multivalue` |
| `PDB2PQR_BIN` | PDB2PQR executable | `/tools/pdb2pqr-2.1.1/pdb2pqr` |

### Reduce Tool

| Variable | Description | Example Path |
|----------|-------------|--------------|
| `REDUCE_HET_DICT` | Reduce heterogen dictionary | `/tools/reduce/reduce_wwPDB_het_dict.txt` |

The `reduce` binary should be in `PATH`.

### PyMesh

| Variable | Description | Example Path |
|----------|-------------|--------------|
| `PYMESH_PATH` | PyMesh installation directory | `/tools/PyMesh` |

### Setting Environment Variables

```bash
# Add to ~/.bashrc or ~/.bash_profile
export MSMS_BIN=/path/to/msms/msms
export PDB2XYZRN=/path/to/msms/pdb_to_xyzrn
export APBS_BIN=/path/to/apbs/bin/apbs
export MULTIVALUE_BIN=/path/to/apbs/share/apbs/tools/bin/multivalue
export PDB2PQR_BIN=/path/to/pdb2pqr/pdb2pqr
export PATH=$PATH:/path/to/reduce/
export REDUCE_HET_DICT=/path/to/reduce/reduce_wwPDB_het_dict.txt
export PYMESH_PATH=/path/to/PyMesh
```

---

## Custom Parameters

### Creating Custom Parameter Files

Each neural network model can have a `custom_params.py` file:

```python
# nn_models/my_model/custom_params.py
custom_params = {}
custom_params['n_conv_layers'] = 4
custom_params['model_dir'] = 'nn_models/my_model/model_data/'
custom_params['out_pred_dir'] = 'output/my_model/pred_data/'
custom_params['out_surf_dir'] = 'output/my_model/pred_surfaces/'
```

### Loading Custom Parameters

```bash
# In shell scripts
./predict_site.sh nn_models.my_model.custom_params 4ZQK_A

# In Python
import importlib
custom = importlib.import_module('nn_models.my_model.custom_params')
params.update(custom.custom_params)
```

### Parameter Override Hierarchy

1. Default values in `masif_opts.py`
2. Application-specific values (`masif_opts["site"]`, etc.)
3. Custom parameters from `custom_params.py`
4. Command-line arguments (where applicable)

---

## Configuration Examples

### Minimal MaSIF-site Configuration

```python
# For basic site prediction
masif_opts["site"]["max_distance"] = 9.0
masif_opts["site"]["max_shape_size"] = 100
masif_opts["site"]["n_conv_layers"] = 3
```

### Feature Ablation Study

```python
# Shape features only
masif_opts["site"]["feat_mask"] = [1.0, 1.0, 0.0, 0.0, 0.0]

# Chemical features only
masif_opts["site"]["feat_mask"] = [0.0, 0.0, 1.0, 1.0, 1.0]
```

### High-Resolution Surface

```python
# Finer mesh (slower preprocessing)
masif_opts["mesh_res"] = 0.5

# More vertices per patch
masif_opts["site"]["max_shape_size"] = 200
```

### Custom Training Split

```python
# 80/10/10 split
masif_opts["ligand"]["train_fract"] = 0.80
masif_opts["ligand"]["val_fract"] = 0.10
masif_opts["ligand"]["test_fract"] = 0.10
```

---

## Validation

### Checking Configuration

```python
from default_config.masif_opts import masif_opts

def validate_config():
    """Validate configuration parameters."""

    # Check directory existence
    import os
    for key in ['raw_pdb_dir', 'pdb_chain_dir', 'ply_chain_dir']:
        if not os.path.exists(masif_opts[key]):
            print(f"Warning: {key} directory does not exist")

    # Check feature mask dimensions
    for app in ['site', 'ppi_search', 'ligand']:
        if len(masif_opts[app]['feat_mask']) != 5:
            print(f"Error: {app} feat_mask must have 5 elements")

    # Check radius values
    if masif_opts['site']['max_distance'] != 9.0:
        print("Warning: MaSIF-site expects 9Å radius")

    if masif_opts['ppi_search']['max_distance'] != 12.0:
        print("Warning: MaSIF-search expects 12Å radius")

validate_config()
```

### Environment Variable Check

```bash
#!/bin/bash
# check_env.sh - Verify environment variables

required_vars=(
    "MSMS_BIN"
    "PDB2XYZRN"
    "APBS_BIN"
    "MULTIVALUE_BIN"
    "PDB2PQR_BIN"
    "REDUCE_HET_DICT"
    "PYMESH_PATH"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Missing: $var"
    else
        if [ ! -f "${!var}" ] && [ ! -d "${!var}" ]; then
            echo "Invalid path: $var = ${!var}"
        else
            echo "OK: $var"
        fi
    fi
done
```
