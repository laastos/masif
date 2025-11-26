#!/bin/bash -l
masif_root=$(git rev-parse --show-toplevel)
masif_source=$masif_root/source/
masif_matlab=$masif_root/source/matlab_libs/
masif_data=$masif_root/data/
export PYTHONPATH=$PYTHONPATH:$masif_source
# Change to masif_ligand directory for relative model paths to work
cd $masif_data/masif_ligand/
python -u $masif_source/masif_ligand/masif_ligand_evaluate_test.py
