import yaml
import os
from itertools import product as prod
from typing import List

from qpfas.workflow.wrapper import *


class ExperimentList(yaml.YAMLObject):
    """
    Class for constructing unique molecule experiments from YAML file. 
    YAML file syntax for a set of experiments is given as below example:
    Note that this class has been replaced by EfficientDAG in dask_efficient.py and thus
    this code may be out of date.
    """
    yaml_tag = u"!Experiment"

    def __init__(self, exp):
        self.molecule_path = exp["molecule_path"]

        if exp["molecule_tag"] == "all_in_path":
            self.molecule_tag = self.get_all_molecules_in_path()
        else:
            self.molecule_tag = exp["molecule_tag"]

        self.comment = exp["comment"]
        self.basis = exp["basis"]

        self.benchmark = exp["benchmark"]
        if type(self.benchmark) != List:
            self.benchmark = [self.benchmark]

        self.active_space = exp["active_space"]
        self.transformation = exp["transformation"]
        self.ansatz_method = exp["ansatz_method"]
        self.optim = exp["optim"]
        self.backend = exp["backend"]
        self.samples = exp["samples"]
        self.stages = exp["stages"]

    def get_all_molecules_in_path(self):
        return [i.split(".")[0] for i in os.listdir(self.molecule_path) if '.xyz' in i]

    @classmethod
    def load_exp(cls, filename):
        """Returns a list of Experiment objects from given YAML file"""
        with open(filename, 'r') as f:
            return cls(list(yaml.load_all(f, Loader=yaml.FullLoader))[0])

    def gen_exp(self):
        """Breaks down any above ExperimentList to generate list of unique 
        single param experiments"""
        exp_list = []
        uid = 0
        iterative_variables = [self.molecule_tag, self.basis, self.active_space,
                               self.transformation, self.ansatz_method,
                               self.optim, self.samples]
        for instance in list(prod(*tuple(val if isinstance(val, list) else [val] for val in iterative_variables))):
            exp_list.append(Experiment(instance[0],
                                       self.molecule_path,
                                       self.comment,
                                       instance[1],
                                       self.benchmark,
                                       instance[2],
                                       instance[3],
                                       instance[4],
                                       instance[5],
                                       self.backend,
                                       instance[6],
                                       self.stages,
                                       uid))
            uid += 1
        return exp_list

    @staticmethod
    def get_dag_list(exp_list: List):
        return [exp.dag for exp in exp_list]

    @staticmethod
    def get_exp_params_list(exp_list: List):
        return [exp.exp_params for exp in exp_list]


class Experiment:
    def __init__(self, molecule_tag, molecule_path, comment, basis, benchmark, active_space,
                 transformation, ansatz_method, optim, backend, samples, stages, uid):
        self.molecule_tag = molecule_tag
        self.molecule_path = molecule_path
        self.comment = comment
        self.basis = basis
        self.benchmark = benchmark
        self.active_space = active_space
        self.transformation = transformation
        self.ansatz_method = ansatz_method
        self.optim = optim
        self.backend = backend
        self.samples = samples
        self.stages = stages
        self.uid = uid

        ret_list = [node['ret'] for node in self.stages]

        self.dag = {f"{node['ret']}-{self.uid}":
                    (eval(node['func']),
                     *[getattr(self, val) if val not in ret_list else f"{val}-{self.uid}" for val in node['args']])
                    for node in self.stages}

        self.exp_params = {"molecule_tag": self.molecule_tag,
                           "molecule_path": self.molecule_path,
                           "comment": self.comment,
                           "basis": self.basis,
                           "benchmark": self.benchmark,
                           "active_space": self.active_space,
                           "transformation": self.transformation,
                           "ansatz_method": self.ansatz_method,
                           "optim": self.optim,
                           "backend": self.backend,
                           "samples": self.samples,
                           "uid": self.uid}

    def __repr__(self):
        return(f"{self.__class__.__name__}(molecule_tag={self.molecule_tag},"
               f"\nmolecule_path={self.molecule_path},"
               f"\ncomment={self.comment},"
               f"\nbasis={self.basis},"
               f"\nbenchmark={self.benchmark},"
               f"\nactive_space={self.active_space},"
               f"\ntransformation={self.transformation},"
               f"\nansatz_method={self.ansatz_method},"
               f"\noptim={self.optim},"
               f"\nbackend={self.backend},"
               f"\nsamples={self.samples},"
               f"\nstages={self.stages},"
               f"\nuid={self.uid})")
