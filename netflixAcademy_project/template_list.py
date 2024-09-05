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
    import nuke

import sys
import os
import json

class Template_List(QWidget):
    template_selected = Signal(str)

    def __init__(self):
        super().__init__()

        print ("world Hello")

        ui_file_path = "/home/rapa/test_python/0808/nuke/template_list.ui"
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        ui_file.close()

        self.get_template()
        self.import_template()

        self.ui.pushButton.clicked.connect(self.import_template_to_node_list)

    def get_template(self):
        json_read_path = f"/home/rapa/test_python/0808/nuke/template/template.json"

        if os.path.exists(json_read_path):
            with open(json_read_path, 'r', encoding="UTF-8") as f:
                template_dict = json.load(f)
        return template_dict

    def import_template(self):
        template_dict = self.get_template()
        template_names = template_dict.keys()
        for template_name in template_names:
            path = f"/home/rapa/test_python/0808/nuke/template/{template_name}.nknc"
            self.ui.listWidget.addItem(f"{template_name}\n{path}")
  
    def import_template_to_node_list(self):
        selected_item = self.ui.listWidget.currentItem()
        if selected_item:
            selected_name = selected_item.text().split("\n")[0]
            print (selected_name)
            self.template_selected.emit(selected_name)
            



# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     from node_template import Node_Template

#     node_window = Node_Template()
#     template_window = Template_List()

#     template_window.template_selected.connect(node_window.receive_template_name)

#     node_window.show()
#     template_window.show()

#     sys.exit(app.exec_())



        # path = "/home/rapa/test_python/0808/nuke/template"
        # file_list = os.listdir(path)
        # template_name_dict = {}
        # nknc_list = []
        
        # i = 0
        # for file in file_list:
        #     file_name = file.split(".")[0]
        #     nknc_list.append(file_name)
        #     template_path = os.path.abspath(os.path.join(path, file_name))
        #     template_name_dict[nknc_list[i]] = template_path
    
        #     i += 1
        # return template_name_dict




# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = Template_List()
#     window.show()
#     sys.exit(app.exec())    




"""
from importlib import reload
import sys
sys.path.append("/home/rapa/test_python/0808/nuke")
import template_list
reload(template_list)
win = template_list.Template_List()
win.show()
"""