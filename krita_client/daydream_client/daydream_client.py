import urllib.request
from krita import Krita, DockWidget, DockWidgetFactoryBase, DockWidgetFactory, Extension
from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QMessageBox, QAction

APPLICATION =  Krita.instance()
HOST = "127.0.0.1"
PORT = "8000"
FILE_REQUEST_ROOT = f"http://{HOST}:{PORT}/files/"
API_KEY = "Set your own darn API Key :)"

def write_remote_image_to_layer(name):
    current_document =  APPLICATION.activeDocument()
    req = urllib.request.Request(f"{FILE_REQUEST_ROOT}{name}")
    req.add_header('x-api-key', API_KEY)
    contents = urllib.request.urlopen(req).read()
    with open("test.png", "wb") as f:
        f.write(contents)
    new_file_layer = current_document.createFileLayer(name, "test.png", None)
    new_paint_layer = current_document.createNode(name, "paintLayer")
    new_group_layer = current_document.createNode(name, "groupLayer")
    new_group_layer.setChildNodes([new_file_layer, new_paint_layer])
    root = current_document.rootNode()
    child_nodes = root.childNodes()
    root.addChildNode(new_group_layer, child_nodes[0]) 
    current_document.refreshProjection()



class DaydreamClient(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def get_daydream(self):
        # QMessageBox creates quick popup with information
        messageBox = QMessageBox()        
        messageBox.setInformativeText(APPLICATION.version())
        messageBox.setWindowTitle('System Check')
        messageBox.setText("Hello! Here is the version of Krita you are using.");
        messageBox.setStandardButtons(QMessageBox.Close)
        messageBox.setIcon(QMessageBox.Information)
        messageBox.exec()        

    def createActions(self, window):
        action = window.createAction("", "Get DayDream")
        action.triggered.connect(self.get_daydream)


Krita.instance().addExtension(DaydreamClient(Krita.instance()))