# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 10:30:28 2022

@author: Ortiz Montufar Gerardo
"""

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

matplotlib.use("Qt5Agg")

class QMatplotlibCanvas(FigureCanvasQTAgg):
    """
    Basic PyQt-Matplotlib widget that creates a figure in the GUI
    """
    def __init__(self, parent=None, dpi=100, *args, **kwargs):
        """
        Widget constructor, that associates a figure with a QWidget
        """
        # Instantiate a Matplotlib figure at dpi resolution
        self.fig = Figure(dpi=dpi)
        # Link figure with PyQt widget
        super().__init__(self.fig)

    def setupCanvas(self, gridspec=(1, 1), axes=[(0, 1, 0, 1)], toolbar=False, x_label = ""):
        """
        Setup routine, that creates axes in the figure, from a specification
        given with a GridSpec (rows, columns), a list of axes, each defined
        as a tuple indicating de span (row_start, row_stop, col_start, col_stop)
        of the gridspec that each axes will occupy, and a boolean to add a
        toolbar to the figure.
        """
        # Create the required gridspec for the figure
        gs = self.fig.add_gridspec(gridspec[0], gridspec[1])
        
        # Crate axes for each specification in the list
        self.axes = [self.fig.add_subplot(gs[ri:rf+1,ci:cf+1],xlabel = "", ylabel = "Gain ($dB$)") for ri,rf,ci,cf in axes]
        
        # Add a toolbar if requested
        if toolbar:
            self.toolbar = NavigationToolbar2QT(self, self)
