![MaSIF banner and concept](https://raw.githubusercontent.com/LPDI-EPFL/masif/master/img/Concept-01.png)

# Docker tutorial for MaSIF.

## Table of Contents:

- [Installation](#Installation)
- [MaSIF-site](#MaSIF-site)
    * [Running MaSIF-site on a single protein from a PDB id or PDB file](#Running-MaSIF-site-on-a-single-protein-from-a-PDB-id)
    * [Reproducing the transient benchmark from the paper](#Reproducing-the-transient-benchmark-from-the-paper)
- [MaSIF-search](#MaSIF-search)
    * [GIF Descriptors](#GIF-Descriptors)
- [MaSIF-PDL1-benchmark](#MaSIF-PDL1-benchmark)
- [MaSIF-ligand](#MaSIF-ligand)
    * [Overview](#MaSIF-ligand-Overview)
    * [Data Preparation](#MaSIF-ligand-Data-Preparation)
    * [Training](#MaSIF-ligand-Training)
    * [Evaluation](#MaSIF-ligand-Evaluation)
- [MaSIF-peptides](#MaSIF-peptides)
    * [Overview](#MaSIF-peptides-Overview)
    * [Helix Extraction](#Helix-Extraction)
    * [Running Predictions](#MaSIF-peptides-Predictions)
- [Comparison and Benchmark Tools](#Comparison-and-Benchmark-Tools)
    * [MaSIF-site Comparisons](#MaSIF-site-Comparisons)
    * [MaSIF-search Comparisons](#MaSIF-search-Comparisons)
    * [MaSIF-ligand Comparisons](#MaSIF-ligand-Comparisons)
- [PyMOL Plugin](#PyMOL-Plugin)
    * [Installation](#PyMOL-Plugin-Installation)
    * [Surface Features and Visualization](#Surface-Features-and-Visualization)
    * [Color Schemes](#Color-Schemes)
- [Building Docker MaSIF image from a Dockerfile](#Dockerfile)



## Installation

```bash
docker pull pablogainza/masif:latest
docker run -it pablogainza/masif
```

You now start a local container with MaSIF. The first step should be to update the repository to make sure you have the latest version (in case the image has not been updated):

```bash
root@b30c52bcb86f:/masif# git pull
```

Alternatively, build from the included Dockerfile (see [Building Docker MaSIF image from a Dockerfile](#Dockerfile)).

**Note:** This container runs in CPU-only mode. For future GPU support with modern NVIDIA GPUs (Blackwell architecture, CUDA 12+), see `CUDA_UPDATE_PLAN.md`.

## MaSIF-site

### Running MaSIF-site on a single protein from a PDB id

Go into the MaSIF site data directory. 
```
root@b30c52bcb86f:/masif# cd data/masif_site/
root@b30c52bcb86f:/masif/data/masif_site# 
```

We will now run MaSIF site on chain A of PDB id 4ZQK. It is important to always input a chain and a PDB id. The first step consists of preparing the data and it is the slowest part of the process. It consists of downloading the pdb, extracting the chain, protonating it, computing the molecular surface and PB electrostatics, and decomposing the protein into patches (about 1 minute on a 120 residue protein): 

```
root@b30c52bcb86f:/masif/data/masif_site# ./data_prepare_one.sh 4ZQK_A
Downloading PDB structure '4ZQK'...
Removing degenerated triangles
Removing degenerated triangles
4ZQK_A
Reading data from input ply surface files.
Dijkstra took 2.28s
Only MDS time: 18.26s
Full loop time: 28.54s
MDS took 28.54s
```

If you want to run a prediction on multiple chains (e.g. a multidomain protein) you can do so by concatenting all chains (e.g., 4ZQK_AB). You can also run this command on a specific file (i.e. not on a downloaded file) using the --file flag: 

```
root@b30c52bcb86f:/masif/data/masif_site# ./data_prepare_one.sh --file /path/to/myfile/4ZQK.pdb 4ZQK_A
```

The next step consists of actually running the protein through the neural network to predict interaction sites: 

```
root@b30c52bcb86f:/masif/data/masif_site# ./predict_site.sh 4ZQK_A
Setting model_dir to nn_models/all_feat_3l/model_data/
Setting feat_mask to [1.0, 1.0, 1.0, 1.0, 1.0]
Setting n_conv_layers to 3
Setting out_pred_dir to output/all_feat_3l/pred_data/
Setting out_surf_dir to output/all_feat_3l/pred_surfaces/
(12, 2)
...
Total number of patches for which scores were computed: 2336

Inference time: 1.890s
```

After this step you can find the predictions in numpy files:

```
root@b30c52bcb86f:/masif/data/masif_site# ls output/all_feat_3l/pred_data
pred_4ZQK_A.npy
root@b30c52bcb86f:/masif/data/masif_site/#
```

Finally you can run a command to output a ply file with the predicted interface for visualization. A ROC AUC is also computed, but it is only accurate if the protein was found in the original complex (the ground truth is extracted from there):

```
root@b30c52bcb86f:/masif/data/masif_site# ./color_site.sh 4ZQK_A
Setting model_dir to nn_models/all_feat_3l/model_data/
Setting feat_mask to [1.0, 1.0, 1.0, 1.0, 1.0]
Setting n_conv_layers to 3
Setting out_pred_dir to output/all_feat_3l/pred_data/
Setting out_surf_dir to output/all_feat_3l/pred_surfaces/
ROC AUC score for protein 4ZQK_A : 0.91
Saving output/all_feat_3l/pred_surfaces/4ZQK_A.ply
Computed 1 proteins
Median ROC AUC score: 0.9137235650273854
root@b30c52bcb86f:/masif/data/masif_site#
```

If you have installed the pymol plugin for MaSIF, you can now visualize the predictions. From your local computer run: 

``` 
docker cp b30c52bcb86f:/masif/data/masif_site/output/all_feat_3l/pred_surfaces/4ZQK_A.ply .
```

```
pymol
```

Then from the pymol command window run: 

```
loadply 4ZQK_A.ply 
```

Then deactivate all objects except the one with 'iface' as part of its name. You should see something like this: 

![MaSIF PyMOL plugin example](https://raw.githubusercontent.com/LPDI-EPFL/masif/master/img/masif_plugin_example_2.png)



### Reproducing the transient benchmark from the paper

All the MaSIF-site experiments from the paper should be reproducible using the Docker container. For convenience, I have provided a script to reproduce the transient PPI interaction prediction benchmark, which is the one that is compared to state-of-the-art tools (SPPIDER, PSIVER).

```
cd data/masif_site
./reproduce_transient_benchmark.sh
```

This process takes about 2 hours, since there are ~60 proteins and they take about 2 minutes to run per protein.

### Retraining the neural network from zero. 

In order to retrain the neural network from zero, I strongly recommend using a cluster to precompute the data. It will take about 5 days in a single CPU to preprocess all the data. Ideally, one would instead use a cluster. However, if a cluster is not available you can precompute all data by running the commands: 

```
cd data/masif_site
./data_prepare_all.sh
```
Then, one can train the neural network: 

```
./train_nn.sh
```

## MaSIF-search

### Reproducing the MaSIF-ppi-search bound docking benchmark.

This section describes the fast docking benchmark presented in our paper (Table 1).

#### Fastest and easiest way to reproduce this benchmark. 

The fastest way to reproduce this benchmark is to download all the precomputed data from the following site: 
https://www.dropbox.com/s/09fwtic1095z9z6/masif_ppi_search_precomputed_data.tar.gz?dl=0

Run the masif container and download the data: 
```
docker run -it pablogainza/masif
cd data/masif_ppi_search/
wget https://www.dropbox.com/s/09fwtic1095z9z6/masif_ppi_search_precomputed_data.tar.gz?dl=0
tar cvfz masif_ppi_search_precomputed_data.tar.gz
```

Change the directory to the benchmark directory and run the benchmark for a number of decoys K (e.g. 100 or 2000 as in the paper): 

``` 
cd ../../comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100
```

The results should be the last line of the results_masif.txt file. 

#### Recomputing the data for the benchmark 

If you wish, you can also reproduce the benchmark data. I have conveniently left a script to recompute the data: 

```
docker run -it pablogainza/masif
cd data/masif_ppi_search/
././recompute_data_docking_benchmark.sh
```

This should take about 3 minutes per protein. For a total of 100 protein pairs it may take a few hours.

Finally change the directory to the benchmark directory and run the benchmark for a number of decoys K (e.g. 100 or 2000 as in the paper): 

```
cd ../../comparison/masif_ppi_search/masif_descriptors_nn/
./second_stage_masif.sh 100
```

#### Recomputing all training data and retraining the network.

For this task I strongly recommend a cluster to do the precomputation because there are about 10000 proteins per cluster. The steps to recompute and retrain are laid out in the main MaSIF readme.

[MaSIF Readme](Readme.md)

### Reproducing the MaSIF-ppi-search unbound docking benchmark.

#### Fastest and easiest way to reproduce this benchmark. 

Similar as for the bound: 

```
docker run -it pablogainza/masif
cd data/masif_ppi_search_ub/
wget https://www.dropbox.com/s/5w46ankuk3y2edo/masif_ppi_search_ub_precomputed_data.tar.gz?dl=0
tar cvfz masif_ppi_search_ub_precomputed_data.tar.gz
```

Change the directory to the benchmark directory and run the benchmark for a number of decoys K (e.g. 2000 as in the paper): 

``` 
cd ../../comparison/masif_ppi_search_ub/masif_descriptors_nn/
./second_stage_masif.sh 2000
```

#### Recomputing the data for the benchmark 

If you wish, you can also reproduce the benchmark data. I have conveniently left a script to recompute the data: 

```
docker run -it pablogainza/masif
cd data/masif_ppi_search_ub/
./recompute_data_docking_benchmark.sh
```

This should take about 3 minutes per protein. For a total of 40 protein pairs it may take a few hours.

Finally change the directory to the benchmark directory and run the benchmark for a number of decoys K (e.g. 2000 as in the paper): 

```bash
cd ../../comparison/masif_ppi_search_ub/masif_descriptors_nn/
./second_stage_masif.sh 2000
```

### GIF Descriptors

GIF (Geometric Invariant Fingerprints) descriptors provide a faster alternative to neural network-based descriptors. They are based on geometric invariants (Yin et al. PNAS 2009).

#### Computing GIF Descriptors

```bash
cd data/masif_ppi_search/
./compute_gif_descriptors.sh lists/ransac_benchmark_list.txt
```

For a single protein:

```bash
./compute_gif_descriptors.sh 4ZQK_A
```

#### Evaluating GIF Descriptors

```bash
cd comparison/masif_ppi_search/gif_descriptors/
./second_stage_gif.sh 100
```

GIF descriptors are faster to compute but may have slightly lower accuracy compared to neural network descriptors. They are useful for:
- Quick prototyping and testing
- Large-scale screening where speed is critical

## MaSIF PDL1 benchmark

In the paper we present a benchmark to scan ~11000 proteins for the binder of PD-L1 (taken from the co-crystal structure). This benchmark is very fast - finishes in minutes. The benchmark works as follows: 

(a) First, based on the MaSIF-site predictions, the center of the interface for PD-L1 is chosen. 

(b) Then, the fingerprint for that point is matched to the fingerprints o ftens of millions of patches from the database of 11000 proteins, and those that are within a *cutoff* are selected for further processing. 

(c) each patch that passes the fingerprint is aligned and scored with a neural network. 

For convenience, I have uploaded all the preprocessed data to Dropbox (eventually this will be replaced by a Zenodo link): 
https://www.dropbox.com/s/aaf5nt6smbrx8p7/masif_pdl1_benchmark_precomputed_data.tar?dl=0

Steps to reproduce the benchmark. 

Download the compressed data files to your local machine and unpack. You must make a temporary directory in your host machine to download a large file (about 30GB) which will contain the benchmark data. Here this directory is called '/your/temporary/path/docker_files/'.

```
mkdir /your/temporary/path/docker_files/
wget https://www.dropbox.com/s/aaf5nt6smbrx8p7/masif_pdl1_benchmark_precomputed_data.tar?dl=0
tar xvf masif_pdl1_benchmark_precomputed_data.tar
rm masif_pdl1_benchmark_precomputed_data.tar
```

You should now have a list of compressed tar.gz files. 

Start the docker container for masif, linking the directory in your host machine. 

``` 
docker run -it -v /your/temporary/path/docker_files/:/var/docker_files/ pablogainza/masif
```

Pull the latest version from the masif repository 

```
root@b30c52bcb86f:/masif# git pull 
```

Go into the pdl1 benchmark data directory and untar all the downloaded data files:

```
cd data/masif_pdl1_benchmark/
tar xvfz /var/docker_files/4ZQK_p1_desc_flipped.tar.gz -C .
tar xvfz /var/docker_files/4ZQK_surf_pred.tar.gz -C .
tar xvfz /var/docker_files/list_indices.tar.gz -C .
tar xvfz /var/docker_files/masif_search_descriptors.tar.gz -C .
tar xvfz /var/docker_files/masif_site_predictions.tar.gz -C .
tar xvfz /var/docker_files/pdbs.tar.gz -C .
tar xvfz /var/docker_files/plys.tar.gz -C .
```

The -C flag force the unpacking to occur in the current directory. Finally run the benchmark.

```
./run_benchmark_nn.sh 
```

This takes some time to run (~30 minutes). After this you can sort scores: 

```
cat log.txt | sort -k 2 -n 
```
You can also visualize the top candidates who were all stored in the ```out/``` directory. 


*** A note on descriptors distance *** A critical value now is the *cutoff* used for masif-search's fingerprint distance. In general, and as explained in the paper, the lower the cutoff, the less the number of results, and therefore the faster the run. By default, the value is set here at 1.7, which works well for this dataset. However, it may be possible that you need to relax this further (to, say, 2.0 or 2.2). You can try different values. 

You can run this protocol on your protein of interest as well. In general, for it to work you need a target with a high shape complementarity, and one in which MaSIF correctly labels the site. You probably may also have to play with the descriptor distance parameters. 

## MaSIF-ligand

### MaSIF-ligand Overview

MaSIF-ligand predicts ligand binding pockets on protein surfaces. It is trained to identify binding sites for seven common ligands:

| Ligand | Full Name |
|--------|-----------|
| ADP | Adenosine Diphosphate |
| COA | Coenzyme A |
| FAD | Flavin Adenine Dinucleotide |
| HEM | Heme |
| NAD | Nicotinamide Adenine Dinucleotide |
| NAP | NADP |
| SAM | S-Adenosyl Methionine |

### MaSIF-ligand Data Preparation

MaSIF-ligand requires Python 2.7 with the SBI library for generating biological assemblies. The data preparation workflow is:

```bash
cd data/masif_ligand/
./data_prepare_one.sh 1ABC_A_ADP
```

The naming convention is `{PDB_ID}_{CHAIN}_{LIGAND}`. For example, `1MBN_A_HEM` for myoglobin chain A with heme.

The preparation script performs:
1. Downloads the PDB structure
2. Generates biological assembly (using SBI library, Python 2.7)
3. Saves ligand coordinates
4. Extracts and triangulates the molecular surface
5. Precomputes surface patches

**Note:** The SBI library requires Python 2.7 and is only needed for generating biological assemblies. It is pre-installed in the Docker container.

### MaSIF-ligand Training

To retrain the neural network (requires preprocessed data):

```bash
cd data/masif_ligand/
# First prepare all training data
./data_prepare_all.sh

# Create TensorFlow records
python $masif_source/masif_ligand/masif_ligand_make_tfrecord.py

# Train the model
python $masif_source/masif_ligand/masif_ligand_train.py
```

### MaSIF-ligand Evaluation

To evaluate the model on the test set:

```bash
cd data/masif_ligand/
./evaluate_test.sh
```

This runs predictions on all test proteins and outputs accuracy metrics for each ligand type.

#### Interpreting Results

The evaluation outputs:
- Per-ligand classification accuracy
- Confusion matrix showing predicted vs. actual ligand types
- ROC AUC scores for each ligand class

Results are saved in the `output/` directory.

## MaSIF-peptides

### MaSIF-peptides Overview

MaSIF-peptides extends the MaSIF framework to analyze helical peptide binding sites on protein surfaces. It combines MaSIF-site for interface prediction and MaSIF-search for fingerprint matching of helical peptide binders.

### Helix Extraction

The first step extracts helical regions from protein structures:

```bash
cd data/masif_peptides/
./data_extract_helix_one.sh 1ABC_A
```

This script:
1. Downloads the PDB structure
2. Identifies helical regions using DSSP
3. Extracts and triangulates the molecular surface of helical segments

### Precomputing Patches

After helix extraction, precompute the surface patches:

```bash
./data_precompute_patches_one.sh 1ABC_A
```

This generates patches for both MaSIF-site (9Å radius) and MaSIF-search (12Å radius) applications.

### MaSIF-peptides Predictions

Run site predictions:

```bash
./predict_site.sh 1ABC_A
```

Compute descriptors for peptide matching:

```bash
./compute_descriptors.sh 1ABC_A
```

The workflow produces:
- Interface probability scores for each surface point
- Fingerprint descriptors for matching against peptide databases

## Comparison and Benchmark Tools

MaSIF includes comparison scripts for benchmarking against other methods.

### MaSIF-site Comparisons

Compare MaSIF-site with SPPIDER and other interface prediction tools:

```bash
cd comparison/masif_site/masif_vs_sppider/
# Contains scripts for comparative analysis
```

Available comparisons:
- **SPPIDER**: Sequence-based interface predictor
- **PSIVER**: Machine learning interface predictor
- **IntPred**: Integrated interface prediction

### MaSIF-search Comparisons

Compare MaSIF-search with docking tools:

```bash
cd comparison/masif_ppi_search/
```

**ZDOCK comparison:**

```bash
cd zdock/
./dock_all.sh    # Run ZDOCK on benchmark set
./eval_all.sh    # Evaluate ZDOCK results
```

**PatchDock comparison:**

```bash
cd patchdock/
./eval_all.sh    # Evaluate PatchDock results
```

**ZRANK scoring:**

```bash
cd zrank/
./run_all.sh     # Re-score docking poses with ZRANK
```

### MaSIF-ligand Comparisons

Compare with ligand binding site prediction methods:

```bash
cd comparison/masif_ligand/
```

Available comparisons:
- **Kripo**: Pharmacophore-based pocket comparison
- **ProBiS**: Protein binding site detection

```bash
./run_probis.sh  # Run ProBiS comparison
./run_all.sh     # Run all comparisons
```

## PyMOL Plugin

### PyMOL Plugin Installation

The MaSIF PyMOL plugin enables visualization of molecular surfaces with computed features.

1. Open PyMOL and go to **Plugin → Plugin Manager**
2. Select the **Install New Plugin** tab
3. Choose the file `source/masif_pymol_plugin.zip`
4. Accept the default installation directory
5. Restart PyMOL

Verify installation in **Plugin Manager** - you should see "masif_pymol_plugin" listed.

### Surface Features and Visualization

Load a surface file:

```
loadply 4ZQK_A.ply
```

The plugin creates multiple visualization objects:

| Object Prefix | Feature | Description |
|---------------|---------|-------------|
| `vert_` | Vertices | Surface points as spheres |
| `pb_` | Electrostatics | Poisson-Boltzmann surface charges |
| `hphobic_` | Hydrophobicity | Kyte-Doolittle hydrophobicity |
| `si_` | Shape Index | Local curvature descriptor |
| `ddc_` | DDC | Distance-dependent curvature |
| `iface_` | Interface | Predicted interface probability |
| `hbond_` | H-bonds | Hydrogen bond potential |
| `mesh_` | Mesh | Surface triangulation |

Toggle objects on/off to view different features.

### Color Schemes

**Electrostatics (pb_):**
- Red: Negative charge
- White: Neutral
- Blue: Positive charge

**Hydrophobicity (hphobic_):**
- Purple/Magenta: Hydrophilic
- White: Neutral
- Yellow: Hydrophobic

**Shape Index (si_):**
- Red: Concave (cup-like)
- White: Saddle
- Blue: Convex (dome-like)

**Interface (iface_):**
- Red: Low interface probability
- White: Medium
- Blue: High interface probability

### Additional Commands

Load interface silhouette (boundary of predicted interface):

```
loadgiface 4ZQK_A.ply
```

Load dot representation:

```
loaddots 4ZQK_A.ply
```

## Dockerfile

### Building from Source

To build a Docker MaSIF image from the included Dockerfile:

```bash
cd docker/
docker build -t masif .
```

This builds a complete image with:
- Ubuntu 18.04 base
- Python 2.7 + 3.6 dual environment
- All scientific tools (APBS, MSMS, Reduce, PDB2PQR)
- TensorFlow 1.12.0
- SBI library for MaSIF-ligand
- Pre-trained models for all applications

Build time is approximately 15-30 minutes.

**Note:** This is a CPU-only image. For GPU support with modern NVIDIA GPUs, see `CUDA_UPDATE_PLAN.md` for future implementation plans.
