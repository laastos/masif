masif_root=$(git rev-parse --show-toplevel)
masif_source=$masif_root/source/
masif_data=$masif_root/data/
export PYTHONPATH=$PYTHONPATH:$masif_source
# Change to masif_ppi_search directory for relative paths to work correctly
cd $masif_data/masif_ppi_search/
PDB_ID=$(echo $1| cut -d"_" -f1)
CHAIN1=$(echo $1| cut -d"_" -f2)
CHAIN2=$(echo $1| cut -d"_" -f3)
python $masif_source/data_preparation/00-pdb_download.py $1
python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py $PDB_ID\_$CHAIN1
# Only process second chain if it exists
if [ -n "$CHAIN2" ]; then
    python $masif_source/data_preparation/01-pdb_extract_and_triangulate.py $PDB_ID\_$CHAIN2
fi
python $masif_source/data_preparation/04-masif_precompute.py masif_ppi_search $1
