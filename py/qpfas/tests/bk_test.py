# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 18:31:46 2021

@author: james.tricker
"""
import openfermion as opf
import cProfile
from bk_trans import bravyi_kitaev, _update_set, _parity_set, transform


def one_op(i, j):
    return opf.FermionOperator(((i, 1), (j, 0)))


def two_op(i, j):
    return opf.FermionOperator(((i, 1), (j, 0))) + opf.FermionOperator(((j, 1), (i, 0)))


def coul_op(i, j):
    return opf.FermionOperator(((i, 1), (j, 1), (i, 0), (j, 0)))


def num_exc_op(i, j, k):
    return opf.transforms.normal_ordered(
        opf.FermionOperator(((i, 1), (j, 1), (j, 0), (k, 0))) + opf.FermionOperator(((j, 1), (k, 1), (i, 0), (j, 0))))


def four_op(i, j, k, l):
    return opf.transforms.normal_ordered(opf.FermionOperator(((i, 1), (j, 1), (k, 0), (l, 0))))


def bk_test(i, j, n_qubits):
    # n_op, coefs, ops, herm = unhermitianize(one_op(i, j))
    # ham = one_op(i, j)

    qubit_hamiltonian = bravyi_kitaev(i, j, 1, n_qubits)
    qubit_hamiltonian = opf.QubitOperator(qubit_hamiltonian)
    qubit_hamiltonian.compress(1e-6)
    return qubit_hamiltonian


def test_case_one(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 0 and j % 2 == 0:
                # print(i, j)

                custom = bk_test(i, j, n_qubits)

                ham = one_op(i, j)
                opf_ham = opf.transforms.bravyi_kitaev(ham)

                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_one(64)

def test_case_two(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 0 and i not in _parity_set(j):
                # print(i, j)

                custom = bk_test(i, j, n_qubits)
                opf_ham = opf.transforms.bravyi_kitaev(ham, n_qubits)  # have to add one to get match with custom soln
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_two(64)

def test_case_three(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 0 and i in _parity_set(j):
                # print(i, j)

                custom = bk_test(i, j, n_qubits)
                opf_ham = opf.transforms.bravyi_kitaev(ham)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_three(64)

def test_case_four(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 0 and j % 2 == 1 and i not in _parity_set(j) and j not in _update_set(i, n_qubits):
                # print(i, j)

                custom = bk_test(i, j, n_qubits)
                opf_ham = opf.transforms.bravyi_kitaev(ham)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_four(64)

def test_case_five(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 0 and j % 2 == 1 and i not in _parity_set(j) and j in _update_set(i, n_qubits):
                # print(i, j)

                custom = bk_test(i, j, n_qubits)
                opf_ham = opf.transforms.bravyi_kitaev(ham)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_five(64)

def test_case_six(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 0 and j % 2 == 1 and i in _parity_set(j) and j in _update_set(i, n_qubits):
                # print(i, j)

                custom = bk_test(i, j, n_qubits)
                opf_ham = opf.transforms.bravyi_kitaev(ham)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_six(64)

def test_case_seven(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 1 and i not in _parity_set(j) and j not in _update_set(i, n_qubits):
                # print(i, j)

                opf_ham = opf.transforms.bravyi_kitaev(ham)
                custom = bk_test(i, j, n_qubits)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_seven(64)

def test_case_eight(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 1 and i in _parity_set(j) and j not in _update_set(i, n_qubits):
                # print(i, j)

                opf_ham = opf.transforms.bravyi_kitaev(ham)
                custom = bk_test(i, j, n_qubits)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_eight(64)

def test_case_nine(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 1 and i not in _parity_set(j) and j in _update_set(i, n_qubits):
                # print(i, j)

                opf_ham = opf.transforms.bravyi_kitaev(ham)
                custom = bk_test(i, j, n_qubits)
                assert custom == opf_ham
                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_nine(64)

def test_case_ten(test_range):
    for i in range(test_range):
        for j in range(test_range):

            ham = one_op(i, j)
            n_qubits = opf.count_qubits(ham)

            if i % 2 == 1 and j % 2 == 1 and i in _parity_set(j) and j in _update_set(i, n_qubits):
                # print(i, j)

                opf_ham = opf.transforms.bravyi_kitaev(ham)
                custom = bk_test(i, j, n_qubits)

                assert custom == opf_ham

                if custom != opf_ham:
                    print("custom:")
                    print(custom, "\n")

                    print("opf:")
                    print(opf_ham, "\n")

                    print("difference:")
                    print(custom - opf_ham, "\n")


# test_case_ten(64)

def test_exc_op(test_range):
    # A: Simplest class of operators (Number operators)
    # B: Excitation operators (also tests case A)
    for i in range(test_range):
        for j in range(test_range):
            ham = two_op(i, j)
            n_qubits = opf.count_qubits(ham)

            opf_ham = opf.transforms.bravyi_kitaev(ham, n_qubits)

            custom = transform(ham)

            # print(i, j)
            # print(ham)
            assert custom == opf_ham
            # if custom != opf_ham:
            #     print("custom:")
            #     print(custom, "\n")
            #
            #     print("opf:")
            #     print(opf_ham, "\n")
            #
            #     print("difference:")
            #     print(custom - opf_ham, "\n")


def test_coul_op(test_range):
    # C: Coulomb and exchange operators
    for i in range(test_range):
        for j in range(test_range):
            if i > j:
                ham = coul_op(i, j)
                n_qubits = opf.count_qubits(ham)

                opf_ham = opf.transforms.bravyi_kitaev(ham, n_qubits)
                custom = transform(ham, n_qubits)

                # print(i, j)
                # print(ham)
                assert custom == opf_ham
                # if custom != opf_ham:
                #     print("custom:")
                #     print(custom, "\n")
                #
                #     print("opf:")
                #     print(opf_ham, "\n")
                #
                #     print("difference:")
                #     print(custom - opf_ham, "\n")


def test_num_exc_op(test_range):
    # Number-excitation operator
    correct = 0
    for i in range(test_range):
        for j in range(test_range):
            if i != j:
                for k in range(test_range):
                    if k not in (i, j):
                        ham = num_exc_op(i, j, k)
                        # print(i, j, k)
                        # print(ham)

                        n_qubits = opf.count_qubits(ham)

                        opf_ham = opf.transforms.bravyi_kitaev(ham, n_qubits)
                        custom = transform(ham, n_qubits)

                        assert custom == opf_ham
                        # if custom != opf_ham:
                        #     # print(ham, "\n")
                        #     print("custom:")
                        #     print(custom, "\n")
                        #
                        #     print("opf:")
                        #     print(opf_ham, "\n")
                        #
                        #     print("N \n")


def test_double_exc_op(test_range):
    for i in range(test_range):
        for j in range(test_range):
            for k in range(test_range):
                for l in range(test_range):
                    if len({i, j, k, l}) == 4:
                        # print(i, j, k, l)
                        ham = four_op(i, j, k, l) + four_op(k, l, i, j)
                        n_qubits = opf.count_qubits(ham)

                        opf_ham = opf.transforms.bravyi_kitaev(ham, n_qubits)
                        custom = transform(ham, n_qubits)

                        assert custom == opf_ham

                        # if custom != opf_ham:
                        #     print(ham)
                        #     print("custom:")
                        #     print(custom, "\n")
                        #     print("opf:")
                        #     print(opf_ham, "\n")
                        #     # print("difference:")
                        #     # print(custom - opf_ham, "\n")



if __name__ == "__main__":
    import time
    t_start = time.time()

    print('Running tests 1/4 ...')
    test_exc_op(64)
    print('Running tests 2/4 ...')
    test_coul_op(64)
    print('Running tests 3/4 ...')
    test_num_exc_op(16)
    print('Running tests 4/4 ...')
    test_double_exc_op(8)
    print('All tests have passed.')
    t_elapsed = time.time() - t_start
    print(f'Runtime: {t_elapsed}')

test_range = 128

test_case_one(test_range)
test_case_two(test_range)
test_case_three(test_range)
test_case_four(test_range)
test_case_five(test_range)
test_case_six(test_range)
test_case_seven(test_range)
test_case_eight(test_range)
test_case_nine(test_range)
test_case_ten(test_range)