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
Contains ImportErrorWidget class.

:author: P. Vennström (VTT)
:date:   1.6.2019
"""

from PySide2.QtWidgets import (
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QWidget,
)
from PySide2.QtCore import Signal


class OptionsWidget(QWidget):
    """Simple option widget to be used for simple options.
    """

    # Emitted whenever a option in the widget is changed.
    optionsChanged = Signal()

    def __init__(self, options, header="Options", parent=None):
        """Creates OptionWidget

        Arguments:
            options {Dict} -- Dict describing what options to build a widget around.

        Keyword Arguments:
            header {str} -- Title of groupbox (default: {"Options"})
            parent {[type]} -- parent of widget (default: {None})
        """
        super().__init__(parent)
        self._options = options

        # ui
        self._ui_choices = {str: QLineEdit, list: QComboBox, int: QSpinBox, bool: QCheckBox}
        self._ui_elements = {}

        # layout
        self.setLayout(QVBoxLayout())
        self._form_layout = QFormLayout()
        self._groupbox = QGroupBox(header)
        self._groupbox.setLayout(self._form_layout)
        self.layout().addWidget(self._groupbox)

        self._build_ui()
        self.set_options()

    def _build_ui(self):
        """Builds ui from specification in dict
        """
        for key, options in self._options.items():
            ui_element = self._ui_choices[options["type"]]()
            if options.get('Maximum', None) is not None:
                ui_element.setMaximum(options['Maximum'])
            if options.get('Minimum', None) is not None:
                ui_element.setMinimum(options['Minimum'])
            if options.get('MaxLength', None) is not None:
                ui_element.setMaxLength(options['MaxLength'])
            # using lambdas here beacuse i want to emit a signal without arguments
            if isinstance(ui_element, QSpinBox):
                ui_element.valueChanged.connect(lambda: self.optionsChanged.emit())
            if isinstance(ui_element, QLineEdit):
                ui_element.textChanged.connect(lambda: self.optionsChanged.emit())
            if isinstance(ui_element, QCheckBox):
                ui_element.stateChanged.connect(lambda: self.optionsChanged.emit())
            if isinstance(ui_element, QComboBox):
                ui_element.addItems([str(x) for x in options["Items"]])
                ui_element.currentIndexChanged.connect(lambda: self.optionsChanged.emit())
            self._ui_elements[key] = ui_element

            # Add to layout:
            self._form_layout.addRow(QLabel(options['label']), ui_element)

    def set_options(self, options=None, set_missing_default=True):
        """Sets state of options

        Keyword Arguments:
            options {Dict} -- Dict with option name as key and value as value (default: {None})
            set_missing_default {bool} -- Sets missing options to default if True (default: {True})
        """
        if options is None:
            options = {}
        for key, ui_element in self._ui_elements.items():
            default = None
            if set_missing_default:
                default = self._options[key]['default']
            value = options.get(key, default)
            if value is None:
                continue
            ui_element.blockSignals(True)
            if isinstance(ui_element, QSpinBox):
                ui_element.setValue(value)
            if isinstance(ui_element, QLineEdit):
                ui_element.setText(value)
            if isinstance(ui_element, QCheckBox):
                ui_element.setChecked(value)
            if isinstance(ui_element, QComboBox):
                ui_element.setCurrentText(value)
            ui_element.blockSignals(False)

    def get_options(self):
        """Returns current state of option widget

        Returns:
            [Dict] -- Dict with option name as key and value as value
        """
        options = {}
        for key, ui_element in self._ui_elements.items():
            if isinstance(ui_element, QSpinBox):
                value = int(ui_element.value())
            if isinstance(ui_element, QLineEdit):
                value = str(ui_element.text())
            if isinstance(ui_element, QCheckBox):
                value = bool(ui_element.checkState())
            if isinstance(ui_element, QComboBox):
                value = str(ui_element.currentText())
            options[key] = value
        return options
