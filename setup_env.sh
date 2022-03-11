#!/bin/bash
if [[ $# -lt 1 ]]; then
    echo "Please provide full path to install"
    exit 1
fi

CONDAENV=conda_env
INSTALL_DIR=$1/toolchain
SCRIPT_PATH="$( dirname "$(readlink -f "$0")" )"
QPFAS_SOURCE_PATH=$SCRIPT_PATH/py
mkdir -p $INSTALL_DIR


# ************************************************** #
#               Initial setup
# ************************************************** #
function init(){
    module purge
    module load conda
    source activate python3
    conda create --prefix=$INSTALL_DIR/$CONDAENV python=3.7 -y
    conda activate $INSTALL_DIR/$CONDAENV #Can now use CONDA_PREFIX env variable

    module load gcc
    module load intel/2020u4
    module load cmake3
}
# ************************************************** #


# ************************************************** #
#   Install python-graphviz (Required for Dask visualization)
#   (install before pyscf as it tends to conflict with it)
# ************************************************** #
function install_python_graphviz(){
    pushd . &> /dev/null
    conda install -c conda-forge python-graphviz -y
    popd &> /dev/null
}
# ************************************************** #

# ************************************************** #
#  Quantum Chemistry packages installation section
# ************************************************** #
function install_quantum_chemistry_packages(){
    pushd . &> /dev/null
    conda install -c pyscf pyscf=1.7.6 -y
    conda install -c psi4 psi4 -y
    pip install h5py==3.2.1
    pip install tequila-basic==1.6.0
    pip install openfermionpsi4==0.5
    pip install Qulacs==0.3.0
    popd &> /dev/null
}
# ************************************************** #

# ************************************************** #
#  Generic packages installation section 
# (including Jupyter)
# ************************************************** #
function install_generic_packages(){
    pushd . &> /dev/null
    conda install -c conda-forge zeromq pydantic pyyaml jupyter -y
    popd &> /dev/null
}
# ************************************************** #

# ************************************************** #
#  Dask packages installation section
# ************************************************** #
function install_dask_packages(){
    pushd . &> /dev/null
    conda install -c conda-forge python-blosc cytoolz dask==2021.6.2 lz4 tini==0.18.0 -y
    popd &> /dev/null
}
# ************************************************** #

# ************************************************** #
#   Build and install mpi4py
# ************************************************** #
function install_mpi4py(){
    pushd . &> /dev/null
    wget --progress=bar --directory-prefix ${INSTALL_DIR}  https://github.com/mpi4py/mpi4py/releases/download/3.1.1/mpi4py-3.1.1.tar.gz
    tar -C ${INSTALL_DIR} -xf ${INSTALL_DIR}/mpi4py-3.1.1.tar.gz
    cd ${INSTALL_DIR}/mpi4py-3.1.1
    MPI_CC_COMPILER=$(which mpiicc)
    MPI_CXX_COMPILER=$(which mpiicpc)
    CC=${MPI_CC_COMPILER} CXX=${MPI_CXX_COMPILER} $CONDA_PREFIX/bin/python setup.py build --mpicc=${MPI_CXX_COMPILER}
    $CONDA_PREFIX/bin/python setup.py install
    cd -
    popd &> /dev/null
}

# ************************************************** #
#   Build and install Dask MPI
# ************************************************** #
function install_dask_mpi(){
    pushd . &> /dev/null
    wget --progress=bar --directory-prefix ${INSTALL_DIR} https://github.com/dask/dask-mpi/archive/2.21.0.tar.gz
    tar -C ${INSTALL_DIR} -xf ${INSTALL_DIR}/2.21.0.tar.gz
    cd ${INSTALL_DIR}/dask-mpi-2.21.0
    MPI_CC_COMPILER=$(which mpiicc)
    MPI_CXX_COMPILER=$(which mpiicpc)
    CC=${MPI_CC_COMPILER} CXX=${MPI_CXX_COMPILER} $CONDA_PREFIX/bin/python setup.py build
    $CONDA_PREFIX/bin/python setup.py install
    cd -
    popd &> /dev/null
}

# ************************************************** #
#   Create Environment file
# ************************************************** #
function create_env(){
cat > ${INSTALL_DIR}/load_env.sh << EOL
#!/bin/bash
module load conda gcc intel/2020u4

source activate python3
conda activate $INSTALL_DIR/$CONDAENV ;

export PATH="$INSTALL_DIR/builds/bin":"\${CONDA_PREFIX}/bin":"\${PATH}:$CONDA_PREFIX/bin"
export LD_LIBRARY_PATH="$INSTALL_DIR/builds/lib":"\${CONDA_PREFIX}/lib":"\${LD_LIBRARY_PATH}:$LD_LIBRARY_PATH:${CONDA_PREFIX}/lib"
export PYTHONPATH=$QPFAS_SOURCE_PATH:$CONDA_PREFIX/lib:$PYTHONPATH
export JUPYTER_PATH=$CONDA_PREFIX/share/jupyter/kernels:$JUPYTER_PATH
export QPFAS_SOURCE_PATH=$QPFAS_SOURCE_PATH

rm -rf \${HOME}/.local/share/jupyter/kernels/qpfas
mkdir -p \${HOME}/.local/share/jupyter/kernels/ 
ln -sf $CONDA_PREFIX/share/jupyter/kernels/qpfas \${HOME}/.local/share/jupyter/kernels/

EOL
}
# ************************************************** #


# ************************************************** #
#   Create kernelspec files
# ************************************************** #
function create_kernelspec(){
    KERNEL_DIR=$CONDA_PREFIX/share/jupyter/kernels/qpfas
    mkdir -p $KERNEL_DIR
    touch $KERNEL_DIR/run_kernel.sh
    touch $KERNEL_DIR/kernel.json

cat > $KERNEL_DIR/kernel.json << EOL
{
     "argv": [ "$KERNEL_DIR/run_kernel.sh",
               "-f", "{connection_file}"],
                "display_name": "QPFAS Py3",
                 "language": "python",
     "env": {"LD_LIBRARY_PATH":"$PYTHONPATH:$CONDA_PREFIX/lib:$INSTALL_DIR/builds/lib:\${LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}"}
}
EOL

cat > $KERNEL_DIR/run_kernel.sh << EOL
#!/usr/bin/env bash
module load conda gcc intel/2020u4

source activate python3
conda activate $INSTALL_DIR/$CONDAENV ;

export PATH="$INSTALL_DIR/builds/bin":"${CONDA_PREFIX}/bin":"\${CONDA_PREFIX}/bin":"\${PATH}"
export LD_LIBRARY_PATH="$INSTALL_DIR/builds/lib":${CONDA_PREFIX}/lib:"\${CONDA_PREFIX}/lib":"\${LD_LIBRARY_PATH}"
export PYTHONPATH=$PYTHONPATH:$CONDA_PREFIX/lib
export JUPYTER_PATH=$JUPYTER_PATH:$CONDA_PREFIX/share/jupyter/kernels

# this is the critical part, and should be at the end of your script:
exec env JUPYTER_PATH=$JUPYTER_PATH:$CONDA_PREFIX/share/jupyter/kernels env PYTHONPATH=$PYTHONPATH:$CONDA_PREFIX/lib env SBCL_HOME=$CONDA_PREFIX/lib/sbcl QUICKLISP_HOME=$INSTALL_DIR/quicklisp PATH="$INSTALL_DIR/builds/bin":"${CONDA_PREFIX}/bin":"\${PATH}" env LD_LIBRARY_PATH="$INSTALL_DIR/builds/lib":${CONDA_PREFIX}/lib:"\${CONDA_PREFIX}/lib":"\${LD_LIBRARY_PATH}" python -m IPython.kernel \$@
EOL
    chmod +x $KERNEL_DIR/run_kernel.sh
    export JUPYTER_PATH=$KERNEL_DIR:$JUPYTER_PATH 
}
# ************************************************** #

# ************************************************** #
#   Execute and log the output of each function
# ************************************************** #
function log_command(){
    LOG_NAME="SetupEnv"
    touch ${INSTALL_DIR}/${LOG_NAME}_out.log
    touch ${INSTALL_DIR}/${LOG_NAME}_err.log
    $1 > >(tee -a ${INSTALL_DIR}/${LOG_NAME}_out.log) 2> >(tee -a ${INSTALL_DIR}/${LOG_NAME}_err.log >&2)
}
# ************************************************** #


# ************************************************** #
#   Call functions
# ************************************************** #
log_command init &&
log_command install_python_graphviz &&
log_command install_quantum_chemistry_packages &&
log_command install_generic_packages &&
log_command install_dask_packages &&
log_command install_mpi4py &&
log_command install_dask_mpi &&
log_command create_env &&
log_command create_kernelspec
# ************************************************** #

