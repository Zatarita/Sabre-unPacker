from PyQt5 import uic
from PyQt5.QtWidgets import QComboBox, QDialog, QFileDialog, QTreeWidgetItem, QTreeWidget, QPushButton, QHeaderView

from Sabre.s3dpak import s3dpak

class import_dialog(QDialog):
    class tree_widget_item():
        def __init__(self, parent):
            self.parent = parent
            self.type_combo = QComboBox()
            self.tree_widget = QTreeWidgetItem()
            self.browse_button = QPushButton()
            self.browse_button.setMaximumWidth(25)
            self.text = ""

            self.browse_button.clicked.connect(self.browse_file)
            self.type_combo.addItems(s3dpak.s3d_type_definitions.values())

            self.widget_item = QTreeWidgetItem()

        def browse_file(self):
            file, _ = QFileDialog.getOpenFileName(None, "file", "", "all files (*.*)")
            if file == "": return
            for item in self.parent.tree_widget_items:
                if item.text == file : return
            if self.text == "":
                self.parent.add_tree_item()
            self.text = file
            self.widget_item.setText(1, file)


        def populate_items(self, tree_widget):
            tree_widget.addTopLevelItem(self.widget_item)
            tree_widget.setItemWidget(self.widget_item, 0, self.type_combo)
            tree_widget.setItemWidget(self.widget_item, 2, self.browse_button)

            self.type_combo.setCurrentText("Template")
            return

    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi('UI/import.ui', self)
        self.tree_widget_items = []

        self.import_objects.header().resizeSection(0,150)
        self.import_objects.header().setStretchLastSection(False)
        self.import_objects.header().setSectionResizeMode(1, QHeaderView.Stretch)

        self.batch.clicked.connect(self.open_clicked)

        self.add_tree_item()

    def add_tree_item(self):
        item = self.tree_widget_item(self)
        self.tree_widget_items.append(item)
        item.populate_items(self.import_objects)

    def open_clicked(self, button):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        files, _ = file_dialog.getOpenFileNames(None, "file", "", "all files (*.*)")
        if len(files) == 0 : return
        for file in files:
            if self.tree_widget_items[0].text == "":
                self.tree_widget_items[0].text = file
                self.tree_widget_items[0].widget_item.setText(1, file)
                continue
            for widget_item in self.tree_widget_items:
                if widget_item.text == file : return
            item = self.tree_widget_item(self)
            self.tree_widget_items.append(item)
            item.populate_items(self.import_objects)
            item.text = file
            item.widget_item.setText(1, file)
        self.add_tree_item()
        return

