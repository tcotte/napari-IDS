import os
import pathlib
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox, QWidget
from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from napari._qt.qthreading import thread_worker

from video_ui import initui


class LiveIDS(QWidget):
    ten_frames = pyqtSignal(int)

    def __init__(self, napari_viewer):
        super(LiveIDS, self).__init__()

        # Attributes to compute fps
        self.start = time.time()
        self.end = 0

        self.exp_time_value = 50
        initui(self)
        self.viewer = napari_viewer

        # initialize ids_peak library
        ids_peak.Library.Initialize()

        self.init = True
        self.device = None
        self.nodemap_remote_device = None
        self.datastream = None
        self.acquisition_timer = QTimer()
        self.frame = 0
        self.live = False
        self.worker = None
        self.picture = []

        self.display()
        self.connect_actions()

    def display(self):
        """
        Define style for the Qdock_widget camera
        """
        self.setFixedSize(250, 340)

    def connect_actions(self):
        """
        Events
        """
        self.connect_cam_button.clicked.connect(self._on_connect_clicked)
        self.select_cam_combobox.currentIndexChanged.connect(self._on_select_cam)
        self.rec_button.clicked.connect(self._on_click_live)
        self.photo_button.clicked.connect(self._on_photo)
        self.exp_time_box.valueChanged.connect(self._on_exp_changed)
        # Signal when 10 frames appeared
        self.ten_frames.connect(self.refresh_fps)

    def refresh_fps(self):
        """
        Refresh the FPS counter when 10 frames were displayed
        """
        self.end = time.time()

        time_taken = self.end - self.start
        fps = int(np.around(10 / time_taken))

        if not self.counter_fps_label.isVisible():
            self.counter_fps_label.setVisible(True)
        self.counter_fps_label.setText("FPS : "+str(fps))

        self.start = time.time()

    def _on_exp_changed(self):
        """
        Change the exposure time
        """
        self.exp_time_value = self.exp_time_box.value()
        self.nodemap_remote_device.FindNode("ExposureTime").SetValue(self.exp_time_value * 1000)

    def stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        """
        # Try to stop acquisition
        try:
            # Stop acquisition timer and camera acquisition
            self.acquisition_timer.stop()
            remote_nodemap = self.device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush datastream
            self.datastream.KillWait()
            self.datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
            self.datastream = None

            # Unlock parameters after acquisition stop
            if self.nodemap_remote_device is not None:
                try:
                    self.nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

        except Exception as e:
            QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

    def _on_photo(self):
        """
        Photo event -> Remove the "Video" layer and display only the last picture as "Image" layer
        """
        self.live = False
        self.trigger_buttons(True)

        # Save the picture to run the model on this picture after
        self.picture = cv2.cvtColor(self.viewer.layers['Video'].data, cv2.COLOR_BGR2RGB)

        now = datetime.now()
        filename = os.path.join(Path.home(), 'Pictures', now.strftime('%d_%m_%Y_%H_%M_%S') + '.png')
        cv2.imwrite(filename, self.picture)

        # Confirm to run the model
        self.confirmation_message_box(filename)

    def confirmation_message_box(self, filename):
        """
        Confirmation box to run the model or not
        """
        msg = QMessageBox()

        # Remember the program chosen by the user
        msg.setText("The capture was successfully recorded as \n" + filename)
        msg.setWindowTitle("Confirmation - Capture")
        msg.setStandardButtons(QMessageBox.Ok)

        val = msg.exec_()
        if val == QMessageBox.Ok:
            self.start_acquisition()

    def trigger_buttons(self, photo_boolean):
        """
        Enable one button and disalbe other
        :param photo_boolean: Type of program use, if it is not "Photo", it is "Video"
        """
        self.rec_button.setEnabled(photo_boolean)
        self.photo_button.setEnabled(not photo_boolean)

        # Cursor decoration
        if photo_boolean:
            self.rec_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        else:
            self.photo_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

    def _on_click_live(self):
        """
        When the user clicks on the button "Live - view", the behaviour of the program change if the formulary is opened
        """

        self.setStyleSheet(
            open(os.path.join(pathlib.Path(__file__).parent.resolve(), "stylesheets/widget_live.css")).read())

        self.start_acquisition()

    def start_acquisition(self):
        """
        set up some parameters of the camera to take video further
        """
        self.trigger_buttons(False)
        self.remove_layer("Image")

        if self.datastream is None:
            self.open_device()

        # Configure exposure time
        self.nodemap_remote_device.FindNode("ExposureTime").SetValue(self.exp_time_value * 1000)
        max_fps = self.nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
        # fix max fps
        target_fps = min(max_fps, 30)
        self.nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)

        # Setup the clock of the thread which displays the video
        self.aquisition_period = 1 / target_fps

        try:
            # Lock critical features to prevent them from changing during acquisition
            self.nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition on camera
            self.datastream.StartAcquisition()
            self.nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()

            print("max fps ", max_fps)

        except Exception as e:
            print("Exception: " + str(e))
            return False

        if self.worker is None:
            self.worker = self.on_acquisition_timer()
            self.worker.yielded.connect(self.update_display)
            self.worker.start()

        return True

    @staticmethod
    def get_image(buffer):
        """
        Get picture from the buffer and convert it to numpy picture
        :param buffer: current buffer data
        :return: numpy RGB 3 channels picture
        """
        # Create IDS peak IPL image from buffer
        ipl_image = ids_peak_ipl.Image_CreateFromSizeAndBuffer(
            buffer.PixelFormat(),
            buffer.BasePtr(),
            buffer.Size(),
            buffer.Width(),
            buffer.Height()
        )
        # Convert picture in RGB and transform this picture in array with 3 channels
        converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_RGB8)
        image_without_alpha = converted_ipl_image.get_numpy_3D()
        return image_without_alpha

    def remove_layer(self, layer_name):
        """
        Remove layer if it exists
        :param layer_name: Name of the layer
        """
        if layer_name in self.viewer.layers:
            self.viewer.layers.remove(layer_name)

    @thread_worker
    def on_acquisition_timer(self):
        """
        Get image from the buffer and transmit it
        :return: yield RGB picture
        """
        while self.viewer.window.qt_viewer:
            buffer = self.datastream.WaitForFinishedBuffer(5000)

            image_rgb = self.get_image(buffer)

            self.datastream.QueueBuffer(buffer)

            yield image_rgb

            # Take time between two sends of pictures
            time.sleep(self.aquisition_period)


    def update_display(self, image):
        """
        Update the display replacing the old with the new picture in the "Video" layer
        :param image: RGB picture
        """
        # Add new layer if "Video" layer does not exist else overwrite on it
        if self.frame == 0:
            self.viewer.add_image(image, name="Video", blending='additive', rgb=True)
        else:
            self.viewer.layers["Video"].data = image
        self.frame += 1

        # Refresh the FPS when 10 pictures were displayed
        if self.frame % 10 == 0:
            self.ten_frames.emit(self.frame)



    @staticmethod
    def remove_controls(grid):
        """
        Remove the gridLayout of the control layer
        :param grid: specify which grid we have to remove
        """
        for i in range(grid.count()):
            widget = grid.itemAt(i).widget()
            if not isinstance(widget, type(None)):
                widget.close()

    def _on_select_cam(self, index):
        """
        Connect the camera selected in the drop-down menu
        :param index: index of the item selected in the drop-down menu
        """
        # create a device manager object
        device_manager = ids_peak.DeviceManager.Instance()

        # update the device manager
        device_manager.Update()

        selected_device = index
        self.device = device_manager.Devices()[selected_device].OpenDevice(ids_peak.DeviceAccessType_Control)
        # get the remote device node map
        self.nodemap_remote_device = self.device.RemoteDevice().NodeMaps()[0]

        self.camera_label.setText("Connected to : " + self.device.ModelName())
        # Set visible some widgets
        self.visible_widgets(3)

        self.open_device()

    def visible_widgets(self, start_index):
        """
        Set visible some widget which were invisible
        :param start_index: index of item in grid from which we make visible the widgets
        """
        for i in range(start_index, self.layout.count()):
            self.layout.itemAt(i).widget().setVisible(True)

    def open_device(self):
        """
        Open the device
        """
        # Open standard data stream
        datastreams = self.device.DataStreams()
        if datastreams.empty():
            QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.Ok)
            self.device = None

        self.datastream = datastreams[0].OpenDataStream()

        if self.device is not None:
            # Get nodemap of the remote device for all accesses to the genicam nodemap tree
            self.nodemap_remote_device = self.device.RemoteDevice().NodeMaps()[0]
        else:
            QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.Ok)

        # To prepare for untriggered continuous image acquisition, load the default user set if available and
        # wait until execution is finished
        try:
            self.nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
            self.nodemap_remote_device.FindNode("UserSetLoad").Execute()
            self.nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
        except ids_peak.Exception:
            # Userset is not available
            print("No userset")
            pass

        # Get the payload size for correct buffer allocation
        payload_size = self.nodemap_remote_device.FindNode("PayloadSize").Value()

        # Get minimum number of buffers that must be announced
        buffer_count_max = self.datastream.NumBuffersAnnouncedMinRequired()

        # Allocate and announce image buffers and queue them
        for i in range(buffer_count_max):
            buffer = self.datastream.AllocAndAnnounceBuffer(payload_size)
            self.datastream.QueueBuffer(buffer)

    def show_error_box(self):
        """
        Show QMessageBox when there are not IDS camera plugged
        """
        msg = QMessageBox()
        msg.setWindowIcon(self.icon)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("There is not any IDS camera plugged")
        msg.setInformativeText("Please plug a camera and retry")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def list_ids_cameras(self):
        """
        List all the IDS devices in a drop-down menu
        """
        # create a device manager object
        device_manager = ids_peak.DeviceManager.Instance()

        # update the device manager
        device_manager.Update()

        # exit program if no device was found
        if device_manager.Devices().empty():
            self.show_error_box()
        else:
            self.select_cam_combobox.setVisible(True)

        # list all available devices
        for device in device_manager.Devices():
            self.select_cam_combobox.addItem(device.ModelName())

    def _on_connect_clicked(self):
        """
        Signal when user clicks on "Connect camera"
        """
        self.connect_cam_button.setEnabled(False)
        self.list_ids_cameras()