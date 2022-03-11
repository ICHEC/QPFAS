name="qpfas"
"""
Module for molecular composition, manipulation and energy estimation as
part of qpfas project.
"""
import os
QPFAS_DIR = os.path.dirname(os.path.abspath(__file__))
from qpfas._version import __version__

from qpfas import chemistry
from qpfas import workflow
from qpfas import utils

def version():
    """Returns the QPFAS version number."""
    return __version__
