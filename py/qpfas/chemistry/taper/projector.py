import openfermion
import time

class Projector:
    def __init__(self, n_spin_orbitals, n_sector):
        self.n_spin_orbitals = n_spin_orbitals
        self.n_sector = n_sector
        self.time = {}

    def project_hamiltonian(self, hamiltonian):
        t0 = time.time()
        projector = self.make_proj_total()
        hamiltonian = projector * hamiltonian * projector
        self.time['proj'] = time.time() - t0
        return hamiltonian

    def project_hamiltonian_fast(self, hamiltonian):
        """
        See 'Optimizing qubit resources for quantum chemistry simulations in second quantization on a quantum computer'
        """
        t0 = time.time()
        number_operator = self.op_total()

        for i in range(self.n_spin_orbitals + 1):
            if i != self.n_sector:
                p_i = (number_operator - openfermion.FermionOperator("", i)) / (self.n_sector - i)
                hamiltonian = p_i * hamiltonian * p_i
                hamiltonian = openfermion.utils.normal_ordered(hamiltonian)

        self.time['proj_fast'] = time.time() - t0
        return hamiltonian

    def make_proj_total(self):
        """
        Returns the projector for the N particle subspace
        """
        number_operator = self.op_total()
        projector = openfermion.FermionOperator("")  # identity
        for i in range(self.n_spin_orbitals + 1):
            if i != self.n_sector:
                projector *= (number_operator - openfermion.FermionOperator("", i)) / (self.n_sector - i)
        return openfermion.utils.normal_ordered(projector)

    def op_total(self):
        op = openfermion.FermionOperator()  # empty operator
        for ind in range(self.n_spin_orbitals):
            op += openfermion.FermionOperator(((ind, 1), (ind, 0)))
        return op



# class Projector:
#     """
#     sector is a list
#         if only one component then it's the total number of particles
#         if two: N_up, N_down
#     """
#     def __init__(self, n_spin_orbitals, sector):
#         self.n_spin_orbitals = n_spin_orbitals
#         self.sector = sector
#
#     def project_hamiltonian(self, hamiltonian):
#         projector = self.get_projector()
#         projector_h = openfermion.utils.hermitian_conjugated(projector)
#         hamiltonian = projector_h * hamiltonian * projector
#         return hamiltonian
#
#
#     def get_projector(self):
#         if len(self.sector) == 1:
#             return self.make_proj_total()
#         elif len(self.sector) == 2:
#             return self.make_proj_spin()
#         else:
#             raise Exception
#
#
#
#     def op_spin(self, up_down):
#         if up_down == "up":
#             c = 0
#         elif up_down == "down":
#             c = 1
#         else:
#             raise Exception
#
#         op = openfermion.FermionOperator()  # empty operator
#         for ind in range(c, self.n_spin_orbitals, 2):
#             op += openfermion.FermionOperator(((ind, 1), (ind, 0)))
#         return op
#
#     def make_proj_total(self):
#         """
#         Returns the projector for the N particle subspace
#         """
#         number_operator = self.op_total()
#         projector = openfermion.FermionOperator("")  # identity
#         n_part = self.sector[0]
#         for i in range(self.n_spin_orbitals + 1):
#             if i != n_part:
#                 projector *= (number_operator - openfermion.FermionOperator("", i)) / (n_part - i)
#         return openfermion.utils.normal_ordered(projector)
#
