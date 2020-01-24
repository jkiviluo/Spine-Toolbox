######################################################################################################################
# Copyright (C) 2017 - 2019 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains a class for a widget that presents a 'Select Project Directory' dialog.

:author: P. Savolainen (VTT)
:date: 1.11.2019
"""

import logging
import os
from PySide2.QtWidgets import QDialog, QFileSystemModel, QAbstractItemView, QAction, QComboBox
from PySide2.QtCore import Qt, Slot, QDir, QStandardPaths, QTimer, QModelIndex, QItemSelectionModel
from PySide2.QtGui import QKeySequence, QValidator
from spinetoolbox.helpers import ProjectDirectoryIconProvider
from spinetoolbox.widgets.notification import Notification
from spinetoolbox.widgets.custom_menus import OpenProjectDialogComboBoxContextMenu


class OpenProjectDialog(QDialog):
    """A dialog that let's user select a project to open either by choosing
    an old .proj file or by choosing a project directory."""

    def __init__(self, toolbox):
        """

        Args:
            toolbox (ToolboxUI): QMainWindow instance
        """
        from ..ui import open_project_dialog

        super().__init__(parent=toolbox, f=Qt.Dialog)  # Setting the parent inherits the stylesheet
        self._toolbox = toolbox
        # Set up the user interface from Designer file
        self.ui = open_project_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.combobox_context_menu = None
        # Ensure this dialog is garbage-collected when closed
        self.setAttribute(Qt.WA_DeleteOnClose)
        # QActions for keyboard shortcuts
        self.go_root_action = QAction(self)
        self.go_home_action = QAction(self)
        self.go_documents_action = QAction(self)
        self.go_desktop_action = QAction(self)
        self.set_keyboard_shortcuts()
        self.selected_path = ""
        self.cb_ss = self.ui.comboBox_current_path.styleSheet()
        self.file_model = CustomQFileSystemModel()
        self.file_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.icon_provider = ProjectDirectoryIconProvider()
        self.file_model.setIconProvider(self.icon_provider)
        self.file_model.setRootPath(QDir.rootPath())
        self.ui.treeView_file_system.setModel(self.file_model)
        # Read recent project directories and populate combobox
        recents = self._toolbox.qsettings().value("appSettings/recentProjectStorages", defaultValue=None)
        if recents:
            recents_lst = str(recents).split("\n")
            self.ui.comboBox_current_path.insertItems(0, recents_lst)
        self.ui.comboBox_current_path.setCurrentIndex(-1)
        # Go and select root immediately
        root_index = self.file_model.index(QDir.rootPath())
        self.ui.treeView_file_system.setCurrentIndex(root_index)
        self.ui.treeView_file_system.expand(root_index)
        self.ui.treeView_file_system.resizeColumnToContents(0)
        self.file_model.sort(0, Qt.AscendingOrder)
        self.set_selected_path(root_index)
        # Enable validator (experimental, not very useful here)
        # Validator prevents typing Invalid strings to combobox. (Not in use)
        # When text in combobox is Intermediate, the validator prevents emitting
        # currentIndexChanged signal when enter is pressed.
        # Pressing enter still triggers the done() slot of the QDialog.
        self.validator = DirValidator()
        self.ui.comboBox_current_path.setValidator(self.validator)
        self.ui.comboBox_current_path.setInsertPolicy(QComboBox.NoInsert)
        # Override QCombobox keyPressEvent to catch the Enter key press
        self.ui.comboBox_current_path.keyPressEvent = self.combobox_key_press_event
        self.connect_signals()

    def set_keyboard_shortcuts(self):
        """Creates keyboard shortcuts for the 'Root', 'Home', etc. buttons."""
        self.go_root_action.setShortcut(QKeySequence(Qt.Key_F1))
        self.addAction(self.go_root_action)
        self.go_home_action.setShortcut(QKeySequence(Qt.Key_F2))
        self.addAction(self.go_home_action)
        self.go_documents_action.setShortcut(QKeySequence(Qt.Key_F3))
        self.addAction(self.go_documents_action)
        self.go_desktop_action.setShortcut(QKeySequence(Qt.Key_F4))
        self.addAction(self.go_desktop_action)

    def connect_signals(self):
        """Connects signals to slots."""
        self.ui.toolButton_root.clicked.connect(self.go_root)
        self.ui.toolButton_home.clicked.connect(self.go_home)
        self.ui.toolButton_documents.clicked.connect(self.go_documents)
        self.ui.toolButton_desktop.clicked.connect(self.go_desktop)
        self.ui.comboBox_current_path.editTextChanged.connect(self.combobox_text_edited)
        self.ui.comboBox_current_path.currentIndexChanged.connect(self.current_index_changed)
        self.ui.comboBox_current_path.customContextMenuRequested.connect(self.show_context_menu)
        self.validator.changed.connect(self.validator_state_changed)
        self.ui.treeView_file_system.clicked.connect(self.set_selected_path)
        self.ui.treeView_file_system.selectionModel().currentChanged.connect(self.current_changed)
        self.go_root_action.triggered.connect(self.go_root)
        self.go_home_action.triggered.connect(self.go_home)
        self.go_documents_action.triggered.connect(self.go_documents)
        self.go_desktop_action.triggered.connect(self.go_desktop)

    def combobox_key_press_event(self, e):
        """Interrupts Enter and Return key presses when QComboBox is in focus.
        This is needed to prevent showing the 'Not a valid Spine Toolbox project'
        Notifier every time Enter is pressed.

        Args:
            e (QKeyEvent): Received key press event.
        """
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            state = self.ui.comboBox_current_path.validator().state
            fm_current_index = self.ui.treeView_file_system.currentIndex()
            if state == QValidator.Intermediate:
                # Remove entry from qsettings and combobox if present
                self.remove_directory_from_recents(os.path.abspath(self.selection()))
                notification = Notification(self, "Path does not exist")
                notification.show()
            elif state == QValidator.Acceptable:
                p = self.ui.comboBox_current_path.currentText()
                fm_index = self.file_model.index(p)
                if not fm_current_index == fm_index:
                    self.ui.treeView_file_system.setCurrentIndex(fm_index)
                    QTimer.singleShot(150, self.update_filesystem_treeview)
                else:
                    project_json_fp = os.path.abspath(os.path.join(self.selection(), ".spinetoolbox", "project.json"))
                    if os.path.isfile(project_json_fp):
                        self.done(QDialog.Accepted)
            else:
                # INVALID (or None). Happens if Enter key is pressed and the combobox text has not been edited yet.
                pass
            e.accept()
        else:
            QComboBox.keyPressEvent(self.ui.comboBox_current_path, e)

    @Slot()
    def validator_state_changed(self):
        """Changes the combobox border color according to the current state of the validator."""
        state = self.ui.comboBox_current_path.validator().state
        if state == QValidator.Acceptable:
            self.ui.comboBox_current_path.setStyleSheet(self.cb_ss)
        elif state == QValidator.Intermediate:
            ss = "QComboBox {border: 1px solid #ff704d}"
            self.ui.comboBox_current_path.setStyleSheet(ss)
        else:  # Invalid. This is never returned.
            ss = "QComboBox {border: 1px solid #ff3300}"
            self.ui.comboBox_current_path.setStyleSheet(ss)

    @Slot(int)
    def current_index_changed(self, i):
        """Combobox selection changed. This slot is processed when a new item
        is selected from the drop-down list. This is not processed when new
        item txt is QValidotor.Intermediate.

        Args:
            i (int): Selected row in combobox
        """
        p = self.ui.comboBox_current_path.itemText(i)
        fm_index = self.file_model.index(p)
        self.ui.treeView_file_system.setCurrentIndex(fm_index)
        QTimer.singleShot(150, self.update_filesystem_treeview)

    @Slot("QModelIndex", "QModelIndex", name="current_changed")
    def current_changed(self, current, previous):
        """Processed when the current item in file system tree view has been
        changed with keyboard or mouse. Updates the text in combobox the combobox.

        Args:
            current (QModelIndex): Currently selected index
            previous (QModelIndex): Previously selected index
        """
        self.set_selected_path(current)

    @Slot("QModelIndex", name="set_selected_path")
    def set_selected_path(self, index):
        """Sets the text in the combobox as the selected path in the file system tree view.

        Args:
            index (QModelIndex): The index which was mouse clicked.
        """
        if not index.isValid():
            return
        selected_path = os.path.abspath(self.file_model.filePath(index))
        self.ui.comboBox_current_path.setCurrentText(selected_path)  # Emits editTextChanged signal
        self.selected_path = selected_path

    @Slot(str)
    def combobox_text_edited(self, text):
        """Updates selected path when combobox text is edited.
        Note: pressing enter in combobox does not trigger this.
        """
        self.selected_path = text

    def update_filesystem_treeview(self):
        """Scrolls the file system tree view to the current index (path)."""
        self.ui.treeView_file_system.collapseAll()
        index = self.ui.treeView_file_system.currentIndex()
        self.ui.treeView_file_system.scrollTo(index, hint=QAbstractItemView.PositionAtTop)
        self.ui.treeView_file_system.expand(index)
        self.ui.treeView_file_system.resizeColumnToContents(0)
        self.set_selected_path(index)

    def selection(self):
        """Returns the selected path from dialog."""
        return self.selected_path

    @Slot(bool, name="go_root")
    def go_root(self, checked=False):
        """Slot for the 'Root' button. Scrolls the treeview to show and select the user's root directory."""
        root_index = self.file_model.index(QDir.rootPath())
        self.ui.treeView_file_system.setCurrentIndex(root_index)
        QTimer.singleShot(150, self.update_filesystem_treeview)

    @Slot(bool, name="go_home")
    def go_home(self, checked=False):
        """Slot for the 'Home' button. Scrolls the treeview to show and select the user's home directory."""
        home_index = self.file_model.index(QDir.homePath())
        self.ui.treeView_file_system.setCurrentIndex(home_index)
        QTimer.singleShot(150, self.update_filesystem_treeview)

    @Slot(bool, name="go_documents")
    def go_documents(self, checked=False):
        """Slot for the 'Documents' button. Scrolls the treeview to show and select the user's documents directory."""
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        if not docs:
            logging.error("No documents found on your OS")
            return
        docs_index = self.file_model.index(docs)
        self.ui.treeView_file_system.setCurrentIndex(docs_index)
        QTimer.singleShot(150, self.update_filesystem_treeview)

    @Slot(bool, name="go_desktop")
    def go_desktop(self, checked=False):
        """Slot for the 'Desktop' button. Scrolls the treeview to show and select the user's desktop directory."""
        desktop = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)  # Return a list
        if not desktop:
            logging.error("No desktop found on your OS")
            return
        desktop_index = self.file_model.index(desktop)
        self.ui.treeView_file_system.setCurrentIndex(desktop_index)
        QTimer.singleShot(150, self.update_filesystem_treeview)

    def done(self, r):
        """Checks that selected path exists and is a valid
        Spine Toolbox directory when ok button is clicked or
        when enter is pressed without the combobox being in focus.

        Args:
            r (int) Return code
        """
        if r == QDialog.Accepted:
            if not os.path.isdir(self.selection()):
                notification = Notification(self, "Path does not exist")
                notification.show()
                return
            project_json_fp = os.path.abspath(os.path.join(self.selection(), ".spinetoolbox", "project.json"))
            if not os.path.isfile(project_json_fp):
                notification = Notification(self, "Not a valid Spine Toolbox project", width=140, height=70)
                notification.show()
                return
            # self.selection() now contains a valid Spine Toolbox project directory.
            # Add the parent directory of selected directory to qsettings
            self.update_recents(os.path.abspath(os.path.join(self.selection(), os.path.pardir)))
        super().done(r)

    def update_recents(self, entry):
        """Adds a new entry to QSettings variable that remembers the five most recent project storages.

        Args:
            entry (str): Abs. path to a directory that will be added to the combobox the next time the
            open project dialog is opened.
        """
        recents = self._toolbox.qsettings().value("appSettings/recentProjectStorages", defaultValue=None)
        if not recents:
            updated_recents = entry
        else:
            recents = str(recents)
            recents_list = recents.split("\n")
            # Add path only if it's not in the list already
            if entry not in recents_list:
                recents_list.insert(0, entry)
                if len(recents_list) > 5:
                    recents_list.pop()
            else:
                # If entry was on the list, move it as the first item
                recents_list.insert(0, recents_list.pop(recents_list.index(entry)))
            updated_recents = "\n".join(recents_list)
        # Save updated recent paths
        self._toolbox.qsettings().setValue("appSettings/recentProjectStorages", updated_recents)
        self._toolbox.qsettings().sync()  # Commit change immediately

    def remove_directory_from_recents(self, p):
        """Removes directory from the recent project storages.

        Args:
            p (str): Full path to a project directory
        """
        recents = self._toolbox.qsettings().value("appSettings/recentProjectStorages", defaultValue=None)
        if not recents:
            return
        recents = str(recents)
        recents_list = recents.split("\n")
        if p in recents_list:
            recents_list.pop(recents_list.index(p))
            # Remove it from combobox as well
            cb_index = self.ui.comboBox_current_path.findText(p)
            if cb_index == -1:
                logging.error("{0} not found in combobox")
            else:
                self.ui.comboBox_current_path.removeItem(cb_index)
        updated_recents = "\n".join(recents_list)
        # Save updated recent paths
        self._toolbox.qsettings().setValue("appSettings/recentProjectStorages", updated_recents)
        self._toolbox.qsettings().sync()  # Commit change immediately

    @Slot("QPoint")
    def show_context_menu(self, pos):
        """Shows the context menu for the QCombobox with a 'Clear history' entry.

        Args:
            pos (QPoint): Mouse position
        """
        # ind = self.ui.comboBox_current_path.indexAt(pos)
        global_pos = self.ui.comboBox_current_path.mapToGlobal(pos)
        # if not ind.isValid():
        self.combobox_context_menu = OpenProjectDialogComboBoxContextMenu(self, global_pos)
        action = self.combobox_context_menu.get_action()
        if action == "Clear history":
            self.ui.comboBox_current_path.clear()
            self._toolbox.qsettings().setValue("appSettings/recentProjectStorages", "")
            self.go_root()
        else:  # No option selected
            pass
        self.combobox_context_menu.deleteLater()
        self.combobox_context_menu = None

    def closeEvent(self, event=None):
        """Handles dialog closing.

        Args:
            event (QCloseEvent): Close event
        """
        if event:
            event.accept()


class CustomQFileSystemModel(QFileSystemModel):
    """Custom file system model."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def columnCount(self, parent=QModelIndex()):
        """Returns one."""
        return 1


class DirValidator(QValidator):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = None

    def validate(self, txt, pos):
        """Returns Invalid if input is invalid according to this
        validator's rules, Intermediate if it is likely that a
        little more editing will make the input acceptable and
        Acceptable if the input is valid.

        Args:
            txt (str): Text to validate
            pos (int): Cursor position

        Returns:
            QValidator.State: Invalid, Intermediate, or Acceptable
        """
        previous_state = self.state
        if not txt:
            self.state = QValidator.Intermediate
            if not previous_state == self.state:
                self.changed.emit()
            return self.state
        if os.path.isdir(txt):
            self.state = QValidator.Acceptable
            if not previous_state == self.state:
                self.changed.emit()
            return self.state
        else:
            self.state = QValidator.Intermediate
            if not previous_state == self.state:
                self.changed.emit()
            return self.state