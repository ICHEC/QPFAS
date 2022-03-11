import qpfas
import pandas as pd

molecules = ["H2", "LiH", "H2O", "CH4", "CO", "N2"]  #, "O2", "C2H2", "CH2O", "CH3F", "C2H4"]
set_name = "under30Q"
#,"CH3NH2", "CO2" "C2H6","CH2CO","CHF3","CH3CN","C3H4","CH3CHO","CF2O"]


basis = "sto-3g"
comment = "computing the circuit requirements"
transformation = "jordan_wigner"

active_space_methods = ["None", "frozen_core", "noons_0.01", "noons_0.005", "noons_0.002"]

data = []

for mol in molecules:
    print("\n\n", mol)
    for active_space_method in active_space_methods:
        mol_qpfas = qpfas.workflow.create_molecule(mol, basis, active_space_method)
        mol_tq = qpfas.workflow.get_molecule_tq(mol_qpfas, transformation)
        e_bench = qpfas.workflow.compute_benchmark_energies_pyscf(mol_qpfas, ["ccsd", "hf"])
        qubit_hamiltonian_tq = qpfas.workflow.molecule_make_hamiltonian(mol_tq)
        taper_output = qpfas.workflow.number_of_qubits_after_taper(qubit_hamiltonian_tq)

        circuit_he = qpfas.workflow.get_ansatz_list_convention(mol_tq, ["hardware", 2])
        gate_stats_he = qpfas.workflow.get_gate_dict(circuit_he)

        circuit_uccsd = qpfas.workflow.get_ansatz_list_convention(mol_tq, ["uccsd", 1])
        gate_stats_uccsd = qpfas.workflow.get_gate_dict(circuit_uccsd)

        data.append([mol, active_space_method, mol_qpfas.active_orbitals, e_bench["ccsd_energy"], e_bench["hf_energy"], taper_output, len(qubit_hamiltonian_tq), gate_stats_he, gate_stats_uccsd])

exp_df = pd.DataFrame(data, columns=["molecule", "active_space_method", "active_orbitals", "ccsd_energy", "hf_energy", "taper_output", "n_hamiltonian_terms",
                                     "gate_stats_he", "gate_stats_uccsd"])
exp_df.to_json(f"results_{set_name}.json")

