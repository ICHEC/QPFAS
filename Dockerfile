FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential g++ gcc \
    make vim git cmake curl graphviz \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -o Miniconda3-latest-Linux-x86_64.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x ./Miniconda3-latest-Linux-x86_64.sh && \
    ./Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda

ENV CONDA_EXE=/opt/conda/bin/conda
ENV CONDA_PREFIX=/opt/conda
ENV CONDA_PYTHON_EXE=/opt/conda/bin/python
ENV CONDA_DEFAULT_ENV=base
ENV PATH=/opt/conda/bin:$PATH

RUN conda install -c conda-forge python==3.7.10 -y

# Install python-graphviz before pyscf as it tends to conflict with it
RUN conda install -c conda-forge python-graphviz -y

# Quantum Chemistry packages installation section
RUN conda install -c pyscf pyscf=1.7.6 -y && \
    conda install -c psi4 psi4 -y

RUN pip install h5py==3.2.1

RUN pip install tequila-basic==1.6.0 && \
    pip install openfermionpsi4==0.5 && \
    pip install Qulacs==0.3.0

# Generic packages installation section (including Jupyter)
RUN conda install -c conda-forge zeromq pydantic pyyaml jupyter -y

# Dask packages installation section
RUN conda install -c conda-forge python-blosc cytoolz dask==2021.6.2 lz4 tini==0.18.0 -y

# Final configuration
RUN mkdir /root/.jupyter
COPY jupyter_notebook_config.json /root/.jupyter

RUN mkdir /root/qpfas
WORKDIR /root/qpfas
ENV PYTHONPATH=/root/qpfas/py:$PYTHONPATH
CMD ["jupyter", "notebook", "--no-browser", "--allow-root", "--ip=0.0.0.0"]
