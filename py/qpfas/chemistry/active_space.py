import numpy as np
from pyscf import gto, scf, mp
from qpfas.chemistry import Molecule


def number_of_orbitals(molecule: Molecule):
    """
    Returns the number of spatial orbitals a given molecule has for a given basis, assuming a full active space
    """
    basis_sets = ["sto-3g", "3-21G", "6-31g", "cc-pVDZ"]
    basis_dict = {'H': [1, 2, 2, 5], 'He': [1, 2, 2, 5],
                  'Li': [5, 9, 9, 14], 'Be': [5, 9, 9, 14], 'B': [5, 9, 9, 14],
                  'C': [5, 9, 9, 14], 'N': [5, 9, 9, 14], 'O': [5, 9, 9, 14], 'F': [5, 9, 9, 14]}
    if molecule.basis in basis_sets:
        index = basis_sets.index(molecule.basis)
    else:
        raise Exception("Basis '{}' not recognized".format(molecule.basis))

    n_orbitals = 0
    for element in molecule.get_elements():
        if element not in basis_dict.keys():
            raise Exception("Element '%s' not supported. Currently only elements H-Mg are supported." % element)
        else:
            n_orbitals += basis_dict[element][index]
    return n_orbitals


def number_of_qubits(molecule: Molecule):
    return number_of_orbitals(molecule) * 2


def get_frozen_core_active_orbitals(molecule: Molecule):
    """
    Computes the frozen core active space
        https://sites.google.com/site/orcainputlibrary/frozen-core-calculations
    Currently only elements H-F are supported
    """
    el_dict = {'H': 0, 'He': 0, 'Li': 0, 'Be': 0,
               'B': 1, 'C': 1, 'N': 1, 'O': 1, 'F': 1}

    num_frozen = 0
    for element in molecule.get_elements():
        if element not in el_dict.keys():
            raise Exception("Element '%s' not supported. Currently only elements H-Mg are supported." % element)
        else:
            num_frozen += el_dict[element]

    #print("Frozen Orbitals: {}\nThis will remove {} qubits".format(num_frozen, num_frozen*2))
    n_orbtials = number_of_orbitals(molecule)
    return list(range(num_frozen, n_orbtials))


class NaturalOccupations:
    """
    Method based on natural orbital occupation numbers (NOONs)
    """
    def __init__(self,
                 molecule: Molecule,
                 method: str = "mp2"):

        mol_pyscf = gto.Mole()
        mol_pyscf.build(atom=molecule.atom_list,
                        basis=molecule.basis,
                        spin=molecule.multiplicity - 1,
                        charge=molecule.charge,
                        verbose=1)

        self.no_occs, self.hf_energy, self.hf_occs, self.orbital_energies = self.get_natural_orbitals(mol_pyscf, method)

    def split_space(self, tol: float):
        """
        From: arXiv:1902.10679
        The core orbitals are assumed to be doubly occupied,
        and their contributions are integrated out to an effective
        field felt by the active space and virtual space.
        The virtual orbitals are ignored, and the problem is solved exactly within the dressed active space.
        """
        in_active = []

        core_bound = 2.0 - tol
        for i, occ in enumerate(self.no_occs):
            #print(i, occ)
            if (occ > tol) and (occ < core_bound):
                in_active.append(i)
        return in_active

    @staticmethod
    def get_natural_orbitals(mol, method):
        mf = scf.RHF(mol)  # mf = mean-field
        mf.scf(verbose=0)

        if method == "mp2":
            mp2 = mp.MP2(mf)
            e_mp2, t_mp2 = mp2.kernel()
            rdm1 = mp2.make_rdm1(t_mp2)
        else:
            raise Exception("Method not recognised")

        natural_occs, _ = np.linalg.eig(rdm1)
        return natural_occs, mf.e_tot, mf.mo_occ, mf.mo_energy
