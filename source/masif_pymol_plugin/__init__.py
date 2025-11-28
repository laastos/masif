# Pablo Gainza Cirauqui 2016 LPDI IBI STI EPFL
# This pymol plugin for Masif just enables the load ply functions.
# Extended with patch visualization functionality.

from pymol import cmd
from .loadPLY import (
    load_ply,
    load_giface,
    load_patches,
    load_patches_json,
    show_patch,
    color_patch,
    list_patches
)
from .loadDOTS import load_dots
import sys

def __init_plugin__(app):
    # Original MaSIF commands
    cmd.extend('loadply', load_ply)
    cmd.extend('loaddots', load_dots)
    cmd.extend('loadgiface', load_giface)

    # Patch visualization commands
    cmd.extend('loadpatches', load_patches)
    cmd.extend('loadpatches_json', load_patches_json)
    cmd.extend('showpatch', show_patch)
    cmd.extend('colorpatch', color_patch)
    cmd.extend('listpatches', list_patches)

