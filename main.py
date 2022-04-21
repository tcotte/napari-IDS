from widget import LiveIDS
import napari

if __name__ == '__main__':
    viewer = napari.Viewer()
    viewer.window.add_dock_widget(LiveIDS(viewer))
    napari.run()