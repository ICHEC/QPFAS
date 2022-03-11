import unittest
import qpfas
import openfermion


class Testqpfas(unittest.TestCase):

    def testAtomGeomDefaults(self):
        h = qpfas.chemistry.AtomGeom()

        self.assertEqual(h.atom.get_label(), 'H')
        self.assertEqual(h.geom, qpfas.chemistry.Geom(0,0,0))
        self.assertEqual(h, qpfas.chemistry.AtomGeom())

        self.assertEqual(h, qpfas.chemistry.AtomGeom(atom=qpfas.chemistry.Atom('H')))
        self.assertEqual(h, qpfas.chemistry.AtomGeom(geom=qpfas.chemistry.Geom(0,0,0)))
        self.assertEqual(h, qpfas.chemistry.AtomGeom(atom=qpfas.chemistry.Atom('H'), geom=qpfas.chemistry.Geom(0,0,0)))
        
        self.assertNotEqual(h, qpfas.chemistry.AtomGeom(geom=qpfas.chemistry.Geom(1.0,0,0)))
        self.assertNotEqual(h, qpfas.chemistry.AtomGeom(atom=qpfas.chemistry.Atom('F') ) )
        self.assertNotEqual(h, qpfas.chemistry.AtomGeom(atom=qpfas.chemistry.Atom('F'), geom=qpfas.chemistry.Geom(1.0,0,0) ) )

    def testMoleculeDefaults(self):
        # Create H2 by first making a list of H atoms at different positions
        # H is assumed the default atomic element, at position (0,0,0).
        h = [qpfas.chemistry.AtomGeom(), qpfas.chemistry.AtomGeom(geom=qpfas.chemistry.Geom(0, 0, 0.74))]
        H2 = qpfas.chemistry.create_molecule([h[0], h[1]], 0, 1, 'H2')

        self.assertEqual(H2.get_num_atoms(), 2)
        self.assertEqual(H2.label, "H2")
        self.assertEqual(H2.charge, 0)
        self.assertEqual(H2.multiplicity, 1)
        self.assertEqual(H2.description, None)

    def testMoleculeDict(self):
        molecules = qpfas.chemistry.create_molecule_dict()
        self.assertEqual(molecules['H2'].get_num_atoms(), 2)
        self.assertEqual(molecules['H2O'].get_num_atoms(), 3)
        self.assertEqual(molecules['CH4'].get_num_atoms(), 5)
        self.assertEqual(molecules['C3H8'].get_num_atoms(), 11)
        self.assertEqual(molecules['C3F8'].get_num_atoms(), 11)
        self.assertEqual(molecules['PFAS'].get_num_atoms(), 26)

    def testHamiltonianTransformTypes(self):
        molecule = qpfas.chemistry.create_molecule_dict()['H2']
        transformer = qpfas.chemistry.HamiltonianTransform()

        molecule_hamiltonian = transformer.molecule_to_second_quantisation(molecule = molecule, methods = ['scf'], verbose = False, molecule_data_dir = '.')
        fermionic_hamiltonian = molecule_hamiltonian.get_molecular_hamiltonian()
        qubit_hamiltonian = transformer.second_quantisation_to_qubitized(fermionic_hamiltonian, 'jordan_wigner')
        
        self.assertIsInstance(molecule_hamiltonian, openfermion.chem.MolecularData)
        self.assertIsInstance(fermionic_hamiltonian, openfermion.ops.InteractionOperator)
        self.assertIsInstance(qubit_hamiltonian, openfermion.ops.QubitOperator)
        
        # Use tq.QubitHamiltonian.from_openfermion(qubit_hamiltonian) to get tq format.

    #print(qpfas.chemistry.MoleculeFormatTransformer.to_xyz(h2))

if __name__ == '__main__':
    unittest.main()
