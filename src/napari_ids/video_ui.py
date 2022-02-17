import os
import pathlib

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGridLayout, QLabel, QPushButton, QComboBox, QSpinBox


def initui(self):
    self.layout = QGridLayout()

    self.logo = QLabel()
    pixmap = QPixmap(os.path.join(pathlib.Path(__file__).parent.resolve(), r"img/logo_ids.jpg"))
    pixmap = pixmap.scaled(QSize(220, 220), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    self.logo.setPixmap(pixmap)
    self.logo.setAlignment(Qt.AlignHCenter)
    self.logo.setStyleSheet("QLabel{margin-bottom:20px;}")

    self.connect_cam_button = QPushButton("Connect camera")

    self.select_cam_combobox = QComboBox()
    self.select_cam_combobox.setVisible(False)

    self.camera_label = QLabel()

    self.rec_button = QPushButton("Live - view")
    self.rec_button.setObjectName("recButton")
    self.rec_button.setVisible(False)

    self.photo_button = QPushButton("Capture")
    self.photo_button.setObjectName("photoButton")
    self.photo_button.setVisible(False)
    self.photo_button.setEnabled(False)

    self.exp_time_label = QLabel("Exposure time (ms)")
    self.exp_time_label.setVisible(False)
    self.exp_time_box = QSpinBox()
    self.exp_time_box.setMinimum(1)
    self.exp_time_box.setMaximum(300)
    self.exp_time_box.setValue(self.exp_time_value)
    self.exp_time_box.setVisible(False)

    self.layout.addWidget(self.logo, 0, 0, 1, 2)
    self.layout.addWidget(self.connect_cam_button, 1, 0, 1, 2, Qt.AlignTop)
    self.layout.addWidget(self.select_cam_combobox, 2, 0, 1, 2, Qt.AlignTop)
    self.layout.addWidget(self.camera_label, 3, 0, 1, 2, Qt.AlignTop)
    self.layout.addWidget(self.exp_time_label, 4, 0, 1, 1, Qt.AlignTop)
    self.layout.addWidget(self.exp_time_box, 4, 1, 1, 1, Qt.AlignTop)
    self.layout.addWidget(self.rec_button, 7, 0, 1, 1, Qt.AlignBottom)
    self.layout.addWidget(self.photo_button, 7, 1, 1, 1, Qt.AlignBottom)
    self.layout.setContentsMargins(0, 0, 0, 0)

    self.setLayout(self.layout)
