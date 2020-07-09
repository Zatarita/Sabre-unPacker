from os import system, path, remove

from Sabre.s3dpak import s3dpak
from Sabre.ipak import ipak

from UI.logic.import_dialog import import_dialog

from PyQt5 import uic
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTreeWidgetItem, QMessageBox, QHeaderView, QMenu

class SuP(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('UI/main.ui', self)
        self.file_name = ""
        self.original_path = ""
        self.contents = s3dpak()
        self.tree_widget_items = []
        self.context = QMenu()

        self.menu_handler = {
        "Open" : self.file_open,
        "Save As.." : self.file_save_as,
        "Save" : self.file_save,
        "Delete File" : self.select_delete,
        "Select All" : self.select_select_all,
        "Invert Selection" : self.select_invert_selection,
        "Deselect" : self.select_deselect,
        "Extract" : self.select_extract,
        "Extract all" : self.select_extract_all,
        "Import" : self.select_import,
        "About" : self.help_about,
        "Report a Bug" : self.help_bug_report,}


        self.menubar.triggered.connect(self.menu_item_triggered)
        self.file_display.customContextMenuRequested.connect(self.context_menu_init)
        self.setup_context()

        self.import_window = import_dialog()
        return



    def menu_item_triggered(self, menu_item):
        action_function = self.menu_handler.get(menu_item.text(), None)
        if action_function: action_function()
        return

    def file_open(self):
        del self.contents
        self.contents = None
        self.original_path, _ = QFileDialog.getOpenFileName(self, "sabre 3d file", "", "s3dpak (*.s3dpak);;ipak (*.ipak)")
        if self.original_path == "": return
        self.file_name = QFileInfo(self.original_path)
        self.decompress()

        msgBox = QMessageBox()
        msgBox.setText("Unable to open file..")
        msgBox.setStandardButtons(QMessageBox.Ok)

        if self.file_name.completeSuffix() == "s3dpak":
            self.contents = s3dpak(open("TMP/" + self.file_name.fileName() + "_decompressed", "rb"))

        if self.file_name.completeSuffix() == "ipak":
            if not path.exists(self.file_name.absolutePath() + "/" + self.file_name.baseName() + ".csv"):
                msgBox.setInformativeText("Unable to locate .csv")
                msgBox.exec()
                return
            self.contents = ipak(open("TMP/" + self.file_name.fileName() + "_decompressed", "rb"),
                open(self.file_name.absolutePath() + "/" + self.file_name.baseName() + ".csv", "r"))

        remove("TMP/" + self.file_name.fileName() + "_decompressed")
        self.update_UI()
        return

    def file_save_as(self):
        file, _ = QFileDialog.getSaveFileName(self, 'Save File', "", "s3dpak (*.s3dpak)")
        if file == "": return
        info = QFileInfo(file)
        self.contents.save("TMP/" + info.fileName())
        self.compress("TMP/" + info.fileName(), file)
        remove("TMP/" + info.fileName())

    def file_save(self):
        pass

    def select_delete(self):
        items = self.file_display.selectedItems()
        if len(items) == 0: return
        msgBox = QMessageBox()
        msgBox.setText("Are you sure you want to delete this file?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        result = msgBox.exec()

        if result == QMessageBox.Cancel:
            return
        else:
            for item in items:
                 self.contents.blocks.pop(item.text(1))
                 self.file_display.takeTopLevelItem(self.file_display.indexFromItem(item).row())
        self.contents.recalculate_offsets()
        self.update_UI()

    def select_select_all(self):
        for i in range(self.file_display.topLevelItemCount()):
            self.file_display.topLevelItem(i).setSelected(True)
        pass

    def select_invert_selection(self):
        for i in range(self.file_display.topLevelItemCount()):
            if self.file_display.topLevelItem(i) in self.file_display.selectedItems():
                self.file_display.topLevelItem(i).setSelected(False)
            else:
                self.file_display.topLevelItem(i).setSelected(True)
        pass

    def select_deselect(self):
        self.file_display.clearSelection()
        pass

    def select_extract(self):
        items = self.file_display.selectedItems()
        if len(items) == 0: return
        file_path = QFileDialog.getExistingDirectory(self, "Extraction directory")
        if file_path == "": return
        for item in items:
            self.contents.blocks[item.text(1)].extract(file_path)
        return

    def select_extract_all(self):
        file_path = QFileDialog.getExistingDirectory(self, "Extraction directory")
        if file_path == "": return
        for item in self.contents.blocks.values():
            item.extract(file_path)
        return

    def select_import(self):
        if self.import_window.exec() == 0: return

        for item in self.import_window.tree_widget_items:
            if item.text == "": continue
            imported_file = s3dpak.block()
            imported_file = imported_file.import_block(item.text, item.type_combo.currentText())
            self.contents.blocks.update({imported_file.string : imported_file})
            self.contents.recalculate_offsets()
            self.update_UI()
        self.import_window = import_dialog()

    def help_about(self):
        pass

    def help_bug_report(self):
        pass


    def decompress(self):
        system('ceaflate\\ceaflate.exe d "' + self.original_path + '" "TMP/' + self.file_name.fileName() + '_decompressed"')

    def compress(self, file, path):
        system('ceaflate\\ceaflate.exe c "' + file + '" "' + path + '"')

    def update_UI(self):
        self.file_display.clear()
        self.tree_widget_items.clear()

        self.create_tree_widget_items()
        self.file_display.addTopLevelItems(self.tree_widget_items)
        self.file_display.resizeColumnToContents(0)
        self.file_display.resizeColumnToContents(2)
        self.file_display.resizeColumnToContents(3)
        self.file_display.header().setStretchLastSection(False)
        self.file_display.header().setSectionResizeMode(1, QHeaderView.Stretch)

    def create_tree_widget_items(self):
        for block in self.contents.blocks.values():
            self.tree_widget_items.append(QTreeWidgetItem([s3dpak.s3d_type_definitions.get(block.type, block.type).split(" (")[0] ,block.string, hex(block.offset), str(block.size)]))

    def context_menu_init(self, event):
        action = self.context.exec_(QCursor().pos())
        pass

    def setup_context(self):
        select_all_action = self.context.addAction("Select all")
        select_all_action.triggered.connect(self.select_select_all)
        invert_selection_action = self.context.addAction("Invert selection")
        invert_selection_action.triggered.connect(self.select_invert_selection)
        deselect_action = self.context.addAction("Deselect")
        deselect_action.triggered.connect(self.select_deselect)
        self.context.addSeparator()
        extract_action = self.context.addAction("Extract")
        extract_action.triggered.connect(self.select_extract)
        extract_all_action = self.context.addAction("Extract all")
        extract_all_action.triggered.connect(self.select_extract_all)
        self.context.addSeparator()
        delete_action = self.context.addAction("Delete")
        delete_action.triggered.connect(self.select_delete)
        import_action = self.context.addAction("Import")
        import_action.triggered.connect(self.select_import)
