try:
    from PySide6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
    from PySide6.QtGui import Qt
    from PySide6.QtCore import QFile, QTime
    from PySide6.QtUiTools import QUiLoader

except:
    from PySide2.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem
    from PySide2.QtWidgets import QListWidget
    from PySide2.QtGui import Qt
    from PySide2.QtCore import QFile, QTime, Signal, QObject
    from PySide2.QtUiTools import QUiLoader
    from template_list import Template_List
    import nuke
    import nukescripts

import sys
import os
import json

class Node_Template(QWidget): 
    def __init__(self):
        super().__init__() 

        print ("hello_worldd")

        ui_file_path = "/home/rapa/test_python/0808/nuke/node_template.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader() 
        self.ui = loader.load(ui_file, self) 
        ui_file.close()

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # UI 최상단 고정


        # self.import_node()
        self.node_list = self.import_node()
        self.ui.pushButton_export.clicked.connect(self.json_export)
        self.ui.pushButton_export.clicked.connect(self.export_template)
        self.ui.pushButton_import.clicked.connect(self.open_template_list)
        self.ui.pushButton_importScript.clicked.connect(self.import_script)
        self.ui.lineEdit_templateName.returnPressed.connect(self.read_template_nodes)

    def import_node(self):
        nodes = nuke.selectedNodes()
        node_list = []
        
        self.ui.listWidget.clear()

        row = 0
        for node in sorted(nodes):
            node_name = node.name()
            self.ui.listWidget.addItem(node_name)
            node_list.append(node_name)
            row += 1
        return node_list
    
    def open_template_list(self):
        self.template_window = Template_List()
        self.template_window.show()
        self.template_window.template_selected.connect(self.receive_template_name)
        self.template_window.ui.pushButton.clicked.connect(self.connect_import_button)

    def connect_import_button(self):
        self.ui.lineEdit_templateName.textChanged.connect(self.read_template_nodes)

    def receive_template_name(self, selected_name):
        self.ui.lineEdit_templateName.clear()
        self.ui.lineEdit_templateName.setText(selected_name)

    # def check_nodes_by_lineEdit(self):
    #     json_template_name = self.ui.lineEdit_templateName.text()
    #     json_read_path = f"/home/rapa/test_python/0808/nuke/template/template.json"

    #     if os.path.exists(json_read_path):
    #         with open(json_read_path, 'r', encoding="UTF-8") as f:
    #             template_dict = json.load(f)
    #             read_node_list = template_dict[json_template_name]
    #             self.ui.listWidget.clear()
    #             self.ui.listWidget.addItems(read_node_list)

    def read_template_nodes(self):
        json_path = f"/home/rapa/test_python/0808/nuke/template/template.json"

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding="UTF-8") as f:
                template_dict = json.load(f)
                
        template_name = self.ui.lineEdit_templateName.text()
        read_node_list = template_dict.get(template_name, [])
        print (read_node_list)
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(read_node_list)

    def json_export(self):            
        json_path = "/home/rapa/test_python/0808/nuke/template/template.json"
        template_name = self.ui.lineEdit_templateName.text()

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding="UTF-8") as f:
                node_datas = json.load(f)
        else:
            node_datas = {}

        node_datas[template_name] = self.node_list

        nuke.scriptSave(json_path)

        with open(json_path, 'w', encoding="UTF-8") as f:
             json.dump(node_datas, f, indent=4, ensure_ascii=False)
        
        return json_path, node_datas
    
    def export_template(self):

        nukescripts.export_nodes_as_script()

    def import_script(self):

        nukescripts.import_script()


"""
from importlib import reload
import sys
sys.path.append("/home/rapa/test_python/0808/nuke")
import node_template2
reload(node_template2)
win = node_template2.Node_Template()
win.show()
"""
