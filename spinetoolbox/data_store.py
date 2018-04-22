#############################################################################
# Copyright (C) 2017 - 2018 VTT Technical Research Centre of Finland
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
Module for data store class.

:author: Pekka Savolainen <pekka.t.savolainen@vtt.fi>
:date:   18.12.2017
"""

import os
import shutil
import pyodbc
import logging
from PySide2.QtGui import QStandardItemModel, QStandardItem
from metaobject import MetaObject
from widgets.data_store_subwindow_widget import DataStoreWidget
from helpers import create_dir, custom_getopenfilenames
from PySide2.QtCore import Qt, Slot
from widgets.add_connection_string_widget import AddConnectionStringWidget
from widgets.Spine_data_explorer_widget import SpineDataExplorerWidget

class DataStore(MetaObject):
    """Data Store class.

    Attributes:
        parent (ToolboxUI): QMainWindow instance
        name (str): Object name
        description (str): Object description
        project (SpineToolboxProject): Project
        references (list): List of references (for now it's only database references)
    """
    def __init__(self, parent, name, description, project, references):
        super().__init__(name, description)
        self._parent = parent
        self.item_type = "Data Store"
        self.item_category = "Data Stores"
        self._project = project
        self._widget = DataStoreWidget(name, self.item_type)
        self._widget.set_name_label(name)
        self._widget.make_header_for_references()
        self._widget.make_header_for_data()
        # Make directory for Data Store
        self.references = references
        self.databases = list() # name of imported databases
        self.Spine_data_model = QStandardItemModel()
        self.Spine_data_model.setHorizontalHeaderItem(0, QStandardItem(name))
        # Populate references model
        self._widget.populate_reference_list(self.references)
        #set connections buttons slot type
        self._widget.ui.toolButton_connector.is_connector = True
        self.add_connection_string_form = None
        self.Spine_data_explorer_form = None
        self.connect_signals()

    def connect_signals(self):
        """Connect this data store's signals to slots."""
        self._widget.ui.pushButton_open.clicked.connect(self.open_explorer)
        self._widget.ui.toolButton_plus.clicked.connect(self.show_add_connection_string_form)
        self._widget.ui.toolButton_minus.clicked.connect(self.remove_references)
        self._widget.ui.toolButton_add.clicked.connect(self.import_into_project)
        self._widget.ui.pushButton_connections.clicked.connect(self.show_connections)
        self._widget.ui.toolButton_connector.clicked.connect(self.draw_links)

    @Slot(name="draw_links")
    def draw_links(self):
        self._parent.ui.graphicsView.draw_links(self._widget.ui.toolButton_connector)

    @Slot(name="open_explorer")
    def open_explorer(self):
        """Open Spine data explorer."""
        self.Spine_data_explorer_form = SpineDataExplorerWidget(self._parent, self)
        self.Spine_data_explorer_form.showMaximized()

    @Slot(name="add_references")
    def show_add_connection_string_form(self):
        """Show the form for specifying connection strings."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        self.add_connection_string_form = AddConnectionStringWidget(self._parent, self)
        self.add_connection_string_form.show()

    @Slot(name="remove_references")
    def remove_references(self):
        """Remove selected references from reference list.
        Removes all references if nothing is selected.
        """
        indexes = self._widget.ui.treeView_references.selectedIndexes()
        if not indexes:  # Nothing selected
            self.references.clear()
            self._parent.msg.emit("All references removed")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.references.pop(row)
            self._parent.msg.emit("Selected references removed")
        self._widget.populate_reference_list(self.references)

    @Slot(name="import_into_project")
    def import_into_project(self):
        """Import data from selected items in reference list and update database list.
        If no item is selected then import all of them.
        """
        if not self.references:
            self._parent.msg_warning.emit("No data to import")
            return
        indexes = self._widget.ui.treeView_references.selectedIndexes()
        if not indexes:  # Nothing selected
            references_to_import = self.references
        else:
            references_to_import = [self.references[ind.row()] for ind in indexes]
        self._parent.msg.emit("Importing data")
        for connection_string in references_to_import:
            try:
                cnxn = pyodbc.connect(connection_string, autocommit=True, timeout=3)
            except pyodbc.Error as e:
                self._parent.msg_error.emit("[pyodbc.Error] Connection failed ({0})".format(e))
                continue
            try:
                database_name = self.import_database(cnxn)
            except pyodbc.Error as e:
                self._parent.msg_error.emit("[pyodbc.Error] Import failed ({0})".format(e))
                continue
            self.databases.append(database_name)
        self._widget.populate_data_list(self.databases)

    def import_database(self, cnxn):
        """Import database from a ODBC connection reference into Spine data model.
        Args:
            cnxn (pyodbc.Connection): The connection to read data from
        """
        database_name = cnxn.getinfo(pyodbc.SQL_DATABASE_NAME)
        # Make sure that we don't overwrite existing data
        new_database_name = database_name
        k = len(self.Spine_data_model.findItems(database_name, Qt.MatchStartsWith))
        if k > 0:
            new_database_name += "_" + str(k-1)
        self._parent.msg.emit("Importing database <b>{0}</b>".format(new_database_name))
        # Create database item
        database_item = QStandardItem(new_database_name)
        # Create container for parameter names
        parameter_names = list()
        for row in cnxn.cursor().execute("""
            select COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS
            where TABLE_NAME = 'parameters'
            and TABLE_SCHEMA = ?
        """, database_name):
            parameter_names.append(row.COLUMN_NAME)
        # Store parameter names in item's UserRole
        database_item.setData(parameter_names, Qt.UserRole)
        for row in cnxn.cursor().execute("select * from object_classes"):
            # Create object class item
            object_class_item = QStandardItem(row.object_class_id)
            for row2 in cnxn.cursor().execute("""
                select * from objects where object_class_id = ?
            """, row.object_class_id):
                # Create object item
                object_item = QStandardItem(row2.object_id)
                # Create parameter container
                parameter_data = ParameterContainer()
                # Query object parameters
                for row3 in cnxn.cursor().execute("""
                    select pd.parameter_entity_class_id, p.*
                    from parameters as p
                    join parameter_definition as pd
                    on p.parameter_id = pd.parameter_id
                    where pd.parameter_entity_class_id = ?
                    and p.entity_id = ?
                """, [row.object_class_id, row2.object_id]):
                    parameter_data.object.append(row3)
                # Query relationship parameters
                for row3 in cnxn.cursor().execute("""
                    select rc.relationship_class_id, r.parent_object_id, r.child_object_id, p.*
                    from parameters as p
                    join relationships as r
                    on p.entity_id = r.relationship_id
                    join relationship_classes as rc
                    on r.relationship_class_id = rc.relationship_class_id
                    where rc.parent_class_id = ?
                    and r.parent_object_id = ?
                """, [row.object_class_id, row2.object_id]):
                    parameter_data.relationship.append(row3)
                # Store parameter data in item's UserRole
                object_item.setData(parameter_data, Qt.UserRole)
                # Attach object to object class
                object_class_item.appendRow(object_item)
            # Attach object class to database
            database_item.appendRow(object_class_item)
        self.Spine_data_model.appendRow(database_item)
        return database_name

    @Slot(name="show_connections")
    def show_connections(self):
        """Show connections of this item."""
        inputs = self._parent.connection_model.input_items(self.name)
        outputs = self._parent.connection_model.output_items(self.name)
        self._parent.msg.emit("<br/><b>{0}</b>".format(self.name))
        self._parent.msg.emit("Input items")
        if not inputs:
            self._parent.msg_warning.emit("None")
        else:
            for item in inputs:
                self._parent.msg_warning.emit("{0}".format(item))
        self._parent.msg.emit("Output items")
        if not outputs:
            self._parent.msg_warning.emit("None")
        else:
            for item in outputs:
                self._parent.msg_warning.emit("{0}".format(item))

    def add_reference(self, reference):
        """Add reference to reference list and populate widget's reference list"""
        self.references.append(reference)
        self._widget.populate_reference_list(self.references)

    def data_references(self):
        """Return a list of paths to files and databases that are in this item as references (self.references)."""
        return self.references

    def get_widget(self):
        """Returns the graphical representation (QWidget) of this object."""
        return self._widget

class ParameterContainer:
    """A class to store parameter data for a Spine object or relationship,
    to use it as model for table views in SpineDataExplorerWidgets.

    """
    def __init__(self):
        self.object = list()
        self.relationship = list()
