# Installing the MaSIF PyMOL Plugin

## Prerequisites

For full functionality (including patch visualization), install NetworkX:

```bash
pip install networkx
```

## Installation

To install the plugin go to the Plugin -> Plugin Manager window in PyMOL and choose the Install new plugin tab:

![MaSIF Install new plugin window](https://raw.githubusercontent.com/LPDI-EPFL/masif/master/img/ImageInitial.png)

Then select the masif/source/masif_pymol_plugin.zip file: 

![MaSIF Install new plugin window](https://raw.githubusercontent.com/LPDI-EPFL/masif/master/img/PluginSelect.png)

After this, pymol will prompt you for an installation directory. You can select the default path. 

Finally, close and reopen pymol. Go again to the plugin manager window and verify that masif pymol plugin is installed: 


![MaSIF Install new plugin window](https://raw.githubusercontent.com/LPDI-EPFL/masif/master/img/ImageVerify.png)


You can now test the installation of the plugin. For example, you can download any of the files in this link : 

https://github.com/LPDI-EPFL/masif/tree/master/comparison/masif_site/masif_vs_sppider/masif_pred

and then open them using the command (inside pymol):

```
loadply 4ETP_A.ply
```

## Available Commands

After installation, the following commands are available:

### Surface Loading
- `loadply filename.ply` - Load PLY surface with all features
- `loaddots filename` - Load surface as dot representation
- `loadgiface filename.ply` - Load interface with silhouette

### Patch Visualization
- `loadpatches filename.ply` - Compute and visualize interaction patches
- `loadpatches_json filename.ply, patches.json` - Load pre-computed patches
- `showpatch N` - Show/hide patch N
- `listpatches` - List loaded patch data

Example:
```
loadpatches protein.ply, top_k=50, radius=9.0, mode=spheres
```

See the [PyMOL Plugin Guide](docs/pymol-plugin.md) for detailed usage.

## Troubleshooting the plugin installation.

- Make sure that pymol can find the location where you installed the plugin. Another possibilty is to go to "Plugin Manager" within PyMOL and then click the "Settings" tab. There, click on "Add new directory" add the following directory:

```
masif/source/masif_plugin_pymol/
```

This should tell pymol to search this directory for plugins.


In addition, some solutions are provided in this thread to problems with the plugin, especially in windows: 

https://github.com/LPDI-EPFL/masif/issues/15
