import os
from typing import List


def default_molecules(path: str = None) -> List[str]:
    """Returns a list of the molecules in the 'default_molecules' directory or directory given by the path"""
    if not path:
        path = "%s/default_molecules" % os.path.dirname(__file__)
    mol_list = [i.split(".")[0] for i in os.listdir(path)]
    return mol_list


def load_molecule(formula: str, path: str = None) -> str:
    """Loads a molecule from the 'default_molecules' directory or directory given by the path"""
    if not path:
        path = "%s/default_molecules" % os.path.dirname(__file__)

    try:
        with open("%s/%s.xyz" % (path, formula), 'r') as file:
            data = file.read()
    except FileNotFoundError:
        raise Exception("Molecule '%s' is not in '%s'" % (formula, path))
    return data
