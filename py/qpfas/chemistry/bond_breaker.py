import numpy as np


def create_distortions(equilibrium_geom, atom_bond_indices, stretch_params, write_to, tag):
    """
    Given an equilibrium_geom this creates a set of distorted molecules in an xyz file saved at write_to/tag
    - equilibrium_geom: the initial geometry
    - atom_bond_indices: a list specifying the two atoms that define the bond
    - stretch_params: a list [how far to compress bond, how far to stretch bond, how many distortions]
    - write_to: path to save xyz file
    - tag: name of saved xyz file
    """
    bond_distorter = BondBreaker(equilibrium_geom, *atom_bond_indices)
    distortions = np.linspace(*stretch_params)
    bond_distances = []
    with open(f"{write_to}/{tag}.xyz", "w") as text_file:
        for c, i in enumerate(distortions):
            mol, bd = bond_distorter.displace(i)
            text_file.write(f"{len(mol)}\n#id={c}, dist={bd}\n")
            bond_distances.append(bd)
            for atom in mol:
                text_file.write(f"{atom[0]} {atom[1]} {atom[2]} {atom[3]}\n")
    return bond_distances


#############################################################################################################


def compute_distace(x, y):
    """Helper function for computing distances between atoms"""
    d = np.array(x[1:]) - np.array(y[1:])
    return np.linalg.norm(d)


def compute_dmat(molecule):
    d_mat = np.zeros((len(molecule), len(molecule)))
    for ci, i in enumerate(molecule):
        for cj, j in enumerate(molecule):
            d_mat[ci, cj] = compute_distace(i, j)
    return d_mat


#############################################################################################################


class BondBreaker:
    """
    Class for generating the bond breaking geometries
    Given two molecules that specify the bond, all of the atoms in the molecule are split into two clusters
    based on which atom they are nearest two. When the molecule is stretched atoms in the same cluster are displaced
    by the same amount and in the same direction
    """
    def __init__(self, molecule, atom1, atom2):
        self.molecule = molecule
        self.atom1 = atom1
        self.atom2 = atom2
        self.cluster_labels = self.compute_clusters()
        self.dvec = self.compute_displacement_vector()
        self.print_out()

    def compute_displacement_vector(self):
        vec = np.array(self.molecule[self.atom1][1:]) - np.array(self.molecule[self.atom2][1:])
        vec = vec / np.linalg.norm(vec)
        return vec

    def compute_clusters(self):
        cluster_labels = []
        for c, i in enumerate(self.molecule):
            if c == self.atom1:
                cluster_labels.append(1)
            elif c == self.atom2:
                cluster_labels.append(2)
            else:
                ds = [compute_distace(i, self.molecule[self.atom1]),
                      compute_distace(i, self.molecule[self.atom2])]
                if ds[0] < ds[1]:
                    cluster_labels.append(1)
                else:
                    cluster_labels.append(2)
        return cluster_labels

    def displace(self, step):
        mol_dist = [i[:] for i in self.molecule]  # copy
        displacement = 0.5 * self.dvec * step

        for c, n in enumerate(self.cluster_labels):
            if n == 1:
                mol_dist[c][1] += displacement[0]
                mol_dist[c][2] += displacement[1]
                mol_dist[c][3] += displacement[2]

            else:
                mol_dist[c][1] -= displacement[0]
                mol_dist[c][2] -= displacement[1]
                mol_dist[c][3] -= displacement[2]

        distace_between_atoms_1_2 = compute_distace(mol_dist[self.atom1], mol_dist[self.atom2])
        return mol_dist, distace_between_atoms_1_2

    def print_out(self):
        print("Atom 1 is: %s\nAtom 2 is: %s" % (self.molecule[self.atom1][0],
                                                self.molecule[self.atom2][0]))



def get_distortion_distances(path_to_file):
    try:
        with open(path_to_file) as file:
            data = file.read()
    except FileNotFoundError:
        raise Exception("File '%s' doesn't exist" % path_to_file)
    data = data.splitlines()
    data = [float(i.split("dist=")[1]) for i in data if i[0] == "#"]
    return data

