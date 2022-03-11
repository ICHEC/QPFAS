import tequila as tq
import qpfas
import numpy as np
from typing import List, Dict


########################################  General Workflow Functions  ##################################################

def create_molecule(molecule_tag: str,
                    basis: str,
                    active_space,
                    path: str = None,
                    mol_index=None) -> qpfas.chemistry.Molecule:
    """
    Create a qpfas Molecule object from one of the default molecules in the default_molecules
    directory or from the directory specified by path
    """
    # load structure
    if mol_index:
        molecule_qpfas = qpfas.chemistry.Molecule.from_mult_xyz(molecule_tag, path=path, distortion_index=mol_index)
    else:
        molecule_qpfas = qpfas.chemistry.Molecule.from_xyz(molecule_tag, path=path)

    # assign basis
    molecule_qpfas.basis = basis

    # get active space
    if isinstance(active_space, list):
        molecule_qpfas.active_orbitals = active_space
    else:
        if (not active_space) or (active_space == "None") or (active_space == "full"):
            molecule_qpfas.active_orbitals = list(range(qpfas.chemistry.number_of_orbitals(molecule_qpfas)))
        elif active_space == 'frozen_core':
            molecule_qpfas.active_orbitals = qpfas.chemistry.get_frozen_core_active_orbitals(molecule_qpfas)
        elif "noons" in active_space:
            tol = float(active_space.split("_")[1])
            nat_orbitals = qpfas.chemistry.NaturalOccupations(molecule_qpfas)
            molecule_qpfas.active_orbitals = nat_orbitals.split_space(tol)
        else:
            raise Exception(f"Active Space Method{active_space} not recognised")
    return molecule_qpfas


def get_molecule_tq(molecule_qpfas: qpfas.chemistry.Molecule,
                    transformation: str,
                    ) -> tq.chemistry.Molecule:
    """
    Generate the second quantisation from a qpfas molecule object
    """
    return tq.chemistry.Molecule(molecule_qpfas.to_tequila(),
                                 basis_set=molecule_qpfas.basis,
                                 transformation=transformation,
                                 active_orbitals=molecule_qpfas.active_orbitals)


def molecule_make_hamiltonian(molecule: tq.chemistry.Molecule):
    """
    Make the Qubitized Hamiltonian
    """
    return molecule.make_hamiltonian()


def compute_benchmark_energies(molecule: tq.chemistry.Molecule,
                               benchmarks: List[str]) -> Dict:
    """
    This uses psi4 to perforom the classical benchmarks.
    """
    energy_benchmarks = {}
    for method in ["hf", "mp2", "ccsd", "fci"]:
        if method in benchmarks:
            energy_benchmarks[method + "_energy"] = molecule.compute_energy(method=method)
    return energy_benchmarks


def compute_benchmark_energies_pyscf(molecule_qpfas: qpfas.chemistry.Molecule,
                                     benchmarks: List[str]) -> Dict:
    """
    This is an alternative to compute_benchmark_energies. Instead of using psi4 it uses
    pyscf to perforom the classical benchmarks.
    """

    full_space = list(range(qpfas.chemistry.number_of_orbitals(molecule_qpfas)))
    frozen_orbitals = list(set(full_space) - set(molecule_qpfas.active_orbitals))
    frozen_orbitals.sort()
    print("Frozen orbitals:", frozen_orbitals)
    return qpfas.chemistry.run_pyscf(molecule_qpfas, benchmarks, frozen_orbitals)


def get_n_qubits(molecule: tq.chemistry.Molecule):
    if molecule.active_space is not None:
        return 2*len(molecule.active_space.active_orbitals)
    else:
        return 2*molecule.n_orbitals


def get_ansatz(molecule_tq: tq.chemistry.Molecule,
               ansatz_method: str,
               ansatz_depth: int
               ) -> tq.circuit.circuit.QCircuit:
    """
    Generates
        - UCCSD variants
        - hardware efficient variants
    Ansatz for inputted Tequila molecule
    """
    if ansatz_method == "uccsd":
        return molecule_tq.make_uccsd_ansatz(trotter_steps=ansatz_depth)

    elif ansatz_method == "kupccgsd":
        return molecule_tq.make_upccgsd_ansatz(order=ansatz_depth)

    elif ansatz_method == "hardware":
        return qpfas.chemistry.hardware_ansatz(get_n_qubits(molecule_tq), ansatz_depth)

    elif ansatz_method == "hardwareconserving":
        return qpfas.chemistry.hardware_pc_ansatz(get_n_qubits(molecule_tq), molecule_tq.n_electrons, ansatz_depth)

    else:
        raise Exception("Method '%s' not in available ansatzes" % ansatz_method)


def get_ansatz_list_convention(molecule_tq: tq.chemistry.Molecule,
                               ansatz_name_depth: List):
    """A helper function if one wants to create an ansatz from a list convention.
    i.e. [<ansatz_name>, <ansatz+depth>]
    """
    return get_ansatz(molecule_tq, ansatz_name_depth[0], ansatz_name_depth[1])


#def num
########################################  VQE Functions  ###############################################################

def vqe_wrapper(ansatz: list,
                qubit_hamiltonian_tq: tq.QubitHamiltonian,
                molecule_tq: tq.chemistry.Molecule,
                optimizer: str,
                samples,
                backend: str = "qulacs"):
    """
    A wrapper functions for the different VQE workflows
    """
    ansatz_method, ansatz_depth = ansatz
    result_dict =  {"n_hamiltonian_terms": get_number_of_terms(qubit_hamiltonian_tq)}

    if "adapt" in ansatz_method:
        _, pool = ansatz_method.split("-")
        run_output = run_adapt_vqe(qubit_hamiltonian_tq, ansatz_depth, molecule_tq, optimizer, pool, samples, backend)

        ansatz_circuit = run_output.U
        result_dict["vqe_output"] = {"converged_energy": run_output.energy,
                                     "energy_history": list(np.concatenate([i.energies for i in run_output.histories])),
                                     "n_iterations": len(run_output.histories),
                                     "n_params": len(run_output.variables),
                                     "converged_params": {str(i): run_output.variables[i] for i in run_output.variables}}

    elif ansatz_method == "tapering":
        ansatz_circuit, result, tapering_dict = run_tapering_vqe(qubit_hamiltonian_tq, ansatz_depth, optimizer, samples, backend, "best")
        result_dict["vqe_output"] = {"converged_energy": result.energy,
                                     "energy_history": list(result.history.energies),
                                     "n_iterations": len(result.history.energies),
                                     "n_params": len(result.variables),
                                     "converged_params": {str(i): result.variables[i] for i in result.variables}}
        result_dict["tapering_data"] = tapering_dict

    else:
        ansatz_circuit = get_ansatz(molecule_tq, ansatz_method, ansatz_depth)
        run_output = run_vqe(qubit_hamiltonian_tq, ansatz_circuit, optimizer, ansatz_method, samples, backend)
        result_dict["vqe_output"] = {"converged_energy": run_output.energy,
                                     "energy_history": list(run_output.history.energies),
                                     "n_iterations": len(run_output.history.energies),
                                     "n_params": len(run_output.variables),
                                     "converged_params": {str(i): run_output.variables[i] for i in run_output.variables}}
    return result_dict, ansatz_circuit


def run_vqe(qubit_hamiltonian_tq: tq.QubitHamiltonian,
            ansatz_circuit: tq.circuit.circuit.QCircuit,
            optimizer: str = "COBYLA",
            initialization: str = "zeros",
            samples: int = 0,
            backend: str = "qulacs"
            ) -> tq.optimizers.optimizer_scipy.SciPyResults:
    """
    Runs the supplied minimization algorithm on the supplied objective function and returns
    Tequila's SciPyResults object storing the result.
    """
    if initialization in ["zeros", "uccsd", "kupccgsd"]:
        initial_values = {k: 0.0 for k in ansatz_circuit.extract_variables()}
    elif initialization in ["random", "hardware", "hardwareconserving"]:
        tau = 2.*np.pi
        initial_values = {k: tau*np.random.rand() for k in ansatz_circuit.extract_variables()}
    else:
        raise Exception("initialization '%s' not recognized" % initialization)
    if samples == 0:
        samples = None

    energy_objective = _energy_objective_function(qubit_hamiltonian_tq, ansatz_circuit, samples)

    return tq.optimizer_scipy.minimize(objective=energy_objective,
                                       method=optimizer,
                                       backend=backend,
                                       samples=samples,
                                       initial_values=initial_values,
                                       tol=1e-3)


def run_tapering_vqe(qubit_hamiltonian_tq: tq.QubitHamiltonian,
                     depth: int,
                     optimizer: str,
                     samples: int = 0,
                     backend: str = "qulacs",
                     return_type: str = "best"):
    """
    Runs the VQE algorithm with tapering
    """
    taper = qpfas.chemistry.TaperQubits(qubit_hamiltonian_tq.to_openfermion())
    taper.compute_generators()
    taper.transform_hamiltonian()

    n_qubits = taper.num_qubits - taper.nullity
    ansatz_circuit = qpfas.chemistry.hardware_ansatz(n_qubits, depth)  # must use ansatz that can generate arbitrary states

    results = []
    sectors = []
    for i in range(2**taper.nullity):
        sec = bin(i)[2:]
        sec = "0" * (taper.nullity - len(sec)) + sec
        sec = [int(j) for j in sec]
        taper.remove_qubits(sec)

        qubit_hamiltonian_tq = tq.QubitHamiltonian.from_openfermion(taper.tapered_hamiltonian)
        vqe_run = run_vqe(qubit_hamiltonian_tq, ansatz_circuit, optimizer, "random", samples, backend)
        results.append(vqe_run)
        sectors.append(sec)
    if return_type == "best":
        indx = np.argmin([i.energy for i in results])
        tapering_dict = {"sector": sectors[indx],
                         "qubit_set": taper.qubit_set,
                         "qubits_removed": len(taper.qubit_set)}
        return ansatz_circuit, results[indx], tapering_dict
    elif return_type == "all":
        return results
    else:
        raise Exception("Return type must be either 'best' or 'all'")


def run_adapt_vqe(qubit_hamiltonian_tq: tq.QubitHamiltonian,
                  norm_tolerance,
                  molecule: tq.chemistry.Molecule,
                  optimizer: str,
                  pool: str = "UpCCSD",
                  samples: int = 0,
                  backend: str = "qulacs"):
    """
    Method based on "An adaptive variational algorithm for exact molecular simulations on a quantum computer"
    https://www.nature.com/articles/s41467-019-10988-2
    """
    if samples == 0:
        samples = None

    operator_pool = tq.adapt.MolecularPool(molecule=molecule, indices=pool)

    solver = tq.adapt.Adapt(H=qubit_hamiltonian_tq,
                            Upre=molecule.prepare_reference(),
                            operator_pool=operator_pool,
                            optimizer_args={"method": optimizer},
                            compile_args={"samples": samples, "backend": backend},
                            gradient_convergence=norm_tolerance,
                            energy_convergence=1e-3)
    return solver(operator_pool=operator_pool, label=0)


########################################  Results Gathering  ###########################################################
def split_vqe_wrapper_results(results):
    """A helper function for workflow"""
    return results[0]


def split_vqe_wrapper_ansatz(results):
    """A helper function for workflow"""
    return results[1]


def get_gate_dict(ansatz):
    variables = {i: np.random.rand() for i in ansatz.extract_variables()}  # necessary for qasm conversion
    qasm_str = tq.export_open_qasm(ansatz, variables=variables)
    qasm_str = qasm_str.split("\n")[4:-1]
    qasm_str = np.array([i[:2] for i in qasm_str])

    gate_dict = {"n_qubits": ansatz.n_qubits,
                 "depth_tq": ansatz.depth,
                 "n_gates_tq": len(ansatz.gates),
                 "gate_total": len(qasm_str)}

    for i in np.unique(qasm_str):
        gate_dict["gate_" + i.strip()] = int(np.sum(qasm_str == i))  # necessary for json conversion

    return gate_dict


def get_number_of_terms(qubit_hamiltonian_tq: tq.QubitHamiltonian):
    return len(qubit_hamiltonian_tq)


def combine_results(result_dict, molecule_qpfas, gate_stats):
    result_dict["geometry"] = molecule_qpfas.to_tequila()
    result_dict["active_space"] = molecule_qpfas.active_orbitals
    result_dict["circuit_stats"] = gate_stats

    return result_dict


def number_of_qubits_after_taper(qubit_hamiltonian_tq: tq.QubitHamiltonian, include_n_ham_terms=True):
    taper = qpfas.chemistry.TaperQubits(qubit_hamiltonian_tq.to_openfermion())
    taper.compute_generators()
    n_qubits = taper.num_qubits - taper.nullity

    if include_n_ham_terms:
        # here we project to the sector with all zeros
        taper.transform_hamiltonian()
        taper.remove_qubits([0] * taper.nullity)
        qubit_hamiltonian_tq = tq.QubitHamiltonian.from_openfermion(taper.tapered_hamiltonian)
        return {"n_qubits_taper": n_qubits, "n_hamiltonian_terms_taper": len(qubit_hamiltonian_tq)}

    else:
        return {"n_qubits_taper": n_qubits}


def combine_results_circuit_requirements(gate_stats, taper_output, qubit_hamiltonian_tq, molecule_qpfas):
    # helper function to combine results for calculating the circuit requirements
    merged_dict = {}
    for i in [gate_stats, taper_output]:
        merged_dict.update(i)
    merged_dict["n_hamiltonian_terms"] = get_number_of_terms(qubit_hamiltonian_tq)
    merged_dict["active_space"] = molecule_qpfas.active_orbitals
    return merged_dict


########################################  Internal Methods  ############################################################

def _energy_objective_function(qubit_hamiltonian_tq,
                               ansatz: tq.circuit.circuit.QCircuit,
                               samples) -> tq.objective.objective.Objective:
    """
    Generate and return the objective function for a supplied hamiltonian and Ansatz
    Note that you will only benefit from optimizing measurements when you simulate with finite samples
    """
    if (samples is None) or (samples == 0):
        return tq.ExpectationValue(H=qubit_hamiltonian_tq, U=ansatz)

    else:
        return tq.ExpectationValue(H=qubit_hamiltonian_tq, U=ansatz, optimize_measurements=True)
