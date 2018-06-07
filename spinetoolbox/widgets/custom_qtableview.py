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
Class for a custom QTableView for the Data store form.

:author: Manuel Marin <manuelma@kth.se>
:date:   18.5.2018
"""

import logging
from PySide2.QtWidgets import QTableView, QApplication
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QKeySequence

class ParameterValueTableView(QTableView):
    """Custom QTableView class.

    Attributes:
        parent (QWidget): The parent of this view
    """

    def __init__(self, parent):
        """Initialize the QGraphicsView."""
        super().__init__(parent)
        self.adding_new_parameter_value = False

    def edit(self, proxy_index, trigger=QTableView.AllEditTriggers, event=None):
        """Starts editing the item corresponding to the given index if it is editable.
        To edit `parameter_name`, set the attribute `adding_new_parameter_value`
        before calling this method.
        """
        if not proxy_index.isValid():
            return False
        source_index = proxy_index.model().mapToSource(proxy_index)
        header = proxy_index.model().sourceModel().header
        if header[source_index.column()] == "parameter_name":
            if not self.adding_new_parameter_value:
                return False
            self.adding_new_parameter_value = False
            super().edit(proxy_index, trigger, event)
            return True
        return super().edit(proxy_index, trigger, event)

    def keyPressEvent(self, event):
        """Copy selection to clipboard so that it can be pasted into Excel"""
        if not event.matches(QKeySequence.Copy):
            event.ignore()
            return
        selection = self.selectionModel().selection()
        if not selection:
            event.ignore()
            return
        first = selection.first()
        content = ""
        v_header = self.verticalHeader()
        h_header = self.horizontalHeader()
        for i in range(first.top(), first.bottom()+1):
            if v_header.isSectionHidden(i):
                continue
            row = list()
            for j in range(first.left(), first.right()+1):
                if h_header.isSectionHidden(j):
                    continue
                row.append(str(self.model().index(i, j).data(Qt.DisplayRole)))
            content += "\t".join(row)
            content += "\n"
        QApplication.clipboard().setText(content)


class ParameterTableView(QTableView):
    """Custom QTableView class.

    Attributes:
        parent (QWidget): The parent of this view
    """

    def __init__(self, parent):
        """Initialize the QGraphicsView."""
        super().__init__(parent)

    def keyPressEvent(self, event):
        """Copy selection to clipboard so that it can be pasted into Excel"""
        if not event.matches(QKeySequence.Copy):
            event.ignore()
            return
        selection = self.selectionModel().selection()
        if not selection:
            event.ignore()
            return
        first = selection.first()
        content = ""
        v_header = self.verticalHeader()
        h_header = self.horizontalHeader()
        for i in range(first.top(), first.bottom()+1):
            if v_header.isSectionHidden(i):
                continue
            row = list()
            for j in range(first.left(), first.right()+1):
                if h_header.isSectionHidden(j):
                    continue
                row.append(str(self.model().index(i, j).data(Qt.DisplayRole)))
            content += "\t".join(row)
            content += "\n"
        QApplication.clipboard().setText(content)


class DataPackageKeyTableView(QTableView):
    """Custom QTableView class.

    Attributes:
        parent (QWidget): The parent of this view
    """

    def __init__(self, parent):
        """Initialize the QGraphicsView."""
        super().__init__(parent)
        self.setup_combo_items = None

    def edit(self, index, trigger=QTableView.AllEditTriggers, event=None):
        """Starts editing the item corresponding to the given index if it is editable.
        """
        if not index.isValid():
            return False
        column = index.column()
        header = self.model().headerData(column)
        if header == 'Select': # this column should be editable with only one click
            return super().edit(index, trigger, event)
        if not trigger & self.editTriggers():
            return False
        self.setup_combo_items(index)
        return super().edit(index, trigger, event)
