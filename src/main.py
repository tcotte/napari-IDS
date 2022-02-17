import os

import napari
import napari._qt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

__author__ = "Tristan Cotte, https://tcotte.github.io/Portfolio/"
__version__ = "$Revision: 0.0 $"
__date__ = "$Date: 01/19/2022 $"
__copyright__ = "Copyright 2022 SGS"

from dock_widget_live import LiveForm


def init_viewer():
    """
    Set up Napari's viewer
    """
    n_viewer = napari.Viewer(title='IDS_APP')
    n_viewer.window._qt_window.setWindowState(Qt.WindowMaximized)
    # n_viewer.window.qt_viewer.dockLayerList.setVisible(False)
    # n_viewer.window.main_menu.setVisible(False)
    return n_viewer


if __name__ == '__main__':
    viewer = init_viewer()
    viewer.window.add_dock_widget(LiveForm(viewer), name="Camera")

    napari.run()
