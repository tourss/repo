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
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # UI 최상단 고정
        ui_file.close()

        self.import_node()
        self.ui.pushButton_export.clicked.connect(self.json_export)
        self.ui.pushButton_export.clicked.connect(self.export_template)
        self.ui.pushButton_import.clicked.connect(self.open_template_list)
        self.ui.lineEdit_templateName.textChanged.connect(self.read_template_nodes)
        self.ui.pushButton_importScript.clicked.connect(self.import_script)

    def import_node(self):
        nodes = nuke.selectedNodes()
        node_list = []
        
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

    def receive_template_name(self, selected_name):
        self.ui.lineEdit_templateName.clear()
        self.ui.lineEdit_templateName.setText(selected_name)

    def read_template_nodes(self):
        json_template_name = self.ui.lineEdit_templateName.text()
        json_read_path = f"/home/rapa/test_python/0808/nuke/template/{json_template_name}.json"

        if os.path.exists(json_read_path):
            with open(json_read_path, 'r', encoding="UTF-8") as f:
                template_dict = json.load(f)
                read_node_list = template_dict[json_template_name]
                self.ui.listWidget.clear()
                self.ui.listWidget.addItems(read_node_list)

    def json_export(self):            
        path = nuke.scriptName()
        json_path = os.path.dirname(path)

        template_name = self.ui.lineEdit_templateName.text()
       
        node_datas = {}
        node_datas[template_name] = self.import_node()
        
        json_path = f"{json_path}/{template_name}.json"
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
import node_template
reload(node_template)
win = node_template.Node_Template()
win.show()
"""


# 노드그래프에서 노드들을 선택한 다음 ui에서 버튼을 누르면
# 선택한 노드들이 익스포트 되는데, 지정된 경로 (본인이 정해주세요)
# 파일이 저장되는데, 저장되는 이름을 정해주셔야 
# 나중에 그 파일들 중 저장된 이름으로 불러올 수도 있을 것 같습니다

