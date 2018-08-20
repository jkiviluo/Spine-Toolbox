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
Various QDialogs to add items to Database in DataStoreForm,
and a QDialog that can be programmatically populated with many options.
Originally intended to be used within DataStoreForm

:author: Manuel Marin <manuelma@kth.se>
:date:   13.5.2018
"""

import logging
from copy import deepcopy
from PySide2.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QPlainTextEdit, QLineEdit, \
    QDialogButtonBox, QComboBox, QHeaderView, QStatusBar, QStyle
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QFont, QFontMetrics, QIcon, QPixmap
from config import STATUSBAR_SS
from models import MinimalTableModel
from widgets.combobox_delegate import ComboBoxDelegate
import ui.add_object_classes
import ui.add_objects
import ui.add_relationship_classes
import ui.add_relationships
import ui.add_parameters
import ui.add_parameter_values
import ui.edit_datapackage_primary_keys


class CustomQDialog(QDialog):
    """A dialog with options to insert and remove rows from a tableview."""
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = None
        self.model = MinimalTableModel(self)
        self.model.can_grow = True
        self.object_icon = QIcon(QPixmap(":/icons/object_icon.png"))
        self.relationship_icon = QIcon(QPixmap(":/icons/relationship_icon.png"))
        self.icon_width = qApp.style().pixelMetric(QStyle.PM_ListViewIconSize)
        self.font_metric = QFontMetrics(QFont("", 0))
        self.setAttribute(Qt.WA_DeleteOnClose)

    def setup_ui(self, ui_dialog):
        self.ui = ui_dialog
        self.ui.setupUi(self)
        self.ui.toolButton_insert_row.setDefaultAction(self.ui.actionInsert_row)
        self.ui.toolButton_remove_row.setDefaultAction(self.ui.actionRemove_row)
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.actionInsert_row.triggered.connect(self.insert_row)
        self.ui.actionRemove_row.triggered.connect(self.remove_row)

    def resize_tableview(self):
        table_width = self.font_metric.width('9999') + qApp.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        for j in range(self.ui.tableView.horizontalHeader().count()):
            table_width += self.ui.tableView.columnWidth(j)
        self.ui.tableView.setMinimumWidth(table_width)

    @Slot(name="insert_row")
    def insert_row(self, row=False):
        if row is False:
            row = self.ui.tableView.currentIndex().row()+1
        self.model.insertRows(row, 1)

    @Slot(name="remove_row")
    def remove_row(self):
        current_row = self.ui.tableView.currentIndex().row()
        self.ui.tableView.setCurrentIndex(self.model.index(-1, -1))
        self.model.removeRows(current_row, 1)


class AddObjectClassesDialog(CustomQDialog):
    """A dialog to query user's preferences for new object classes."""
    def __init__(self, parent, mapping):
        super().__init__(parent)
        self.object_class_list = mapping.object_class_list()
        self.object_class_args_list = list()
        self.setup_ui(ui.add_object_classes.Ui_Dialog())
        self.model.header = ['name', 'description']
        self.model.clear()
        # Add items to combobox
        insert_position_list = ['Insert new classes at the top']
        insert_position_list.extend(["Insert new classes after '{}'".format(i.name) for i in self.object_class_list])
        self.ui.comboBox.addItems(insert_position_list)
        self.connect_signals()
        self.insert_row()
        self.resize_tableview()

    def resize_tableview(self):
        self.ui.tableView.horizontalHeader().resizeSection(0, 200)  # name
        self.ui.tableView.horizontalHeader().resizeSection(1, 300)  # description
        super().resize_tableview()

    @Slot("QWidget", name="data_commited")
    def data_commited(self, editor):
        self.model.setData(editor.index, editor.text(), Qt.EditRole)

    def accept(self):
        index = self.ui.comboBox.currentIndex()
        if index == 0:
            display_order = self.object_class_list.first().display_order-1
        else:
            display_order = self.object_class_list.all()[index-1].display_order
        for i in range(self.model.rowCount()):
            name, description = self.model.rowData(i)
            if not name:
                continue
            object_class_args = {
                'name': name,
                'description': description,
                'display_order': display_order
            }
            self.object_class_args_list.append(object_class_args)
        super().accept()


class AddObjectsDialog(CustomQDialog):
    """A dialog to query user's preferences for new objects."""
    def __init__(self, parent, mapping, class_id=None):
        super().__init__(parent)
        self.object_args_list = list()
        self.object_class_list = mapping.object_class_list()
        self.object_class_name_list = [item.name for item in self.object_class_list]
        default_class = mapping.single_object_class(id=class_id).one_or_none()
        self.default_class_name = default_class.name if default_class else None
        self.object_icon = QIcon(QPixmap(":/icons/object_icon.png"))
        self.model.header = ['class', 'name', 'description']
        self.setup_ui(ui.add_objects.Ui_Dialog())
        self.ui.tableView.setItemDelegateForColumn(0, ComboBoxDelegate(self))
        self.connect_signals()
        self.insert_row()
        self.resize_tableview()

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.tableView.itemDelegateForColumn(0).closeEditor.connect(self.class_data_commited)
        self.model.rowsInserted.connect(self.setup_new_row)
        super().connect_signals()

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        object_class_width = max([self.font_metric.width(x.name) for x in self.object_class_list], default=0)
        class_width = max(object_class_width, header.sectionSize(0))
        header.resizeSection(0, self.icon_width + class_width)
        header.resizeSection(1, 200)
        header.resizeSection(2, 300)
        super().resize_tableview()

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        if self.default_class_name:
            self.model.setData(self.model.index(first, 0, parent), self.default_class_name)
            self.model.setData(self.model.index(first, 0, parent), self.object_icon, Qt.DecorationRole)

    @Slot("QWidget", name='class_data_commited')
    def class_data_commited(self, editor):
        """Update 'class' field with data from combobox editor."""
        class_name = editor.currentText()
        if not class_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, class_name, Qt.EditRole)
        self.model.setData(index, self.object_icon, Qt.DecorationRole)

    def accept(self):
        for i in range(self.model.rowCount()):
            class_name, name, description = self.model.rowData(i)
            if not class_name or not name:
                continue
            class_id = self.object_class_list.filter_by(name=class_name).one().id
            object_args = {
                'class_id': class_id,
                'name': name,
                'description': description
            }
            self.object_args_list.append(object_args)
        super().accept()


class AddRelationshipClassesDialog(CustomQDialog):
    """A dialog to query user's preferences for new relationship classes."""
    def __init__(self, parent, mapping, object_class_one_id=None):
        super().__init__(parent)
        self.wide_relationship_class_args_list = list()
        self.mapping = mapping
        self.number_of_dimensions = 2
        self.object_class_name_list = [item.name for item in mapping.object_class_list()]
        self.object_class_one_name = None
        if object_class_one_id:
            object_class_one = mapping.single_object_class(id=object_class_one_id).one_or_none()
            if object_class_one:
                self.object_class_one_name = object_class_one.name
        self.model.header = ['object class 1', 'object class 2', 'name']
        self.setup_ui(ui.add_relationship_classes.Ui_Dialog())
        self.ui.tableView.setItemDelegateForColumn(0, ComboBoxDelegate(self))
        self.ui.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(self))
        self.connect_signals()
        self.insert_row()
        self.resize_tableview()

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.tableView.itemDelegateForColumn(0).closeEditor.connect(self.object_class_data_commited)
        self.ui.tableView.itemDelegateForColumn(1).closeEditor.connect(self.object_class_data_commited)
        self.ui.spinBox.valueChanged.connect(self.insert_or_remove_column)
        self.model.rowsInserted.connect(self.setup_new_row)
        super().connect_signals()

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        object_class_width = max([self.font_metric.width(x) for x in self.object_class_name_list], default=0)
        for column in range(self.number_of_dimensions):
            header.resizeSection(column, self.icon_width + object_class_width)
            header.resizeSection(column, self.icon_width + object_class_width)
        name_width = max(self.number_of_dimensions * object_class_width, header.sectionSize(self.number_of_dimensions))
        header.resizeSection(self.number_of_dimensions, name_width)

    @Slot("int", name="insert_or_remove_column")
    def insert_or_remove_column(self, i):
        self.ui.spinBox.setEnabled(False)
        if i > self.number_of_dimensions:
            self.insert_column()
        elif i < self.number_of_dimensions:
            self.remove_column()
        self.ui.spinBox.setEnabled(True)
        # TODO: resizing
        for row in range(self.model.rowCount()):
            self.compose_relationship_class_name(row)

    def insert_column(self):
        column = self.number_of_dimensions
        self.number_of_dimensions += 1
        self.model.header.insert(column, "object class {}".format(self.number_of_dimensions))
        self.model.insertColumns(column, 1)
        for row in range(self.model.rowCount()):
            self.model.setData(self.model.index(row, column), self.object_class_name_list, Qt.UserRole)
        self.ui.tableView.setItemDelegateForColumn(column, ComboBoxDelegate(self))
        self.ui.tableView.itemDelegateForColumn(column).closeEditor.connect(self.object_class_data_commited)

    def remove_column(self):
        self.number_of_dimensions -= 1
        column = self.number_of_dimensions
        self.ui.tableView.itemDelegateForColumn(column).closeEditor.disconnect(self.object_class_data_commited)
        self.model.header.pop(column)
        self.model.removeColumns(column, 1)
        line_delegate = self.ui.tableView.itemDelegate()
        self.ui.tableView.setItemDelegateForColumn(column, line_delegate)

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        if self.object_class_one_name:
            self.model.setData(self.model.index(first, 0), self.object_class_one_name)
            self.model.setData(self.model.index(first, 0), self.object_icon, Qt.DecorationRole)
        for column in range(self.model.columnCount()-1):  # Leave 'name' column out
            self.model.setData(self.model.index(first, column), self.object_class_name_list, Qt.UserRole)
            self.model.setData(self.model.index(first, column), self.object_class_name_list, Qt.UserRole)

    @Slot("QWidget", name='object_class_data_commited')
    def object_class_data_commited(self, editor):
        """Update 'object_classx' field with data from combobox editor."""
        object_class_name = editor.currentText()
        if not object_class_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, object_class_name, Qt.EditRole)
        self.model.setData(index, self.object_icon, Qt.DecorationRole)
        self.compose_relationship_class_name(row)

    def compose_relationship_class_name(self, row):
        """Compose relationship class name automatically."""
        object_class_name_list = list()
        name_column = self.model.columnCount() - 1
        for column in range(name_column):  # Leave 'name' column outside
            index = self.model.index(row, column)
            object_class_name = self.model.data(index, Qt.DisplayRole)
            if object_class_name:
                object_class_name_list.append(object_class_name)
        relationship_class_name = "_".join(object_class_name_list)
        self.model.setData(index.sibling(row, name_column), relationship_class_name, Qt.EditRole)

    def accept(self):
        name_column = self.model.columnCount() - 1
        for i in range(self.model.rowCount()):
            row = self.model.rowData(i)
            relationship_class_name = row[name_column]
            if not relationship_class_name:
                continue
            object_class_id_list = list()
            for column in range(name_column):  # Leave 'name' column outside
                object_class_name = row[column]
                if not object_class_name:
                    continue
                object_class = self.mapping.single_object_class(name=object_class_name).one_or_none()
                if not object_class:
                    continue
                object_class_id_list.append(object_class.id)
            if len(object_class_id_list) < 2:
                continue
            wide_relationship_class_args = {
                'name': relationship_class_name,
                'object_class_id_list': object_class_id_list
            }
            self.wide_relationship_class_args_list.append(wide_relationship_class_args)
        super().accept()


class AddRelationshipsDialog(CustomQDialog):
    """A dialog to query user's preferences for new relationships."""
    def __init__(self, parent, mapping, relationship_class_id=None, object_id=None, object_class_id=None):
        super().__init__(parent)
        self.wide_relationship_args_list = list()
        self.mapping = mapping
        self.relationship_class_id = relationship_class_id
        self.default_object_column = None
        self.default_object_name = None
        self.default_combo_index = -1
        self.object_class_id_list = None
        self.object_names_list = None
        wide_relationship_class_list = mapping.wide_relationship_class_list(object_class_id=object_class_id)
        self.relationship_class_name_list = [x.name for x in wide_relationship_class_list]
        self.relationship_class_id_list = [x.id for x in wide_relationship_class_list]
        self.set_defaults(object_id, object_class_id)
        self.setup_ui(ui.add_relationships.Ui_Dialog())
        self.ui.toolButton_insert_row.setEnabled(False)
        self.ui.toolButton_remove_row.setEnabled(False)
        self.ui.comboBox_relationship_class.addItems(self.relationship_class_name_list)
        self.ui.comboBox_relationship_class.setCurrentIndex(self.default_combo_index)
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        self.connect_signals()
        self.reset_model()

    def set_defaults(self, object_id, object_class_id):
        """Set input relationship class in combobox, and store
        default object name and column for when adding rows.
        """
        if not self.relationship_class_id:
            return
        relationship_class = self.mapping.single_wide_relationship_class(id=self.relationship_class_id).\
            one_or_none()
        if not relationship_class:
            logging.debug("Couldn't find relationship class, probably a bug.")
            return
        relationship_class_name = relationship_class.name
        self.default_combo_index = self.relationship_class_name_list.index(relationship_class_name)
        if object_id is None or object_class_id is None:
            return
        object_ = self.mapping.single_object(id=object_id).one_or_none()
        if not object_:
            return
        try:
            object_class_id_list = relationship_class.object_class_id_list
            self.default_object_column = [int(x) for x in object_class_id_list.split(',')].index(object_class_id)
        except ValueError:
            return
        self.default_object_name = object_.name

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.comboBox_relationship_class.currentIndexChanged.connect(self.call_reset_model)
        self.model.rowsInserted.connect(self.setup_new_row)
        super().connect_signals()

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        font_metric = QFontMetrics(QFont("", 0))
        icon_width = qApp.style().pixelMetric(QStyle.PM_ListViewIconSize)
        name_width = 0
        for section, object_class_id in enumerate(self.object_class_id_list):
            object_list = self.mapping.object_list(class_id=object_class_id)
            object_width = max([font_metric.width(x.name) for x in object_list], default=0)
            section_width = max(icon_width + object_width, header.sectionSize(section))
            header.resizeSection(section, section_width)
            name_width += object_width
        section = header.count()-1
        section_width = max(name_width, header.sectionSize(section))
        header.resizeSection(section, section_width)
        super().resize_tableview()

    @Slot("int", name='call_reset_model')
    def call_reset_model(self, index):
        self.relationship_class_id = self.relationship_class_id_list[index]
        self.reset_model()

    def reset_model(self):
        """Setup model according to current relationship class selected in combobox
        (or given as input).
        """
        if not self.relationship_class_id:
            return
        wide_relationship_class = self.mapping.single_wide_relationship_class(self.relationship_class_id).one_or_none()
        if not wide_relationship_class:
            logging.debug("Couldn't find relationship class, probably a bug.")
            return
        object_class_id_list = wide_relationship_class.object_class_id_list
        self.object_class_id_list = [int(x) for x in object_class_id_list.split(',')]
        header = list()
        self.object_names_list = list()
        for object_class_id in self.object_class_id_list:
            object_class = self.mapping.single_object_class(id=object_class_id).one_or_none()
            if not object_class:
                logging.debug("Couldn't find object class, probably a bug.")
                return
            header.append(object_class.name)
            object_list = self.mapping.object_list(class_id=object_class_id)
            object_names = [x.name for x in object_list]
            if not object_names:
                msg = "There are no objects of class '{}'.".format(object_class.name)
                self.statusbar.showMessage(msg, 5000)
                return
            self.object_names_list.append(object_names)
        for column in range(len(header)):
            self.ui.tableView.setItemDelegateForColumn(column, ComboBoxDelegate(self))
            self.ui.tableView.itemDelegateForColumn(column).closeEditor.connect(self.data_commited)
        header.append('name')
        self.model.header = header
        self.model.clear()
        self.insert_row()
        self.resize_tableview()
        self.ui.toolButton_insert_row.setEnabled(True)
        self.ui.toolButton_remove_row.setEnabled(True)

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        for column, object_names in enumerate(self.object_names_list):
            index = self.model.index(first, column)
            self.model.setData(index, object_names, Qt.UserRole)
            self.model.setData(index, self.object_icon, Qt.DecorationRole)
        if self.default_object_name and self.default_object_column is not None:
            index = self.model.index(first, self.default_object_column)
            self.model.setData(index, self.default_object_name, Qt.EditRole)

    @Slot("QWidget", name='data_commited')
    def data_commited(self, editor):
        """Update 'object x' field with data from combobox editor."""
        name = editor.currentText()
        if not name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, name, Qt.EditRole)
        self.compose_relationship_name(row)

    def compose_relationship_name(self, row):
        """Compose relationship name automatically."""
        object_name_list = list()
        name_column = self.model.columnCount() - 1
        for column in range(name_column):  # Leave 'name' column outside
            index = self.model.index(row, column)
            object_name = self.model.data(index, Qt.DisplayRole)
            if object_name:
                object_name_list.append(object_name)
        relationship_name = "_".join(object_name_list)
        self.model.setData(index.sibling(row, name_column), relationship_name, Qt.EditRole)

    def accept(self):
        name_column = self.model.columnCount() - 1
        for i in range(self.model.rowCount()):
            row = self.model.rowData(i)
            relationship_name = row[name_column]
            if not relationship_name:
                continue
            object_id_list = list()
            for column in range(name_column):  # Leave 'name' column outside
                object_name = row[column]
                if not object_name:
                    continue
                object_ = self.mapping.single_object(name=object_name).one_or_none()
                if not object_:
                    continue
                object_id_list.append(object_.id)
            if len(object_id_list) < 2:
                continue
            wide_relationship_args = {
                'name': relationship_name,
                'object_id_list': object_id_list,
                'class_id': self.relationship_class_id
            }
            self.wide_relationship_args_list.append(wide_relationship_args)
        super().accept()


class AddParametersDialog(CustomQDialog):
    """A dialog to query user's preferences for new parameters."""
    def __init__(self, parent, mapping, object_class_id=None, relationship_class_id=None):
        super().__init__(parent)
        self.parameter_args_list = list()
        self.mapping = mapping
        self.class_name_list = [item.name for item in self.mapping.object_class_list()]
        self.class_name_list.extend([item.name for item in self.mapping.wide_relationship_class_list()])
        self.default_class_name = None
        self.default_class_icon = None
        self.set_defaults(object_class_id, relationship_class_id)
        self.model.header = ['class', 'name']
        self.setup_ui(ui.add_parameters.Ui_Dialog())
        self.ui.tableView.setItemDelegateForColumn(0, ComboBoxDelegate(self))
        self.connect_signals()
        self.insert_row()
        self.resize_tableview()

    def set_defaults(self, object_class_id, relationship_class_id):
        """Set defaults names to put in every new row."""
        if object_class_id:
            object_class = self.mapping.single_object_class(id=object_class_id).one_or_none()
            if object_class:
                self.default_class_name = object_class.name
                self.default_class_icon = self.object_icon
        elif relationship_class_id:
            wide_relationship_class = self.mapping.single_wide_relationship_class(id=relationship_class_id).\
                one_or_none()
            if wide_relationship_class:
                self.default_class_name = wide_relationship_class.name
                self.default_class_icon = self.relationship_icon

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.tableView.itemDelegateForColumn(0).closeEditor.connect(self.class_data_commited)
        self.model.rowsInserted.connect(self.setup_new_row)
        super().connect_signals()

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        object_class_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.object_class_list()], default=0)
        relationship_class_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.wide_relationship_class_list()], default=0)
        class_width = max(object_class_width, relationship_class_width, header.sectionSize(0))
        header.resizeSection(0, self.icon_width + class_width)
        header.resizeSection(1, 200)  # name
        super().resize_tableview()

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        if self.default_class_name:
            self.model.setData(self.model.index(first, 0), self.default_class_name)
            self.model.setData(self.model.index(first, 0), self.default_class_icon, Qt.DecorationRole)
        self.model.setData(self.model.index(first, 0), self.class_name_list, Qt.UserRole)

    @Slot("QWidget", name='class_data_commited')
    def class_data_commited(self, editor):
        """Update 'class' field with data from combobox editor."""
        class_name = editor.currentText()
        if not class_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, class_name, Qt.EditRole)
        object_class = self.mapping.single_object_class(name=class_name).one_or_none()
        if object_class:
            class_icon = self.object_icon
        else:
            class_icon = self.relationship_icon
        self.model.setData(index, class_icon, Qt.DecorationRole)

    def accept(self):
        for i in range(self.model.rowCount()):
            row = self.model.rowData(i)
            if any([True for i in row if not i]):
                continue
            class_name, name = row
            object_class = self.mapping.single_object_class(name=class_name).one_or_none()
            relationship_class = self.mapping.single_wide_relationship_class(name=class_name).one_or_none()
            if object_class is None and relationship_class is None:
                continue
            object_class_id = object_class.id if object_class else None
            relationship_class_id = relationship_class.id if relationship_class else None
            parameter_args = {
                'object_class_id': object_class_id,
                'relationship_class_id': relationship_class_id,
                'name': name
            }
            self.parameter_args_list.append(parameter_args)
        super().accept()


class AddParameterValuesDialog(CustomQDialog):
    """A dialog to query user's preferences for new parameter values."""
    def __init__(self, parent, mapping, object_class_id=None, relationship_class_id=None,
            object_id=None, relationship_id=None
        ):
        super().__init__(parent)
        self.mapping = mapping
        self.parameter_value_args_list = list()
        self.class_name_list = [item.name for item in self.mapping.object_class_list()]
        self.class_name_list.extend([item.name for item in self.mapping.wide_relationship_class_list()])
        self.default_class_name = None
        self.default_entity_name = None
        self.set_defaults(object_class_id, relationship_class_id, object_id, relationship_id)
        self.model.header = ['class', 'entity', 'parameter', 'value', 'json']
        self.setup_ui(ui.add_parameter_values.Ui_Dialog())
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        # Override tableView edit slot
        self.std_edit = self.ui.tableView.edit
        self.ui.tableView.edit = self.edit
        self.ui.tableView.setItemDelegateForColumn(0, ComboBoxDelegate(self))
        self.ui.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(self))
        self.ui.tableView.setItemDelegateForColumn(2, ComboBoxDelegate(self))
        self.connect_signals()
        self.insert_row()
        self.resize_tableview()

    def set_defaults(self, object_class_id, relationship_class_id, object_id, relationship_id):
        """Set default names to put in a new row."""
        if object_class_id:
            object_class = self.mapping.single_object_class(id=object_class_id).one_or_none()
            if object_class:
                self.default_class_name = object_class.name
                self.default_class_icon = self.object_icon
        elif relationship_class_id:
            relationship_class = self.mapping.single_wide_relationship_class(id=relationship_class_id).one_or_none()
            if relationship_class:
                self.default_class_name = relationship_class.name
                self.default_class_icon = self.relationship_icon
        if object_id:
            object_ = self.mapping.single_object(id=object_id).one_or_none()
            if object_:
                self.default_entity_name = object_.name
                self.default_entity_icon = self.object_icon
        elif relationship_id:
            relationship = self.mapping.single_wide_relationship(id=relationship_id).one_or_none()
            if relationship:
                self.default_entity_name = relationship.name
                self.default_entity_icon = self.relationship_icon

    def edit(self, index, trigger, event):
        """Check that first columns are set before editing nexts."""
        if not index.isValid():
            return False
        column = index.column()
        header = self.model.header
        if header[column] == 'entity' and index.data(Qt.UserRole) is None:
            self.statusbar.showMessage("Please select class first.", 5000)
            return False
        if header[column] == 'parameter' and index.data(Qt.UserRole) is None:
            self.statusbar.showMessage("Please select class and entity first.", 5000)
            return False
        return self.std_edit(index, trigger, event)

    def connect_signals(self):
        """Connect signals to slots."""
        self.model.rowsInserted.connect(self.setup_new_row)
        self.ui.tableView.itemDelegateForColumn(0).closeEditor.connect(self.class_data_commited)
        self.ui.tableView.itemDelegateForColumn(1).closeEditor.connect(self.entity_data_commited)
        self.ui.tableView.itemDelegateForColumn(2).closeEditor.connect(self.parameter_data_commited)
        super().connect_signals()

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        object_class_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.object_class_list()], default=0)
        relationship_class_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.wide_relationship_class_list()], default=0)
        object_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.object_list()], default=0)
        relationship_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.wide_relationship_list()], default=0)
        parameter_width = max(
            [self.font_metric.width(x.name) for x in self.mapping.parameter_list()], default=0)
        class_width = max(object_class_width, relationship_class_width, header.sectionSize(0))
        entity_width = max(object_width, relationship_width, header.sectionSize(1))
        parameter_width = max(parameter_width, header.sectionSize(2))
        header.resizeSection(0, self.icon_width + class_width)
        header.resizeSection(1, self.icon_width + entity_width)
        header.resizeSection(2, self.icon_width + parameter_width)
        header.resizeSection(3, 80)  # value
        header.resizeSection(4, 80)  # json
        super().resize_tableview()

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        if self.default_class_name:
            self.model.setData(self.model.index(first, 0), self.default_class_name)
            self.model.setData(self.model.index(first, 0), self.default_class_icon, Qt.DecorationRole)
            self.update_entity_combo(self.default_class_name, first)
        if self.default_entity_name:
            self.model.setData(self.model.index(first, 1), self.default_entity_name)
            self.model.setData(self.model.index(first, 1), self.default_entity_icon, Qt.DecorationRole)
            self.update_parameter_combo(self.default_entity_name, first)
        self.model.setData(self.model.index(first, 0), self.class_name_list, Qt.UserRole)

    @Slot("QWidget", name='class_data_commited')
    def class_data_commited(self, editor):
        """Update 'class' field with data from combobox editor
        and update comboboxes for 'entity' field accordingly.
        """
        class_name = editor.currentText()
        if not class_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, class_name, Qt.EditRole)
        object_class = self.mapping.single_object_class(name=class_name).one_or_none()
        if object_class:
            class_icon = self.object_icon
        else:
            class_icon = self.relationship_icon
        self.model.setData(index, class_icon, Qt.DecorationRole)
        self.model.setData(index.sibling(row, 1), None, Qt.EditRole)
        self.model.setData(index.sibling(row, 1), None, Qt.DecorationRole)
        self.model.setData(index.sibling(row, 2), None, Qt.EditRole)
        self.update_entity_combo(class_name, row)

    def update_entity_combo(self, name, row):
        """Update options available in combobox for entity.

        Args:
            name (str): The name of a class.
            row (int): The row in the model.
        """
        msg = self.statusbar.currentMessage()
        object_class = self.mapping.single_object_class(name=name).one_or_none()
        relationship_class = self.mapping.single_wide_relationship_class(name=name).one_or_none()
        if object_class:
            entity_name_list = [i.name for i in self.mapping.object_list(class_id=object_class.id)]
            if not entity_name_list:
                msg += "Class '{}' does not have any objects. ".format(name)
                self.model.setData(self.model.index(row, 1), None, Qt.EditRole)
        elif relationship_class:
            entity_name_list = [i.name for i in self.mapping.wide_relationship_list(class_id=relationship_class.id)]
            if not entity_name_list:
                msg += "Class '{}' does not have any relationships. ".format(name)
                self.model.setData(self.model.index(row, 1), None, Qt.EditRole)
        else:
            logging.debug("Couldn't find class '{}'. This is probably a bug.".format(name))
            return
        self.model.setData(self.model.index(row, 1), entity_name_list, Qt.UserRole)
        self.statusbar.showMessage(msg, 5000)

    @Slot("QWidget", name='entity_data_commited')
    def entity_data_commited(self, editor):
        """Update 'entity' field with data from combobox editor."""
        entity_name = editor.currentText()
        if not entity_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, entity_name, Qt.EditRole)
        object_ = self.mapping.single_object(name=entity_name).one_or_none()
        if object_:
            entity_icon = self.object_icon
        else:
            entity_icon = self.relationship_icon
        self.model.setData(index, entity_icon, Qt.DecorationRole)
        self.update_parameter_combo(entity_name, row)

    def update_parameter_combo(self, entity_name, row):
        """Update options available in combobox for entity.

        Args:
            entity_name (str): The name of an entity.
            row (int): The row in the model.
        """
        msg = self.statusbar.currentMessage()
        object_ = self.mapping.single_object(name=entity_name).one_or_none()
        relationship = self.mapping.single_wide_relationship(name=entity_name).one_or_none()
        if object_:
            parameter_list = self.mapping.unvalued_object_parameter_list(object_.id)
            parameter_name_list = [i.name for i in parameter_list]
            # TODO: remove from the list the ones already picked in this form.
        elif relationship:
            parameter_list = self.mapping.unvalued_relationship_parameter_list(relationship.id)
            parameter_name_list = [i.name for i in parameter_list]
        else:
            logging.debug("Couldn't find entity '{}'. This is probably a bug.".format(entity_name))
            return
        if not parameter_name_list:
            msg += "All parameters for '{}' already have a value. ".format(entity_name)
            self.model.setData(self.model.index(row, 2), None, Qt.EditRole)
        self.model.setData(self.model.index(row, 2), parameter_name_list, Qt.UserRole)
        self.statusbar.showMessage(msg, 5000)

    @Slot("QWidget", name='parameter_data_commited')
    def parameter_data_commited(self, editor):
        """Update 'parameter' field with data from combobox editor."""
        parameter_name = editor.currentText()
        if not parameter_name:
            return
        row = editor.row
        column = editor.column
        index = self.model.index(row, column)
        self.model.setData(index, parameter_name, Qt.EditRole)

    def accept(self):
        for i in range(self.model.rowCount()):
            class_name, entity_name, parameter_name, value, json = self.model.rowData(i)
            if not entity_name or not parameter_name:
                continue
            if not value and not json:
                continue
            object_ = self.mapping.single_object(name=entity_name).one_or_none()
            relationship = self.mapping.single_wide_relationship(name=entity_name).one_or_none()
            if object_ is None and relationship is None:
                continue
            parameter = self.mapping.single_parameter(name=parameter_name).one_or_none()
            if not parameter:
                continue
            object_id = object_.id if object_ else None
            relationship_id = relationship.id if relationship else None
            parameter_id = parameter.id
            parameter_value_args = {
                'object_id': object_id,
                'relationship_id': relationship_id,
                'parameter_id': parameter_id,
                'value': value,
                'json': json
            }
            self.parameter_value_args_list.append(parameter_value_args)
        super().accept()


class CommitDialog(QDialog):
    """A dialog to query user's preferences for new parameter values."""
    def __init__(self, parent, database):
        """Initialize class

        Args:
            parent (QWidget): the parent of this dialog, needed to center it properly.
            database (str): The database name.
        """
        super().__init__(parent)
        self.commit_msg = None
        self.setWindowTitle('Commit changes to {}'.format(database))
        form = QVBoxLayout(self)
        form.setContentsMargins(0, 0, 0, 0)
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(4, 4, 4, 4)
        self.commit_msg_edit = QPlainTextEdit(self)
        self.commit_msg_edit.setPlaceholderText('Commit message')
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box = QDialogButtonBox()
        button_box.addButton(QDialogButtonBox.Cancel)
        button_box.addButton('Commit', QDialogButtonBox.AcceptRole)
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        inner_layout.addWidget(self.commit_msg_edit)
        inner_layout.addWidget(button_box)
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        form.addLayout(inner_layout)
        form.addWidget(self.statusbar)
        self.setAttribute(Qt.WA_DeleteOnClose)

    @Slot(name="save_and_accept")
    def save_and_accept(self):
        """Check if everything is ok and accept"""
        self.commit_msg = self.commit_msg_edit.toPlainText()
        if not self.commit_msg:
            self.statusbar.showMessage("Please enter a commit message.", 3000)
            return
        self.accept()


class EditDatapackagePrimaryKeysDialog(CustomQDialog):
    """A dialog to query user's preferences for new objects."""
    def __init__(self, parent, datapackage):
        super().__init__(parent)
        self.datapackage = datapackage
        self.resource_name_list = self.datapackage.resource_names
        self.keys_to_set = list()
        self.keys_to_remove = list()
        data = self.datapackage.primary_keys_data()
        self.original_data = deepcopy(data)
        self.setup_ui(ui.edit_datapackage_primary_keys.Ui_Dialog())
        self.ui.tableView.setItemDelegateForColumn(0, ComboBoxDelegate(self))
        self.ui.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(self))
        # Override tableView edit slot
        self.std_edit = self.ui.tableView.edit
        self.ui.tableView.edit = self.edit
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        self.resize_tableview()
        self.connect_signals()
        self.init_model(data)

    def edit(self, index, trigger, event):
        if not index.isValid():
            return False
        column = index.column()
        header = self.model.header
        if header[column] == 'field' and index.data(Qt.UserRole) is None:
            self.statusbar.showMessage("Please select resource first.", 5000)
            return False
        return self.std_edit(index, trigger, event)

    def connect_signals(self):
        """Connect signals to slots."""
        self.model.rowsInserted.connect(self.setup_new_row)
        self.ui.tableView.itemDelegateForColumn(0).closeEditor.connect(self.resource_data_commited)
        self.ui.tableView.itemDelegateForColumn(1).closeEditor.connect(self.field_data_commited)
        super().connect_signals()

    def init_model(self, data):
        """Init model with primary keys data."""
        self.model.header = ['resource', 'field']
        self.model.reset_model(data)
        for i, row in enumerate(data):
            resource = row[0]
            field_name_list = self.datapackage.get_resource(resource).schema.field_names
            self.model.setData(self.model.index(i, 0), self.resource_name_list, Qt.UserRole)
            self.model.setData(self.model.index(i, 1), field_name_list, Qt.UserRole)
        self.insert_row(row=self.model.rowCount())

    def resize_tableview(self):
        self.ui.tableView.resizeColumnsToContents()
        header = self.ui.tableView.horizontalHeader()
        resource_width = max([self.font_metric.width(x) for x in self.resource_name_list], default=0)
        resource_width = max(resource_width, header.sectionSize(0))
        header.resizeSection(0, resource_width)
        # Field with is whatever needs to be (last column stretched)
        super().resize_tableview()

    @Slot(name="setup_new_row")
    def setup_new_row(self, parent, first, last):
        self.model.setData(self.model.index(first, 0), self.resource_name_list, Qt.UserRole)
        self.model.setData(self.model.index(first, 1), None, Qt.UserRole)

    @Slot("QWidget", name='resource_data_commited')
    def resource_data_commited(self, editor):
        """Update 'resource' field with data from combobox editor"""
        current_resource = editor.currentText()
        if not current_resource:
            return
        row = editor.row
        index = self.model.index(row, 0)
        previous_resource = self.model.data(index, Qt.DisplayRole)
        if current_resource == previous_resource:
            return
        self.model.setData(index, current_resource, Qt.EditRole)
        field_index = index.sibling(row, 1)
        field_name_list = self.datapackage.get_resource(current_resource).schema.field_names
        self.model.setData(field_index, field_name_list[0], Qt.EditRole)
        self.model.setData(field_index, field_name_list, Qt.UserRole)
        self.ui.tableView.update(field_index)

    @Slot("QWidget", name='field_data_commited')
    def field_data_commited(self, editor):
        """Update 'field' field with data from combobox editor"""
        current_field = editor.currentText()
        if not current_field:
            return
        row = editor.row
        index = self.model.index(row, 1)
        previous_field = self.model.data(index, Qt.DisplayRole)
        if current_field == previous_field:
            return
        self.model.setData(index, current_field)

    def accept(self):
        new_data = self.model.modelData()
        for row in new_data:
            if None in row:
                continue
            if row not in self.original_data:
                self.keys_to_set.append(row)
        for row in self.original_data:
            if None in row:
                continue
            if row not in new_data:
                self.keys_to_remove.append(row)
        super().accept()

# NOTE: Not in use anymore, too general
# class CustomQDialog(QDialog):
#     """A class to create custom forms with several line edits and comboboxes."""
#     def __init__(self, parent=None, title="", **kwargs):
#         """Initialize class
#
#         Args:
#             parent (QWidget): the parent of this dialog, needed to center it properly
#             title (str): window title
#             kwargs (dict): keys to use when collecting the answer in output dict.
#                 Values are either placeholder texts or combobox lists.
#         """
#         super().__init__(parent)
#         self.font = QFont("", 0)
#         self.font_metric = QFontMetrics(self.font)
#         self.input = dict()
#         self.answer = dict()
#         self.setWindowTitle(title)
#         form = QFormLayout(self)
#         for key,value in kwargs.items():
#             if isinstance(value, str): # line edit
#                 input_ = QLineEdit(self)
#                 input_.setPlaceholderText(value)
#                 input_.setMinimumWidth(self.font_metric.width(value))
#             elif isinstance(value, list): # combo box
#                 input_ = QComboBox(self)
#                 max_width = max(self.font_metric.width(x) for x in value if isinstance(x, str))
#                 input_.setMinimumWidth(max_width)
#                 input_.addItems(value)
#             self.input[key] = input_
#             form.addRow(input_)
#         button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         button_box.accepted.connect(self.save_and_accept)
#         button_box.rejected.connect(self.reject)
#         form.addRow(button_box)
#         # Ensure this window gets garbage-collected when closed
#         self.setAttribute(Qt.WA_DeleteOnClose)
#
#     @Slot(name="save_and_accept")
#     def save_and_accept(self):
#         """Collect answer in output dict and accept"""
#         for key,value in self.input.items():
#             if isinstance(value, QLineEdit):
#                 self.answer[key] = value.text()
#             elif isinstance(value, QComboBox):
#                 self.answer[key] = {
#                     'text': value.currentText(),
#                     'index': value.currentIndex()
#                 }
#         self.accept()
#
