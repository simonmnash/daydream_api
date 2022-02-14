from urllib import request, parse
from krita import Krita, DockWidget, DockWidgetFactoryBase, DockWidgetFactory, Extension
from krita import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QMessageBox, QAction
import json

APPLICATION =  Krita.instance()
HOST = "127.0.0.1"
PORT = "8000"
FILE_REQUEST_ROOT = f"https://daydream.jamfort.io/newlayer"
API_KEY = ""

def write_remote_image_to_layer(name, iterations):
    current_document =  APPLICATION.activeDocument()
    data = json.dumps({'prompt': name, 'start': 0, 'end': iterations}).encode('utf8')
    req = request.Request(f"{FILE_REQUEST_ROOT}", data=data)
    req.add_header('x-api-key', API_KEY)
    req.add_header("Content-Type", "application/json")
    contents = request.urlopen(req, timeout=1000000000)
    with open("test.png", "wb") as f:
        f.write(contents.read())
    new_file_layer = current_document.createFileLayer(name, "test.png", None)
    new_paint_layer = current_document.createNode(name, "paintLayer")
    new_group_layer = current_document.createNode(name, "groupLayer")
    new_group_layer.setChildNodes([new_file_layer, new_paint_layer])
    root = current_document.rootNode()
    child_nodes = root.childNodes()
    root.addChildNode(new_group_layer, child_nodes[0]) 
    current_document.refreshProjection()
import threading
x = threading.Thread(target=write_remote_image_to_layer, args=("Dragon on the wind (Roccoco Painting)", 5))
x.start()
#write_remote_image_to_layer("I love you like the sun loves the moon (metalwork)")