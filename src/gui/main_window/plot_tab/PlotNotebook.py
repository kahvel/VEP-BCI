from gui_elements.widgets.frames.notebooks import PlusNotebook
import PlotNotebookTab
import constants as c


class PlotNotebook(PlusNotebook.PlusNotebook):
    def __init__(self, parent, row, column, **kwargs):
        PlusNotebook.PlusNotebook.__init__(self, parent, c.MAIN_NOTEBOOK_PLOT_TAB, row, column, **kwargs)

    def newTab(self, deletaTab):
        return PlotNotebookTab.PlotNotebookTab(self, deletaTab)
