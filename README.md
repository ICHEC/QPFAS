# Quantum Computing Simulations for PFAS Remediation (QPFAS)

## Background

### PFAS Substances
Per- and polyfluoroalkyl substances (PFAS), also called perfluorochemicals, are a type of molecules present in a wide range of domains, such as engineering, chemical, medical and plastics industries. They are used to make coatings and products which exhibit high resistance to heat, and show repellent (to water, oil, etc) properties. Thus, PFAS are present in clothing, adhesives, fire retardants, foams, food packaging manufacturing, cooking utensils, such as pots and pans, material surfaces, and also as insulator materials. 

The PFAS family comprises wider variety of per-/poly-fluorinated compounds, such as perfluorooctane sulfonic acid (PFOS) an perfluorooctanoic acid (PFOA). On top of their extreme resistance to degradation, PFAS exhibit high mobility in water and soils, which makes the potentially toxic and harmful to the human being. It is well-known that PFAS can contaminate drinking water [1] and subsequently can bioaccumulate in wildlife, particularly in fish, being transported into the human food chain. The health impacts include cancer (of kidney, bladder and liver), thyroid diseases, hormonal changes, increased cholesterol among other conditions. It is also recognised that exposure to high levels of PFAS compounds can have impact on the immune system. Studies on humans and animals suggested that PFAS may reduce antibody responses to vaccines [2] [3]. Therefore, analysis of remediation of PFAS from the ecosystem is crucial and widely studied through wet-lab experiments as well as form the computational and theoretical point of view [4].

## Project Objectives
The goals of the QPFAS project are:
1. Create an end-to-end process to run quantum chemistry experiments using canidate molecules that are representative of PFAS, taking into account qubit reduction techniques and all necessary quantum inputs.
2. Perform as much experiments as possible to define the scalability of the process in terms of molecules' size.
3. Conduct an analysis of the larger PFAS molecules that can be fit into the supercluster following the quantum workflow.
4. Understand the nature of the Variational Quantum Eigensolver and its most accuracy components.

# Setting and running QPFAS workflow non-interactive on an HPC Dask Cluster
## Setup environment on HPC cluster

The `setup_env.sh` script can be executed from within this directory to build the `qpfas` stack in HPC cluster environments and to build and install dependencies. Alternatively, one could build a Docker image locally, see instructions in the next section.

To build the stack, execute the following command from this directory:

```bash
./setup_env.sh <QPFAS-INSTALL-DIR>
```

where
- `<QPFAS-INSTALL-DIR>` is the full path to the location where you would like the environment and toolchain to be built.

Upon successful execution of the above commands, the generated environment can be loaded by executing the following;

```bash
source <QPFAS-INSTALL-DIR>/toolchain/load_env.sh
```
## Running QPFAS non-interactive on an HPC Dask Cluster

The goal is to perform VQE using a wide-variety of parameters, such as different optimisers, transforms, quantum backends, etc. For this purpose the first step is to  create a Dask cluster and the run the desired QPFAS workflow on it.
### Start a Dask Cluster using Slurm

Run the following command to start the Dask Cluster and pass the two required parameters:

```bash
sbatch dask_cluster_big.sh <NUM_WORKERS> <SCHEDULER_FILE_NAME>
```
where
- `<NUM_WORKERS>` - the number of Dask workers to be created on each HPC node plus `1` (i.e. if `10` Dask workers are needed, then pass `11` as the value of the parameter).
- `<SCHEDULER_FILE_NAME>`  - the name of the Dask scheduler file to be created.

Check that the cluster is running:
```bash
squeue -u $USER
```
Check that the file with name `<SCHEDULER_FILE_NAME>` is created and populated.

### Start QPFAS workflow on the Dask Cluster using Slurm

Run the following command to start executing the QPFAS workflow on the Dask Cluster and pass the three required parameters:

```bash
sbatch qpfas_big.sh <LOC> <YML> <SAVE_TO>
```
where
- `<LOC>` - where to execute the  code. Either 'local' or the path to Dask scheduler file.
- `<YML>` - path to yaml input file which descibes the chemistry experiments (example in `py/examples/inputs/H2_fullrun.yml`)
- `<SAVE_TO>` - name of file to save results to (in json format). If None, output is not saved. See example of saved output file in `py/examples/inputs/H2_fullrun.json`.

This script references a partucular Python script (py/run_workflow.py) as an example. This could be replaced with a link to any other valid Python script.
### Clean-up after a QPFAS run

One the QPFAS run is finished, terminate the Slurm job running the Dask Cluster:

- Get the ID of the Slurm job running the Dask Cluster:
```bash
squeue -u $USER
```
- Terminate the Slurm job running the Dask Cluster:
```bash
scancel <DASK_CLUSTER_SLURLM_JOB_ID>
```
# Docker support

To run the software stack using Docker on a local machine, ensure there is
sufficient free memory (2GB minimum).

Next, within this directory, run the following commands:
```bash
docker-compose build
docker-compose up
```

The above command spins up the QPFAS container, a Dask scheduler container and one Dask worker container.

The Dask workers can be scaled up if needed (and if there are enough available local resources). For example the following command will start 4 dask workers:
```bash
docker-compose up --scale dask-workers=4
```
The QPFAS container will have running a Jupyter notebook server (URL and token will be printed to CLI).

If the URL provided does not give you access to the running Jupyter Notebook, then replace the URL with `localhost:8898` and continue as before. The default Jupyter Notebook password is `qpfas`.

The Dask scheduler dashboard is available on `localhost:8787`.

A number of tutorial Jupyter notebooks are available in `py/tutorials`.

# Referencing

If using this work in any way as part of your research, please cite us as: "_Quantum Computing Simulations for PFAS Remediation (QPFAS), beta release, March 2022, by Irish Centre for High-End Computing (ICHEC) and Accenture, 2022 https://github.com/ICHEC/QPFAS_".


# References

<a id="1">[1]</a> 
Environmental U. S. Protection Agency (2016).
Lifetime health advisories and health effects support documents for perfluorooctanoic acid and perfluorooctane sulfonate.
Fed. Reg., 81, 33250-33251.

<a id="2">[2]</a> 
Philippe Grandjean and Carsten Heilmann and Pal Weihe and Flemming Nielsen and Ulla B. Mogensen and Amalie Timmermann and Esben Budtz-Jorgensen (2017). 
Estimated exposures to perfluorinated compounds in infancy predict attenuated vaccine antibody concentrations at age 5-years.
Journal of Immunotoxicology, 14(1), 188-195.

<a id="3">[3]</a> 
Looker, Claire and Luster, Michael I. and Calafat, Antonia M. and Johnson, Victor J. and Burleson, Gary R. and Burleson, Florence G. and Fletcher, Tony (2013). 
Influenza Vaccine Response in Adults Exposed to Perfluorooctanoate and Perfluorooctanesulfonate. 
Toxicological Sciences, 138(1), 76-88.

<a id="4">[4]</a> 
Dombrowski, Paul M. and Kakarla, Prasad and Caldicott, William and Chin, Yan and Sadeghi, Venus and Bogdan, Dorin and Barajas-Rodriguez, Francisco and Chiang, Sheau-Yun (Dora) (2018). 
Technology review and evaluation of different chemical oxidation conditions on treatability of PFAS. 
Remediation Journal, 28(2), 135-150.
