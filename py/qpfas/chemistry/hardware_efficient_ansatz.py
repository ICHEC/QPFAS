import tequila as tq


def hardware_ansatz(n_qubits: int, depth: int):
    """
    The hardware efficient ansatz
    Method based on arXiv:1704.05018

    See also: https://qiskit.org/documentation/stubs/qiskit.circuit.library.EfficientSU2.html
    """
    U = tq.QCircuit()
    
    # initial rotations (z not needed as acting on zero states
    for i in range(n_qubits):
        # U += tq.gates.Rx(tq.Variable("0x%i" % i), i)
        U += tq.gates.Ry(tq.Variable("0y%i" % i), i)

    for d in range(1, depth+1):
        # generate entanglement
        for q1 in range(n_qubits-1):
            for q2 in range(q1+1, n_qubits):
                U += tq.gates.CNOT(q1, q2)
        # rotate
        for i in range(n_qubits):
            # U += tq.gates.Rx(tq.Variable("%ix%i" % (d, i)), i)  # the x rotation is not necessary
            U += tq.gates.Ry(tq.Variable("%iy%i" % (d, i)), i)
            U += tq.gates.Rz(tq.Variable("%iz%i" % (d, i)), i)
        
    return U


def hardware_ansatz_gate_stats(n_qubits: int, depth: int):
    """returns the gate statistics of the hardware ansatz"""
    # total gates =  depth*n_qubits^2/2+ 3*n_qubits*depth/4 + n_qubits

    gate_dict = {"n_qubits": n_qubits,
                 "gate_cx": depth*n_qubits*(n_qubits-1)//2,
                 "gate_ry": n_qubits*(depth+1),
                 "gate_rz": n_qubits*depth}
    gate_dict["gate_total"] = gate_dict["gate_cx"] + gate_dict["gate_ry"] + gate_dict["gate_rz"]
    return gate_dict


def hardware_pc_ansatz(n_qubits: int,
                n_electrons: int,
                depth: int,
                topology: str = "chain"):
    """
    The hardware efficient particle conserving ansatz with chain or ring topology
    Method based on arXiv:1805.04340
    """
    U = _initialize_hf(n_electrons)

    for d in range(depth):
        # generate entanglement
        for q1 in range(n_qubits-1):
            for q2 in range(q1+1, n_qubits):
                U += _pc_entanglement_gate(q1, q2, "%iE%i_%i" % (d, q1, q2))
        if topology == "ring":
            U += _pc_entanglement_gate(n_qubits - 1, 0, "%iE%i_%i" % (d, n_qubits - 1, 0))

        # rotations
        for i in range(n_qubits):
            U += tq.gates.Rz(tq.Variable("%iz%i" % (d, i)), i)

    return U


def _initialize_hf(n_electrons: int):
    """
    Create a circuit to initialize the HF ground state
    Args:
        n_electrons: the number of electrons

    Returns:
        a circuit to create the HF state
    """
    U_hf = tq.QCircuit()
    for i in range(n_electrons):
        U_hf += tq.gates.X(i)
    return U_hf


def _pc_entanglement_gate(q1, q2, theta):
    """
    The entangling gate for the hardware_efficient_conserving method
    see arXiv:1805.04340
    Args:
        q1: first qubit index
        q2: second qubit index
        theta: the angle

    Returns:
        The entangling gate between q1 and q2
    """
    U = tq.QCircuit()
    U += tq.gates.CNOT(q1, q2)
    U += tq.gates.CRx(q2, q1, tq.Variable(theta))
    U += tq.gates.CNOT(q1, q2)
    return U
