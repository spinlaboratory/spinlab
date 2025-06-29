"""Modules to generate matplotlib plots from slData objects"""

from .general import *
from .stack_plot import *
from .image import *
from .colors import *

# We import matplotlib at this point so all functions of the pyplot module are generally available in SpinLab.
import matplotlib.pyplot as plt
