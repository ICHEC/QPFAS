from qpfas.chemistry import Molecule
from pyscf import gto, scf, cc, mp, fci


def run_pyscf(molecule: Molecule, methods, frozen_orbitals=None):
    """
    Functions to run pyscf ccsd
    """
    mol_pyscf = gto.Mole()
    mol_pyscf.atom = molecule.to_tequila()
    mol_pyscf.basis = molecule.basis
    mol_pyscf.spin = molecule.multiplicity - 1  # is 2S, where S = # the unpaired electrons
    mol_pyscf.charge = molecule.charge
    mol_pyscf.build()
    mf = scf.RHF(mol_pyscf)  # mf = mean-field
    mf.scf()

    if isinstance(frozen_orbitals, list):
        if len(frozen_orbitals) == 0:
            frozen_orbitals = None

    energy_benchmarks = {}

    if "hf" in methods:
        energy_benchmarks["hf_energy"] = mf.e_tot

    if "mp2" in methods:
        mp2_c2 = mp.MP2(mf).set()
        mp2_c2 = mp2_c2.run()
        energy_benchmarks["mp2_energy"] = mp2_c2.e_tot

    if "ccsd" in methods:
        my_cc = cc.CCSD(mf).set(frozen=frozen_orbitals)
        my_cc = my_cc.run()
        energy_benchmarks["ccsd_energy"] = my_cc.e_tot

    if "fci" in methods:
        cisolver = fci.FCI(mf, frozen=frozen_orbitals)
        cisolver = cisolver.run()
        energy_benchmarks["fci_energy"] = cisolver.e_tot

    return energy_benchmarks
