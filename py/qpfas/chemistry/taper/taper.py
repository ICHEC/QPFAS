import numpy as np
import openfermion
import cffi
from qpfas.chemistry.taper.mm2r import lib
from itertools import product

class TaperQubits:
    def __init__(self, qubit_hamiltonian: openfermion.QubitOperator):
        self.qubit_hamiltonian = qubit_hamiltonian
        self.num_qubits = openfermion.count_qubits(qubit_hamiltonian)
        self.ops = ['X', 'Z']

        self.parity_check = None
        self.nullity = None
        self.generators = None
        self.qubit_set = None
        self.unitary = None
        self.tapered_hamiltonian = None

    def compute_generators(self):
        """
        To find the null space of a matrix:
        - https://en.wikipedia.org/wiki/Kernel_(linear_algebra)
        - Recall all computations are mod 2
        - Use padding trick: https://math.stackexchange.com/questions/598508/basis-of-a-null-space-of-a-matrix
        """
        self.make_paritycheck()
        
        ffi = cffi.FFI()
        m, n = self.parity_check.shape
        pcheck_c = ffi.new("int* [%i]" % m)
        for i in range(m):
            pcheck_c[i] = ffi.cast("int *", self.parity_check[i].ctypes.data)
        lib.binary_gaussian_elimination(pcheck_c, m, n)

        row_norm = np.sum(self.parity_check, 1)
        self.parity_check = self.parity_check[row_norm > 0]
        n_cols = self.parity_check.shape[1]
        self.nullity = n_cols - self.parity_check.shape[0]

        # find pivots
        pivots = np.zeros(n_cols, dtype=int)
        row_memory = []
        for i in range(n_cols):
            if np.sum(self.parity_check[:, i] == 1):
                row_coord = np.where(self.parity_check[:, i] == 1)[0][0]
                if row_coord not in row_memory:
                    row_memory.append(row_coord)
                    pivots[i] = 1

        tmp = np.eye(n_cols, dtype=int)
        p_count = 0
        for i in range(n_cols):
            if pivots[i]:
                tmp[i] = self.parity_check[row_memory[p_count]]
                p_count += 1

        self.generators = []
        for i in range(n_cols):
            if pivots[i] != 1:
                self.generators.append(tmp[:, i])

    def transform_hamiltonian(self):
        """
        Here we follow the method in arxiv:1701:08213
        From the paper:
            'In all examples considered below the symmetry generators ... are Z-type Pauli operators.'
        """
        # check only Z-type operators
        max_check = max([max(i[:self.num_qubits]) for i in self.generators])
        if max_check == 1:
            raise Exception("X-type Pauli terms in Generator")

        z_ops = np.array(self.generators)[:, self.num_qubits:]
        g_sum = np.sum(z_ops, 0)
        self.qubit_set = []
        self.unitary = openfermion.QubitOperator("")

        for i in range(self.nullity):
            unitary_tmp = openfermion.QubitOperator("")
            cond = True
            for j in range(self.num_qubits):
                if z_ops[i][j] == 1:
                    unitary_tmp *= openfermion.QubitOperator("Z%i" % j)
                    if (g_sum[j] == 1) and cond:
                        unitary_tmp2 = openfermion.QubitOperator("X%i" % j)
                        cond = False
                        self.qubit_set.append(j)
            self.unitary *= unitary_tmp + unitary_tmp2
        self.unitary = self.unitary / np.sqrt(2 ** self.nullity)
        U_dag = openfermion.hermitian_conjugated(self.unitary)
        self.qubit_hamiltonian = U_dag * self.qubit_hamiltonian * self.unitary
        self.qubit_hamiltonian.compress(1e-8)

    def print_generators(self):
        for sigma_op in self.generators:
            s = "[ "
            for i in range(2*self.num_qubits):
                if sigma_op[i] == 1:
                    s += "%s%i " % (self.ops[i // self.num_qubits], i % self.num_qubits)
            s += "]"
            print(s)

    def get_sectors(self, n_electrons):
        sector_values = []
        for i in self.generators:
            spin_sums = [sum(i[self.num_qubits:][0::2]),
                         sum(i[self.num_qubits:][1::2])]
            spin_sums = sorted(spin_sums)
            if (spin_sums[0] == 0) and (spin_sums[1] == self.num_qubits // 2):
                sector_values.append([n_electrons % 2])
            else:
                sector_values.append([0, 1])
        return list(product(*sector_values))

    def remove_qubits(self, sector):
        self.tapered_hamiltonian = self.qubit_hamiltonian
        for q in self.qubit_set:
            h_q = openfermion.QubitOperator("X%i" % q) + openfermion.QubitOperator("Z%i" % q)
            self.tapered_hamiltonian = h_q * self.tapered_hamiltonian * h_q
            self.tapered_hamiltonian = self.tapered_hamiltonian / 2

        self.tapered_hamiltonian = openfermion.transforms.project_onto_sector(self.tapered_hamiltonian, self.qubit_set,
                                                                              sector)
        self.tapered_hamiltonian.compress(1e-8)

    def make_paritycheck(self):
        """
        Constructs the parity check matrix from the Hamiltonian
        The jth row in E is the Pauli String (z|x) of term j
        """
        r = len(self.qubit_hamiltonian.terms)
        self.parity_check = np.zeros((r, self.num_qubits*2), dtype="int32")
        for c, t in enumerate(self.qubit_hamiltonian.terms):
            for t_i in t:
                if t_i[1] == 'Z':
                    self.parity_check[c, t_i[0]] += 1

                elif t_i[1] == 'X':
                    self.parity_check[c, t_i[0] + self.num_qubits] += 1

                elif t_i[1] == 'Y':
                    self.parity_check[c, t_i[0]] += 1
                    self.parity_check[c, t_i[0] + self.num_qubits] += 1

        self.parity_check = self.parity_check % 2

        
    

