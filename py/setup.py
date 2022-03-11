import setuptools
#from Cython.Build import cythonize

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QPFAS", 
    version="0.4.0-beta",
    author="Irish Centre for High-End Computing \& Accenture",
    maintainer_email="support@ichec.ie",
    description="QPFAS software package",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://git.ichec.ie/accenture-qpfas/accenture-qpfas",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "scipy", "jupyter", "pydantic", "dask", "pandas", "mpi4py", "dask-mpi", "pint", "pyyaml", "pyscf"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: Linux",
    ],
    python_requires='==3.7.*',
    # ext_modules=cythonize("qpfas/chemistry/qubitization/analytic_cython.pyx",
    #     compiler_directives={'language_level' : "3"},
    #     annotate=True,
    # ),
    # package_data={'': ['build/lib*/analytic_cython.*.so'],},
    # include_package_data = True
)
