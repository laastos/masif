# PyMOL Plugin Guide

The MaSIF PyMOL plugin enables visualization of protein molecular surfaces with computed features.

## Table of Contents

- [Installation](#installation)
- [Loading Surfaces](#loading-surfaces)
- [Understanding Surface Objects](#understanding-surface-objects)
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

| Prefix | Feature | Description |
|--------|---------|-------------|
| `mesh_` | Mesh | Triangulated surface wireframe |
| `vert_` | Vertices | Surface vertices as spheres |
| `pb_` | Electrostatics | Poisson-Boltzmann potential |
| `hphobic_` | Hydrophobicity | Kyte-Doolittle scale |
| `si_` | Shape Index | Local curvature measure |
| `ddc_` | DDC | Distance-dependent curvature |
| `iface_` | Interface | Predicted interaction sites |
| `hbond_` | H-bonds | Hydrogen bond potential |

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

## Color Schemes

### Interface Predictions (iface_)

| Color | Meaning |
|-------|---------|
| Red | Low interaction probability |
| White | Medium probability |
| Blue | High interaction probability |

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
| Purple/Magenta | Hydrophilic (polar) |
| White | Intermediate |
| Yellow/Orange | Hydrophobic (nonpolar) |

Scale: Kyte-Doolittle (-4.5 to +4.5)

### Shape Index (si_)

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
