#############################################################################
# Copyright (C) 2016 - 2017 VTT Technical Research Centre of Finland
#
# This file is part of Spine Toolbox.
#
# Spine Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

"""
Module for main application GUI functions.

:author: Pekka Savolainen <pekka.t.savolainen@vtt.fi>
:date:   14.12.2017
"""

import os
import locale
import logging
import json
import datetime
from PySide2.QtCore import Qt, Signal, Slot, QSettings
from PySide2.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QCheckBox, QAction
from PySide2.QtGui import QStandardItemModel, QStandardItem
from ui.mainwindow import Ui_MainWindow
from widgets.data_store_widget import DataStoreWidget
from widgets.about_widget import AboutWidget
from widgets.context_menus import ProjectItemContextMenu
from widgets.project_form_widget import NewProjectForm
from widgets.settings_widget import SettingsWidget
from widgets.add_data_store_widget import AddDataStoreWidget
from widgets.add_data_connection_widget import AddDataConnectionWidget
from widgets.add_tool_widget import AddToolWidget
from widgets.add_view_widget import AddViewWidget
import widgets.toolbars
from data_store import DataStore
from data_connection import DataConnection
from tool import Tool
from view import View
from project import SpineToolboxProject
from configuration import ConfigurationParser
from config import SPINE_TOOLBOX_VERSION, CONFIGURATION_FILE, SETTINGS, STATUSBAR_SS, EVENTLOG_SS
from helpers import project_dir, get_datetime


class ToolboxUI(QMainWindow):
    """Class for application main GUI functions."""

    # Custom signals
    msg = Signal(str, name="msg")
    msg_success = Signal(str, name="msg_success")
    msg_error = Signal(str, name="msg_error")
    msg_warning = Signal(str, name="msg_warning")

    def __init__(self):
        """ Initialize application and main window."""
        super().__init__(flags=Qt.Window)
        # Set number formatting to use user's default settings
        locale.setlocale(locale.LC_NUMERIC, '')
        # Setup the user interface from Qt Designer files
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.qsettings = QSettings("SpineProject", "Spine Toolbox")
        # Class variables
        self._config = None
        self._project = None
        self.project_item_model = self.init_models()
        self.ui.treeView_project.setModel(self.project_item_model)
        # Widget and form references
        self.settings_form = None
        self.about_form = None
        self.data_store_form = None
        self.project_item_context_menu = None
        self.project_form = None
        self.add_data_store_form = None
        self.add_data_connection_form = None
        self.add_tool_form = None
        self.add_view_form = None
        self.project_refs = list()  # TODO: Find out why these are needed in addition with project_item_model
        # Initialize application
        self.ui.statusbar.setStyleSheet(STATUSBAR_SS)  # Initialize QStatusBar
        self.ui.statusbar.setFixedHeight(20)
        self.ui.textBrowser_eventlog.setStyleSheet(EVENTLOG_SS)
        # Make and initialize toolbars
        self.item_toolbar = widgets.toolbars.make_item_toolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.item_toolbar)
        # Make keyboard shortcuts
        self.test1_action = QAction(self)
        self.test1_action.setShortcut("F5")
        self.addAction(self.test1_action)
        self.test2_action = QAction(self)
        self.test2_action.setShortcut("F6")
        self.addAction(self.test2_action)
        self.init_conf()  # Load settings to memory
        self.set_debug_level(level=self._config.get("settings", "logging_level"))
        self.connect_signals()
        self.init_project()
        self.restore_ui()

    def init_conf(self):
        """Load settings from configuration file."""
        self._config = ConfigurationParser(CONFIGURATION_FILE, defaults=SETTINGS)
        self._config.load()

    # noinspection PyMethodMayBeStatic
    def set_debug_level(self, level):
        """Control application debug message verbosity.

        Args:
            level (str): '0': Error messages only, '2': All messages
        """
        if level == '2':
            logging.getLogger().setLevel(level=logging.DEBUG)
            logging.debug("Logging level: All messages")
        else:
            logging.debug("Logging level: Error messages only")
            logging.getLogger().setLevel(level=logging.ERROR)

    def connect_signals(self):
        """Connect signals."""
        # Event log signals
        self.msg.connect(self.add_message)
        self.msg_success.connect(self.add_success_message)
        self.msg_error.connect(self.add_error_message)
        self.msg_warning.connect(self.add_warning_message)
        # Menu commands
        self.ui.actionNew.triggered.connect(self.new_project)
        self.ui.actionOpen.triggered.connect(self.open_project)
        self.ui.actionSave.triggered.connect(self.save_project)
        self.ui.actionSave_As.triggered.connect(self.save_project_as)
        self.ui.actionSettings.triggered.connect(self.show_settings)
        self.ui.actionQuit.triggered.connect(self.closeEvent)
        self.ui.actionData_Store.triggered.connect(self.open_data_store_view)
        self.ui.actionAdd_Data_Store.triggered.connect(self.add_data_store)
        self.ui.actionAdd_Data_Connection.triggered.connect(self.add_data_connection)
        self.ui.actionAdd_Tool.triggered.connect(self.add_tool)
        self.ui.actionAdd_View.triggered.connect(self.add_view)
        self.ui.actionAdd_Item_Toolbar.triggered.connect(lambda: self.item_toolbar.show())
        self.ui.actionEvent_Log.triggered.connect(lambda: self.ui.dockWidget_eventlog.show())
        self.ui.actionAbout.triggered.connect(self.show_about)
        # Keyboard shortcut actions
        self.test1_action.triggered.connect(self.test1)
        self.test2_action.triggered.connect(self.test2)
        # QMdiArea
        self.ui.mdiArea.subWindowActivated.connect(self.update_details_frame)
        # Project TreeView
        self.ui.treeView_project.clicked.connect(self.activate_subwindow)
        self.ui.treeView_project.doubleClicked.connect(self.show_subwindow)
        self.ui.treeView_project.customContextMenuRequested.connect(self.show_item_context_menu)

    @Slot(name="init_project")
    def init_project(self):
        """Initializes project at application start-up. Loads the last project that was open
        when app was closed or starts without a project if app is started for the first time.
        """
        if not self._config.getboolean("settings", "open_previous_project"):
            return
        # Get path to previous project file from configuration file
        project_file_path = self._config.get("settings", "previous_project")
        if not project_file_path:
            return
        if not os.path.isfile(project_file_path):
            msg = "Could not load previous project. File '{0}' not found.".format(project_file_path)
            self.ui.statusbar.showMessage(msg, 10000)
            return
        if not self.open_project(project_file_path):
            self.msg_error.emit("Loading project file <b>{0}</b> failed".format(project_file_path))
            logging.error("Loading project file '{0}' failed".format(project_file_path))
        return

    def restore_ui(self):
        """Restore UI state from previous session."""
        window_size = self.qsettings.value("mainWindow/windowSize")
        window_pos = self.qsettings.value("mainWindow/windowPosition")
        window_state = self.qsettings.value("mainWindow/windowState")
        window_maximized = self.qsettings.value("mainWindow/windowMaximized", defaultValue='false')  # returns string
        if window_size:
            self.resize(window_size)
        if window_pos:
            self.move(window_pos)
        if window_state:
            self.restoreState(window_state, version=1)  # Toolbar and dockWidget positions
        if window_maximized == 'true':
            self.setWindowState(Qt.WindowMaximized)

    # noinspection PyMethodMayBeStatic
    def init_models(self):
        """Initialize data model for project contents."""
        m = QStandardItemModel()
        m.setHorizontalHeaderItem(0, QStandardItem("Contents"))
        m.appendRow(QStandardItem("Data Stores"))
        m.appendRow(QStandardItem("Data Connections"))
        m.appendRow(QStandardItem("Tools"))
        m.appendRow(QStandardItem("Views"))
        return m

    def clear_ui(self):
        """Clean UI to make room for a new or opened project."""
        subwindows = self.ui.mdiArea.subWindowList()
        n = len(subwindows)
        if n == 0:
            return
        for subwindow in subwindows:
            self.remove_sw(subwindow)
        self.msg.emit("All {0} items removed from project".format(n))

    @Slot(name="new_project")
    def new_project(self):
        """Create new project and activate it."""
        self.project_form = NewProjectForm(self, self._config)
        self.project_form.show()

    def create_project(self, name, description):
        """Create new project and set it active.

        Args:
            name (str): Project name
            description (str): Project description
        """
        self.clear_ui()
        self._project = None
        self._project = SpineToolboxProject(self, name, description, self._config, ext='.proj')
        self.setWindowTitle("Spine Toolbox    -- {} --".format(self._project.name))
        self.ui.textBrowser_eventlog.clear()
        self.msg.emit("New project created")
        self.save_project()

    @Slot(name="open_project")
    def open_project(self, load_path=None):
        """Load project from a save file (.proj) file.

        Args:
            load_path (str): If not None, this method is used to load the
            previously opened project at start-up
        """
        if not load_path:
            # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
            answer = QFileDialog.getOpenFileName(self, 'Open project', project_dir(self._config),
                                                 'Projects (*.proj)')
            load_path = answer[0]
            if load_path == '':  # Cancel button clicked
                return False
        if not os.path.isfile(load_path):
            self.msg_error.emit("File <b>{0}</b> not found".format(load_path))
            logging.debug("File not found: {0}".format(load_path))
            return False
        if not load_path.lower().endswith('.proj'):
            logging.debug("File name has unsupported extension. Only .proj files supported")
            return False
        # Load project from JSON file
        try:
            with open(load_path, 'r') as fh:
                dicts = json.load(fh)
        except OSError:
            logging.exception("Could not load project from file {0}".format(load_path))
            return False
        # Initialize UI
        self.clear_ui()
        # Parse project info
        project_dict = dicts['project']
        proj_name = project_dict['name']
        proj_desc = project_dict['description']
        # Create project
        self._project = SpineToolboxProject(self, proj_name, proj_desc, self._config)
        # Setup models and views
        self.setWindowTitle("Spine Toolbox    -- {} --".format(self._project.name))
        # self.msg.emit("Loading project {0}".format(self._project.name))
        # Populate project model with items read from JSON file
        if not self._project.load(dicts['objects']):
            self.msg_error.emit("Loading project items failed")
            logging.error("Loading project items failed")
            self.project_item_model = self.init_models()
            return False
        self.ui.treeView_project.expandAll()
        self.msg.emit("Project <b>{0}</b> is now open".format(self._project.name))
        return True

    @Slot(name="save_project")
    def save_project(self):
        """Save project."""
        if not self._project:
            self.msg.emit("No project open")
            return
        self._project.save()
        self.msg.emit("Project saved to <b>{0}</b>".format(self._project.path))

    @Slot(name="save_project_as")
    def save_project_as(self):
        """Save current project on a new name and activate it."""
        # noinspection PyCallByClass
        dir_path = QFileDialog.getSaveFileName(self, 'Save project', project_dir(self._config),
                                               'Project (*.proj)')
        file_path = dir_path[0]
        if file_path == '':  # Cancel button clicked
            return
        file_name = os.path.split(file_path)[-1]
        if not file_name.lower().endswith('.proj'):
            self.msg_warning.emit("Only *.proj files supported")
            logging.debug("Only *.proj files supported")
            return
        if not self._project:
            self.new_project()
        else:
            # Update project file name
            self._project.change_filename(file_name)
            # TODO: Make a new project with the given name and switch references of all items for the new project.
            # Save open project into new file
            self.save_project()
        return

    @Slot("QModelIndex", name="activate_subwindow")
    def activate_subwindow(self, index):
        """Set focus on selected subwindow.

        Args:
            index (QModelIndex): Index of clicked item, if available
        """
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        else:
            if index.parent().isValid():
                item = self.project_item_model.itemFromIndex(index)
                item_data = item.data(Qt.UserRole)  # This is e.g. DataStore object
                item_widget = item_data.get_widget()
                item_subwindow = item_widget.parent()  # QMdiSubWindow that has item_widget as its internal widget
                self.ui.mdiArea.setActiveSubWindow(item_subwindow)
            return

    @Slot("QModelIndex", name="show_subwindow")
    def show_subwindow(self, index):
        """Show double-clicked item subwindow if it was hidden.
        Sets both QMdiSubWindow and its internal widget visible.

        Args:
            index (QModelIndex): Index of clicked item, if available
        """
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        else:
            if index.parent().isValid():
                item_data = self.project_item_model.itemFromIndex(index).data(Qt.UserRole)  # e.g. DataStore object
                internal_widget = item_data.get_widget()  # QWidget of e.g. DataStore object
                subwindow = internal_widget.parent()  # QMdiSubWindow that has internal_widget as its widget
                subwindow.show()
                internal_widget.show()
            return

    @Slot(name="open_data_store_view")
    def open_data_store_view(self):
        self.data_store_form = DataStoreWidget(self)
        self.data_store_form.show()

    @Slot(name="test1")
    def test1(self):
        sub_windows = self.ui.mdiArea.subWindowList()
        self.msg.emit("Number of subwindows: {0}".format(len(sub_windows)))
        top_level_items = self.project_item_model.findItems('*', Qt.MatchWildcard, column=0)
        for top_level_item in top_level_items:
            # logging.debug("Children of {0}".format(top_level_item.data(Qt.DisplayRole)))
            if top_level_item.hasChildren():
                n_children = top_level_item.rowCount()
                for i in range(n_children):
                    child = top_level_item.child(i, 0)
                    self.msg.emit("{0}".format(child.data(Qt.DisplayRole)))

    @Slot(name="test2")
    def test2(self):
        n = len(self.project_refs)
        self.msg.emit("Items in ref list: {0}".format(n))
        current_sub_window = self.ui.mdiArea.currentSubWindow()
        if not current_sub_window:
            return
        owner_name = current_sub_window.widget().owner()
        par = current_sub_window.widget().parent()
        self.msg.emit("Parent of {0} is {1}".format(owner_name, par))

    @Slot("QMdiSubWindow", name="update_details_frame")
    def update_details_frame(self, window):
        """Update labels on main window according to the currently selected QMdiSubWindow.

        Args:
            window (QMdiSubWindow): Active sub-window
        """
        if window is not None:
            w = window.widget()  # SubWindowWidget
            obj_type = w.objectName()
            name = w.owner()
            self.ui.lineEdit_type.setText(obj_type)
            self.ui.lineEdit_name.setText(name)
            # Find object data from model. Note: Finds child items only if Qt.MatchRecursive is set.
            selected_item = self.find_item(name, Qt.MatchExactly | Qt.MatchRecursive)
            if not selected_item:
                logging.error("Item {0} not found".format(name))
                return
            matching_item_data = selected_item.data(Qt.UserRole)  # TODO: Fix this warning
            self.ui.lineEdit_data.setText(str(matching_item_data.get_data()))
        else:
            self.ui.lineEdit_type.setText("")
            self.ui.lineEdit_name.setText("")
            self.ui.lineEdit_data.setText("")
            self.ui.lineEdit_test.setText("")

    def add_data_store(self, name, description):
        """Make a QMdiSubwindow, add data store widget to it, and add subwindow to QMdiArea."""
        if not self._project:
            self.msg.emit("No project open")
            return
        data_store = DataStore(name, description, self._project)
        # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
        sw = self.ui.mdiArea.addSubWindow(data_store.get_widget(), Qt.SubWindow)
        self.project_refs.append(data_store)  # Save reference or signals don't stick
        self.add_item_to_model("Data Stores", name, data_store)
        self.msg.emit("Data Store <b>{0}</b> added to project".format(name))
        sw.show()

    def add_data_connection(self, name, description):
        """Add Data Connection as a QMdiSubwindow to QMdiArea."""
        if not self._project:
            self.msg.emit("No project open")
            return
        data_connection = DataConnection(name, description, self._project)
        # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
        sw = self.ui.mdiArea.addSubWindow(data_connection.get_widget(), Qt.SubWindow)
        self.project_refs.append(data_connection)  # Save reference or signals don't stick
        self.add_item_to_model("Data Connections", name, data_connection)
        self.msg.emit("Data Connection <b>{0}</b> added to project".format(name))
        sw.show()

    def add_tool(self, name, description):
        """Add Tool as a QMdiSubwindow to QMdiArea."""
        if not self._project:
            logging.debug("No project open")
            return
        tool = Tool(name, description, self._project)
        # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
        sw = self.ui.mdiArea.addSubWindow(tool.get_widget(), Qt.SubWindow)
        self.project_refs.append(tool)  # Save reference or signals don't stick
        self.add_item_to_model("Tools", name, tool)
        self.msg.emit("Tool <b>{0}</b> added to project".format(name))
        sw.show()

    def add_view(self, name, description):
        """Add View as a QMdiSubwindow to QMdiArea."""
        if not self._project:
            logging.debug("No project open")
            return
        view = View(name, description, self._project)
        # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
        sw = self.ui.mdiArea.addSubWindow(view.get_widget(), Qt.SubWindow)
        self.project_refs.append(view)  # Save reference or signals don't stick
        self.add_item_to_model("Views", name, view)
        self.msg.emit("View <b>{0}</b> added to project".format(name))
        sw.show()

    def add_item_to_model(self, category, text, data):
        """Add item to project model.

        Args:
            category (str): Project category (e.g. Data Stores)
            text (str): Display role for the new item
            data (QObject): Object that is added to model (e.g. DataStore())
        """
        # First, find QStandardItem category item where new child item is added
        found_items = self.project_item_model.findItems(category, Qt.MatchExactly, column=0)
        if not found_items:
            logging.error("'{0}' item not found in project item model".format(category))
            return False
        if len(found_items) > 1:
            logging.error("More than one '{0}' items found in project item model".format(category))
            return False
        item_index = found_items[0].index()
        parent_index = item_index.parent()
        if not parent_index.isValid():
            # Parent index is not valid if item has no parent
            new_item = QStandardItem(text)
            new_item.setData(data, role=Qt.UserRole)
            self.project_item_model.itemFromIndex(item_index).appendRow(new_item)
            self.ui.treeView_project.expand(item_index)
        return True

    def remove_item(self, ind):
        """Remove subwindow from project when it's index in the project model is known.

        Args:
            ind (QModelIndex): Index of removed item in project model
        """
        sw = ind.data(Qt.UserRole).get_widget().parent()
        self.remove_sw(sw)

    def remove_sw(self, sw):
        """Remove sub-window and its internal widget from project. To remove all items in project,
        loop all sub-windows through this method.

        Args:
            sw (QMdiSubWindow): Subwindow to remove.
        """
        widget = sw.widget()  # SubWindowWidget
        name = widget.owner()
        # Delete QMdiSubWindow
        self.ui.mdiArea.removeSubWindow(sw)  # QMdiSubWindow
        self.ui.mdiArea.removeSubWindow(widget)  # SubWindowWidget
        # Find item in project model
        item = self.find_item(name, Qt.MatchExactly | Qt.MatchRecursive)  # QStandardItem
        item_data = item.data(Qt.UserRole)  # Object that is contained in the QStandardItem (e.g. DataStore)
        ind = self.project_item_model.indexFromItem(item)
        # Remove item from project model
        if not self.project_item_model.removeRow(ind.row(), ind.parent()):
            self.msg_error.emit("Failed to remove item <b>{0}</b>".format(item.name))
            logging.error("Failed to remove item: {0}".format(item.name))
        # Remove item data from reference list
        try:
            self.project_refs.remove(item_data)  # Note: remove() removes only the first occurrence in the list
        except ValueError:
            self.msg_error.emit("Item '{0}' not found in reference list".format(item_data))
            logging.error("Item '{0}' not found in reference list".format(item_data))
            return
        self.msg.emit("Item <b>{0}</b> removed from project".format(name))
        return

    def find_item(self, name, match_flags=Qt.MatchExactly):
        """Find item by name in project model (column 0)

        Args:
            name (str): Item name to find
            match_flags (QFlags): Or combination of Qt.MatchFlag types

        Returns:
            Matching QStandardItem or None if item not found or more than one item with the same name found.
        """
        found_items = self.project_item_model.findItems(name, match_flags, column=0)
        if len(found_items) == 0:
            # logging.debug("Item '{0}' not found in project model".format(name))
            return None
        if len(found_items) > 1:
            logging.error("More than one item with name '{0}' found".format(name))
            return None
        return found_items[0]

    @Slot(str, name="add_message")
    def add_message(self, msg):
        """Append regular message to Event Log.

        Args:
            msg (str): String written to QTextBrowser
        """
        open_tag = "<span style='color:white;white-space: pre-wrap;'>"
        date_str = get_datetime(self._config)
        message = open_tag + date_str + msg + "</span>"
        self.ui.textBrowser_eventlog.append(message)
        # noinspection PyArgumentList
        QApplication.processEvents()

    @Slot(str, name="add_success_message")
    def add_success_message(self, msg):
        """Append message with green text color to Event Log.

        Args:
            msg (str): String written to QTextBrowser
        """
        open_tag = "<span style='color:#00ff00;white-space: pre-wrap;'>"
        date_str = get_datetime(self._config)
        message = open_tag + date_str + msg + "</span>"
        self.ui.textBrowser_eventlog.append(message)
        # noinspection PyArgumentList
        QApplication.processEvents()

    @Slot(str, name="add_error_message")
    def add_error_message(self, msg):
        """Append message with red color to Event Log.

        Args:
            msg (str): String written to QTextBrowser
        """
        open_tag = "<span style='color:#ff3333;white-space: pre-wrap;'>"
        date_str = get_datetime(self._config)
        message = open_tag + date_str + msg + "</span>"
        self.ui.textBrowser_eventlog.append(message)
        # noinspection PyArgumentList
        QApplication.processEvents()

    @Slot(str, name="add_warning_message")
    def add_warning_message(self, msg):
        """Append message with yellow (golden) color to Event Log.

        Args:
            msg (str): String written to QTextBrowser
        """
        open_tag = "<span style='color:yellow;white-space: pre-wrap;'>"
        date_str = get_datetime(self._config)
        message = open_tag + date_str + msg + "</span>"
        self.ui.textBrowser_eventlog.append(message)
        # noinspection PyArgumentList
        QApplication.processEvents()

    @Slot(name="show_add_data_store_form")
    def show_add_data_store_form(self):
        """Show add data store widget."""
        if not self._project:
            logging.debug("Create a project first")
            return
        self.add_data_store_form = AddDataStoreWidget(self)
        self.add_data_store_form.show()

    @Slot(name="show_add_data_connection_form")
    def show_add_data_connection_form(self):
        """Show add data connection widget."""
        if not self._project:
            logging.debug("Create a project first")
            return
        self.add_data_connection_form = AddDataConnectionWidget(self)
        self.add_data_connection_form.show()

    @Slot(name="show_add_tool_form")
    def show_add_tool_form(self):
        """Show add tool widget."""
        if not self._project:
            logging.debug("Create a project first")
            return
        self.add_tool_form = AddToolWidget(self)
        self.add_tool_form.show()

    @Slot(name="show_add_view_form")
    def show_add_view_form(self):
        """Show add view widget."""
        if not self._project:
            logging.debug("Create a project first")
            return
        self.add_view_form = AddViewWidget(self)
        self.add_view_form.show()

    @Slot(name="show_settings")
    def show_settings(self):
        """Show Settings widget."""
        self.settings_form = SettingsWidget(self, self._config, self._project)
        self.settings_form.show()

    @Slot(name="show_about")
    def show_about(self):
        """Show About Spine Toolbox form."""
        self.about_form = AboutWidget(self, SPINE_TOOLBOX_VERSION)
        self.about_form.show()

    @Slot("QPoint", name="show_item_context_menu")
    def show_item_context_menu(self, pos):
        """Context menu for project items.

        Args:
            pos (QPoint): Mouse position
        """
        ind = self.ui.treeView_project.indexAt(pos)
        global_pos = self.ui.treeView_project.viewport().mapToGlobal(pos)
        self.project_item_context_menu = ProjectItemContextMenu(self, global_pos, ind)
        option = self.project_item_context_menu.get_action()
        if option == "Remove":
            self.remove_item(ind)
            return
        else:
            # No option selected
            pass
        self.project_item_context_menu.deleteLater()
        self.project_item_context_menu = None

    def show_confirm_exit(self):
        """Shows confirm exit message box.

        Returns:
            True if user clicks Yes or False if exit is cancelled
        """
        ex = self._config.getboolean("settings", "show_exit_prompt")
        if ex:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Confirm exit")
            msg.setText("Are you sure you want to exit Spine Toolbox?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            chkbox = QCheckBox()
            chkbox.setText("Do not ask me again")
            msg.setCheckBox(chkbox)
            answer = msg.exec_()  # Show message box
            if answer == QMessageBox.Yes:
                # Update conf file according to checkbox status
                if not chkbox.checkState():
                    show_prompt = True
                else:
                    show_prompt = False
                self._config.setboolean("settings", "show_exit_prompt", show_prompt)
                return True
            else:
                return False
        return True

    def closeEvent(self, event=None):
        """Method for handling application exit.

        Args:
             event (QEvent): PySide2 event
        """
        # Show confirm exit message box
        if not self.show_confirm_exit():
            # Exit cancelled
            if event:
                event.ignore()
            return
        logging.debug("Bye bye")
        # Save current project (if enabled in settings)
        if not self._project:
            self._config.set("settings", "previous_project", "")
        else:
            self._config.set("settings", "previous_project", self._project.path)
        self._config.save()
        self.qsettings.setValue("mainWindow/windowSize", self.size())
        self.qsettings.setValue("mainWindow/windowPosition", self.pos())
        self.qsettings.setValue("mainWindow/windowState", self.saveState(version=1))
        if self.windowState() == Qt.WindowMaximized:
            self.qsettings.setValue("mainWindow/windowMaximized", True)
        else:
            self.qsettings.setValue("mainWindow/windowMaximized", False)
        if event:
            event.accept()
        # noinspection PyArgumentList
        QApplication.quit()
