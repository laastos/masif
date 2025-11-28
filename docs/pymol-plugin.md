# PyMOL Plugin Guide

The MaSIF PyMOL plugin enables visualization of protein molecular surfaces with computed features.

## Table of Contents

- [Installation](#installation)
- [Loading Surfaces](#loading-surfaces)
- [Understanding Surface Objects](#understanding-surface-objects)
- [Patch Visualization](#patch-visualization)
- [Color Schemes](#color-schemes)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Method 1: Plugin Manager (Recommended)

1. Open PyMOL
2. Go to **Plugin → Plugin Manager**
3. Select the **Install New Plugin** tab
4. Click **Choose file...** and select:
   ```
   masif/source/masif_pymol_plugin.zip
   ```
5. Accept the default installation directory
6. Restart PyMOL

### Method 2: Manual Installation

1. Locate your PyMOL plugin directory:
   ```bash
   # Linux
   ~/.pymol/startup/

   # macOS
   ~/Library/Application Support/PyMOL/startup/
   ```

2. Copy the plugin:
   ```bash
   unzip masif/source/masif_pymol_plugin.zip -d ~/.pymol/startup/
   ```

3. Restart PyMOL

### Verify Installation

In PyMOL, go to **Plugin → Plugin Manager** and verify "masif_pymol_plugin" appears in the list.

---

## Loading Surfaces

### Basic Usage

```
loadply filename.ply
```

Example:
```
loadply 4ZQK_A.ply
```

### Loading with Patches (Recommended)

Load surface and compute interaction patches in a single command:

```
# Load surface with default patches (top 100, radius 9.0Å)
loadply protein.ply, patches=1

# Custom patch parameters
loadply protein.ply, patches=1, top_k=50, patch_radius=12.0

# With mesh visualization instead of spheres
loadply protein.ply, patches=1, top_k=50, patch_mode=mesh

# Filter by interface score
loadply protein.ply, patches=1, iface_cutoff=0.5
```

This is more efficient than running `loadply` followed by `loadpatches` separately, as the mesh is only loaded once.

### Loading from Predictions

After running MaSIF-site predictions:

```bash
# In terminal
cd data/masif_site/
./color_site.sh 4ZQK_A
```

Then in PyMOL:
```
loadply output/all_feat_3l/pred_surfaces/4ZQK_A.ply
```

### Loading Multiple Surfaces

```
loadply protein1.ply
loadply protein2.ply
```

Each surface creates multiple objects with different visualizations.

---

## Understanding Surface Objects

When you load a PLY file, the plugin creates multiple PyMOL objects:

### Object Types

Objects are created only if the corresponding attribute exists in the PLY file.

| Prefix | Feature | PLY Attribute | Description |
|--------|---------|---------------|-------------|
| `mesh_` | Mesh | (always) | Triangulated surface wireframe |
| `vert_` | Vertices | (always) | Surface vertices as spheres |
| `pb_` | Electrostatics | `vertex_charge` | Poisson-Boltzmann potential |
| `hphobic_` | Hydrophobicity | `vertex_hphob` | Kyte-Doolittle scale |
| `iface_` | Interface | `vertex_iface` | Predicted interaction sites |
| `hbond_` | H-bonds | `vertex_hbond` | Hydrogen bond potential |
| `ddc_` | DDC | `vertex_ddc` | Distance-dependent curvature (optional) |
| `si_` | Shape Index | `vertex_si` | Local curvature measure |

**Note:** The `ddc_` (distance-dependent curvature) layer only appears if computed during preprocessing. Standard MaSIF-site output includes: `iface`, `charge`, `hbond`, `hphob`, `si`, and normals (`nx`, `ny`, `nz`).

### Viewing Different Features

```
# Show interface prediction
enable iface_4ZQK_A
disable mesh_4ZQK_A
disable pb_4ZQK_A

# Show electrostatics
enable pb_4ZQK_A
disable iface_4ZQK_A

# Show multiple features
enable iface_4ZQK_A
enable pb_4ZQK_A
set transparency, 0.5, pb_4ZQK_A
```

---

## Patch Visualization

The plugin includes functionality to visualize interaction patches on protein surfaces. Patches are local surface regions centered on each vertex, computed using geodesic distances.

### Dependencies

Patch visualization requires NetworkX:
```bash
pip install networkx
```

### Recommended: Integrated Loading

The easiest way to load surfaces with patches is using the `patches` parameter in `loadply`:

```
loadply protein.ply, patches=1, top_k=50
```

This loads the mesh once and computes patches immediately. See [Loading with Patches](#loading-with-patches-recommended) above.

### Alternative: Separate Commands

If you need to load patches separately (e.g., from a pre-computed JSON file), use these commands:

| Command | Description |
|---------|-------------|
| `loadpatches` | Compute and visualize patches on-the-fly |
| `loadpatches_json` | Load pre-computed patches from JSON file |
| `showpatch` | Show/hide individual patches |
| `listpatches` | List all loaded patch data |

### Computing Patches On-the-fly (Separate Command)

```
# Basic usage - top 100 patches with default settings
loadpatches protein.ply

# Customize parameters
loadpatches protein.ply, top_k=50, radius=9.0, mode=spheres

# Use mesh visualization (triangles instead of spheres)
loadpatches protein.ply, top_k=50, radius=9.0, mode=mesh

# Filter by iface score (only show patches with high interface probability)
loadpatches protein.ply, top_k=50, iface_cutoff=0.5

# Save computed patches to JSON for later use
loadpatches protein.ply, top_k=100, save_json=patches.json
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | 100 | Number of top patches to visualize |
| `radius` | 9.0 | Geodesic radius in Angstroms |
| `iface_cutoff` | 0.0 | Minimum iface score for patch center |
| `mode` | spheres | Visualization: 'spheres' or 'mesh' |
| `sphere_size` | 0.6 | Size of spheres (spheres mode only) |
| `save_json` | None | Optional path to save patches as JSON |

### Loading Pre-computed Patches

If you have pre-computed patches in JSON format:

```
loadpatches_json protein.ply, patch_results.json
loadpatches_json protein.ply, patch_results.json, mode=mesh
```

The JSON format follows this structure:
```json
{
  "centers": [vertex_indices...],
  "scores": [float_scores...],
  "vertex_indices": [[patch_1_vertices], [patch_2_vertices], ...]
}
```

### Managing Patches

```
# List all loaded patches
listpatches

# Show/hide individual patches
showpatch 5        # Show patch 5
showpatch 5, 0     # Hide patch 5

# Toggle all patches using PyMOL wildcards
disable patches_*  # Hide all patches
enable patches_*   # Show all patches

# Show only specific patch
disable patches_*
enable patch_3_*
```

### Visualization Modes

**Spheres Mode** (`mode=spheres`):
- Each vertex in the patch is shown as a colored sphere
- Fast rendering, good for quick inspection
- Distinct colors per patch for easy identification

**Mesh Mode** (`mode=mesh`):
- Patch region shown as colored triangles on the surface
- More integrated appearance with the molecular surface
- Only includes triangles where all vertices belong to the patch

### Patch Scoring

Patches are ranked by a weighted score based on surface features:
- **iface**: Interface probability (weight: 1.0)
- **charge**: Electrostatic potential (weight: 0.3)
- **hphob**: Hydrophobicity (weight: 0.5)
- **hbond**: Hydrogen bond potential (weight: 0.8)

Higher scores indicate more likely protein-protein interaction sites.

---

## Color Schemes

### Interface Predictions (iface_)

| Color | Meaning |
|-------|---------|
| Blue | Low interaction probability |
| White | Medium probability |
| Red | High interaction probability |

Typical threshold: > 0.5 indicates likely interface

### Electrostatics (pb_)

| Color | Meaning |
|-------|---------|
| Red | Negative charge (acidic) |
| White | Neutral |
| Blue | Positive charge (basic) |

Range: Typically -5 to +5 kT/e

### Hydrophobicity (hphobic_)

| Color | Meaning |
|-------|---------|
| White | Hydrophilic (polar) |
| Light Magenta | Intermediate |
| Magenta | Hydrophobic (nonpolar) |

Scale: Kyte-Doolittle (-4.5 to +4.5)

### Shape Index (si_)

Computed from mesh curvatures during surface triangulation.

| Color | Meaning |
|-------|---------|
| Red | Concave (cup-like, cavities) |
| White | Saddle (flat/intermediate) |
| Blue | Convex (dome-like, protrusions) |

Range: -1.0 to +1.0

### Hydrogen Bonds (hbond_)

| Color | Meaning |
|-------|---------|
| Red | H-bond acceptor (O, N) |
| White | No H-bond capability |
| Blue | H-bond donor (N-H, O-H) |

---

## Advanced Usage

### Custom Color Ranges

```
# Adjust electrostatics range
spectrum b, red_white_blue, pb_4ZQK_A, -3, 3

# Adjust interface threshold
spectrum b, red_white_blue, iface_4ZQK_A, 0, 1
```

### Transparency

```
# Make surface transparent
set transparency, 0.5, iface_4ZQK_A

# Fully opaque
set transparency, 0, iface_4ZQK_A
```

### Surface Representation

```
# Show as surface
show surface, iface_4ZQK_A

# Show as mesh
show mesh, mesh_4ZQK_A

# Show as dots
show dots, vert_4ZQK_A
```

### Combining with Protein Structure

```
# Load PLY surface
loadply 4ZQK_A.ply

# Load PDB structure
fetch 4ZQK
remove chain B C D  # Keep only chain A

# Show protein as cartoon
show cartoon, 4ZQK
hide everything, 4ZQK
show cartoon, 4ZQK

# Position surface with structure
align iface_4ZQK_A, 4ZQK and chain A
```

### Saving Images

```
# Set up view
bg_color white
set ray_trace_mode, 1

# Render and save
ray 2400, 2400
png output_image.png, dpi=300
```

### Additional Commands

#### loadgiface

Load interface with silhouette (boundary highlighting):

```
loadgiface 4ZQK_A.ply
```

#### loaddots

Load surface as dot representation:

```
loaddots 4ZQK_A.ply
```

---

## Troubleshooting

### Plugin Not Loading

1. **Regenerate the zip file** (if you updated the plugin):
   ```bash
   cd masif/source/
   zip -r masif_pymol_plugin.zip masif_pymol_plugin/
   ```
   Then reinstall in PyMOL.

2. **Check installation path**:
   ```
   # In PyMOL
   import sys
   print(sys.path)
   ```

3. **Add plugin directory manually**:
   - Go to Plugin Manager → Settings
   - Add: `masif/source/masif_pymol_plugin/`
   - Restart PyMOL

### "No module named 'loadPLY'" Error

This error occurs with older versions of the plugin that used Python 2 style imports.

**Solution**: Update to the latest version which uses Python 3 relative imports:
```bash
cd masif/
git pull  # Get latest fixes
cd source/
zip -r masif_pymol_plugin.zip masif_pymol_plugin/
```
Then reinstall the plugin in PyMOL.

### "loadply" Command Not Found

```
# Try manual import
run masif/source/masif_pymol_plugin/loadply.py
loadply 4ZQK_A.ply
```

### Surface Not Visible

1. **Check object list**: Look in the right panel for object names
2. **Enable the object**: Click on the object name or use `enable object_name`
3. **Check view**: Use `zoom` to center on the surface
4. **Check color**: Some features may be white on white background

### Colors Look Wrong

```
# Reset coloring
spectrum b, red_white_blue, iface_4ZQK_A

# Check attribute values
iterate iface_4ZQK_A, print(name, b)
```

### Surface and Structure Don't Align

The PLY surface should automatically align with the PDB structure if both were generated from the same coordinates. If not:

```
# Manual alignment
align iface_4ZQK_A, 4ZQK
```

### Windows-Specific Issues

See GitHub issue: https://github.com/LPDI-EPFL/masif/issues/15

Common fixes:
- Use forward slashes in paths
- Ensure no spaces in file paths
- Run PyMOL as administrator

---

## Example Visualization Script

```python
# masif_visualization.pml
# Run with: pymol masif_visualization.pml

# Load surface
loadply 4ZQK_A.ply

# Load structure
fetch 4ZQK
remove not chain A

# Set up visualization
hide everything
show cartoon, 4ZQK
enable iface_4ZQK_A

# Style
set cartoon_color, gray70, 4ZQK
bg_color white
set transparency, 0.3, iface_4ZQK_A

# Camera
zoom all
turn y, 45

# Labels
set label_size, 20
label 4ZQK and resi 45 and name CA, "Interface"

# Save
ray 1200, 1200
png masif_visualization.png
```

Run from command line:
```bash
pymol masif_visualization.pml
```
