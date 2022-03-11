from qpfas.chemistry.load_default_molecules import load_molecule
from typing import List


class Molecule:
    """
    A class for representing molecules
    It contains all the information in order to perform chemistry calculations
    """
    def __init__(self, atom_list: List,
                 label: str = None,
                 description: str = None,
                 basis: str = None,
                 active_orbitals: List = None,
                 charge: int = 0,
                 multiplicity: int = 1):

        self.atom_list = atom_list
        self.label = label
        self.description = description
        self.basis = basis
        self.active_orbitals = active_orbitals
        self.charge = charge
        self.multiplicity = multiplicity

    def __str__(self):
        geom = "\n".join([f"\t{i[0]} \t{i[1][0]:.3f} {i[1][1]:.3f} {i[1][2]:.3f}" for i in self.atom_list])
        return f'{self.label}: \n{geom}\n\nbasis: {self.basis}\nactive space: {self.active_orbitals}'

    def get_elements(self):
        return [i[0] for i in self.atom_list]

    def to_tequila(self):
        return "\n".join(["{0} {1} {2} {3}".format(i[0], i[1][0], i[1][1], i[1][2]) for i in self.atom_list])

    @classmethod
    def from_xyz(cls, formula: str, path: str = None):
        xyz_data = load_molecule(formula, path).splitlines()
        atom_list = [i.split() for i in xyz_data[2: 2+int(xyz_data[0])]]
        atom_list = [[i[0], (float(i[1]), float(i[2]), float(i[3]))] for i in atom_list]
        return cls(atom_list=atom_list, label=formula, description=xyz_data[1])

    @classmethod
    def from_mult_xyz(cls, formula: str, path, distortion_index: int):
        xyz_data = load_molecule(formula, path).splitlines()
        n_atoms = int(xyz_data[0])
        skip_over = 2 + (2+n_atoms)*distortion_index
        atom_list = [i.split() for i in xyz_data[skip_over: skip_over+n_atoms]]
        atom_list = [[i[0], (float(i[1]), float(i[2]), float(i[3]))] for i in atom_list]
        return cls(atom_list=atom_list, label=formula, description=xyz_data[1])
