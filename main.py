import os

import napari
import napari._qt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# ideas:
# - Retrieve data lost removing rectangles -> undo -> done
# - Comment the code -> done
# - reorganize the code -> done
# - Document what changed in the Napari library -> done
# - Add Visual_AI logo as icon -> done
# - Get all the rectangles when user removes one -> in futur
# documentation sur ce qu'on peut faire pour le futur (améliorations à venir)
# - If the user clicks on "live - view", program show a message box ? -> yes (and make focus on yes Qpushbutton) -> done
# ajouter un fichier de config ou on inscrit tous les chemins d'accès en dur -> done
# chargement de la photo à la main (simulation d'un vrai essai) -> done
# create a pyqt app to transform the style of the QMessageBox

__author__ = "Tristan Cotte, https://tcotte.github.io/Portfolio/"
__version__ = "$Revision: 0.0 $"
__date__ = "$Date: 01/19/2022 $"
__copyright__ = "Copyright 2022 SGS"



def init_viewer():
    """
    Set up Napari's viewer
    """
    n_viewer = napari.Viewer(title='SGS - Visual_AI')
    # n_viewer.window._qt_window.setWindowIcon(QIcon(os.path.join(ROOT_DIR, r"src\logos\visual_ai.ico")))
    n_viewer.window._qt_window.setWindowState(Qt.WindowMaximized)
    n_viewer.window.qt_viewer.dockLayerList.setVisible(False)
    n_viewer.window.main_menu.setVisible(False)
    return n_viewer

if __name__ == '__main__':

    viewer = init_viewer()
    # viewer.window.add_dock_widget(LiveForm(viewer), name="Camera")

    napari.run()

