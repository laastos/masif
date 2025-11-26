masif_root=$(git rev-parse --show-toplevel)
masif_source=$masif_root/source/
masif_matlab=$masif_root/source/matlab_libs/
masif_data=$masif_root/data/
export PYTHONPATH=$PYTHONPATH:$masif_source:$masif_data/masif_ppi_search/
# Change to masif_ppi_search directory for relative model paths to work
cd $masif_data/masif_ppi_search/
python $masif_source/masif_ppi_search/masif_ppi_search_train.py $1
