# -*- coding: utf-8 -*-
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

# Form implementation generated from reading ui file '/home/manuelma/Codes/spine/toolbox/bin/../spinetoolbox/ui/tabular_view_form.ui',
# licensing of '/home/manuelma/Codes/spine/toolbox/bin/../spinetoolbox/ui/tabular_view_form.ui' applies.
#
# Created: Tue Dec  3 21:48:39 2019
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1077, 774)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.GroupedDragging)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1077, 28))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuSession = QtWidgets.QMenu(self.menubar)
        self.menuSession.setObjectName("menuSession")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuDock_Widgets = QtWidgets.QMenu(self.menuView)
        self.menuDock_Widgets.setObjectName("menuDock_Widgets")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = NotificationStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_frozen_table = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget_frozen_table.sizePolicy().hasHeightForWidth())
        self.dockWidget_frozen_table.setSizePolicy(sizePolicy)
        self.dockWidget_frozen_table.setObjectName("dockWidget_frozen_table")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frozen_table = FrozenTableView(self.dockWidgetContents)
        self.frozen_table.setObjectName("frozen_table")
        self.verticalLayout.addWidget(self.frozen_table)
        self.dockWidget_frozen_table.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_frozen_table)
        self.dockWidget_pivot_table = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget_pivot_table.sizePolicy().hasHeightForWidth())
        self.dockWidget_pivot_table.setSizePolicy(sizePolicy)
        self.dockWidget_pivot_table.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_pivot_table.setObjectName("dockWidget_pivot_table")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.pivot_table = PivotTableView(self.dockWidgetContents_2)
        self.pivot_table.setObjectName("pivot_table")
        self.verticalLayout_5.addWidget(self.pivot_table)
        self.dockWidget_pivot_table.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_pivot_table)
        self.dockWidget_entity_class_list = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_entity_class_list.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_entity_class_list.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidget_entity_class_list.setObjectName("dockWidget_entity_class_list")
        self.dockWidgetContents_6 = QtWidgets.QWidget()
        self.dockWidgetContents_6.setObjectName("dockWidgetContents_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.entity_class_list = QtWidgets.QListWidget(self.dockWidgetContents_6)
        self.entity_class_list.setObjectName("entity_class_list")
        self.verticalLayout_4.addWidget(self.entity_class_list)
        self.dockWidget_entity_class_list.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget_entity_class_list)
        self.actionCommit = QtWidgets.QAction(MainWindow)
        self.actionCommit.setEnabled(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/menu_icons/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCommit.setIcon(icon)
        self.actionCommit.setObjectName("actionCommit")
        self.actionRollback = QtWidgets.QAction(MainWindow)
        self.actionRollback.setEnabled(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/menu_icons/undo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRollback.setIcon(icon1)
        self.actionRollback.setObjectName("actionRollback")
        self.actionClose = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/menu_icons/window-close.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClose.setIcon(icon2)
        self.actionClose.setObjectName("actionClose")
        self.actionAdd_object_classes = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/menu_icons/cube_plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_object_classes.setIcon(icon3)
        self.actionAdd_object_classes.setObjectName("actionAdd_object_classes")
        self.actionAdd_objects = QtWidgets.QAction(MainWindow)
        self.actionAdd_objects.setIcon(icon3)
        self.actionAdd_objects.setObjectName("actionAdd_objects")
        self.actionAdd_relationship_classes = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/menu_icons/cubes_plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_relationship_classes.setIcon(icon4)
        self.actionAdd_relationship_classes.setObjectName("actionAdd_relationship_classes")
        self.actionAdd_relationships = QtWidgets.QAction(MainWindow)
        self.actionAdd_relationships.setIcon(icon4)
        self.actionAdd_relationships.setObjectName("actionAdd_relationships")
        self.actionImport = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/menu_icons/file-import.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImport.setIcon(icon5)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setEnabled(True)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/menu_icons/file-export.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport.setIcon(icon6)
        self.actionExport.setObjectName("actionExport")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setEnabled(True)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/menu_icons/copy.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon7)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setEnabled(True)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/menu_icons/paste.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon8)
        self.actionPaste.setObjectName("actionPaste")
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/menu_icons/sync.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon9)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionEdit_object_classes = QtWidgets.QAction(MainWindow)
        self.actionEdit_object_classes.setEnabled(True)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/menu_icons/cube_pen.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_object_classes.setIcon(icon10)
        self.actionEdit_object_classes.setObjectName("actionEdit_object_classes")
        self.actionEdit_relationship_classes = QtWidgets.QAction(MainWindow)
        self.actionEdit_relationship_classes.setEnabled(True)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/menu_icons/cubes_pen.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_relationship_classes.setIcon(icon11)
        self.actionEdit_relationship_classes.setObjectName("actionEdit_relationship_classes")
        self.actionEdit_objects = QtWidgets.QAction(MainWindow)
        self.actionEdit_objects.setEnabled(True)
        self.actionEdit_objects.setIcon(icon10)
        self.actionEdit_objects.setObjectName("actionEdit_objects")
        self.actionEdit_relationships = QtWidgets.QAction(MainWindow)
        self.actionEdit_relationships.setEnabled(True)
        self.actionEdit_relationships.setIcon(icon11)
        self.actionEdit_relationships.setObjectName("actionEdit_relationships")
        self.actionManage_parameter_tags = QtWidgets.QAction(MainWindow)
        self.actionManage_parameter_tags.setObjectName("actionManage_parameter_tags")
        self.actionRemove_selection = QtWidgets.QAction(MainWindow)
        self.actionRemove_selection.setEnabled(True)
        self.actionRemove_selection.setObjectName("actionRemove_selection")
        self.actionRestore_Dock_Widgets = QtWidgets.QAction(MainWindow)
        self.actionRestore_Dock_Widgets.setObjectName("actionRestore_Dock_Widgets")
        self.menuSession.addAction(self.actionRefresh)
        self.menuSession.addAction(self.actionCommit)
        self.menuSession.addAction(self.actionRollback)
        self.menuFile.addAction(self.actionClose)
        self.menuDock_Widgets.addSeparator()
        self.menuView.addAction(self.menuDock_Widgets.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuSession.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.menuSession.setTitle(QtWidgets.QApplication.translate("MainWindow", "Session", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.menuView.setTitle(QtWidgets.QApplication.translate("MainWindow", "View", None, -1))
        self.menuDock_Widgets.setTitle(QtWidgets.QApplication.translate("MainWindow", "Dock Widgets", None, -1))
        self.dockWidget_frozen_table.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Frozen table", None, -1))
        self.dockWidget_pivot_table.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Pivot table", None, -1))
        self.dockWidget_entity_class_list.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Entity list", None, -1))
        self.actionCommit.setText(QtWidgets.QApplication.translate("MainWindow", "Commit", None, -1))
        self.actionCommit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Return", None, -1))
        self.actionRollback.setText(QtWidgets.QApplication.translate("MainWindow", "Rollback", None, -1))
        self.actionRollback.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Backspace", None, -1))
        self.actionClose.setText(QtWidgets.QApplication.translate("MainWindow", "Close", None, -1))
        self.actionClose.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+W", None, -1))
        self.actionAdd_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_object_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_objects.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationship_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionAdd_relationships.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionImport.setText(QtWidgets.QApplication.translate("MainWindow", "Import", None, -1))
        self.actionExport.setText(QtWidgets.QApplication.translate("MainWindow", "Export", None, -1))
        self.actionCopy.setText(QtWidgets.QApplication.translate("MainWindow", "Copy", None, -1))
        self.actionCopy.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+C", None, -1))
        self.actionPaste.setText(QtWidgets.QApplication.translate("MainWindow", "Paste", None, -1))
        self.actionPaste.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+V", None, -1))
        self.actionRefresh.setText(QtWidgets.QApplication.translate("MainWindow", "Refresh", None, -1))
        self.actionRefresh.setShortcut(QtWidgets.QApplication.translate("MainWindow", "F5", None, -1))
        self.actionEdit_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit object classes", None, -1))
        self.actionEdit_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationship classes", None, -1))
        self.actionEdit_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Edit objects", None, -1))
        self.actionEdit_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationships", None, -1))
        self.actionManage_parameter_tags.setText(QtWidgets.QApplication.translate("MainWindow", "Manage parameter tags", None, -1))
        self.actionRemove_selection.setText(QtWidgets.QApplication.translate("MainWindow", "Remove selection", None, -1))
        self.actionRemove_selection.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Del", None, -1))
        self.actionRestore_Dock_Widgets.setText(QtWidgets.QApplication.translate("MainWindow", "Restore Dock Widgets", None, -1))

from spinetoolbox.widgets.frozen_table_view import FrozenTableView
from spinetoolbox.widgets.pivot_table_view import PivotTableView
from spinetoolbox.widgets.custom_qstatusbar import NotificationStatusBar
from spinetoolbox import resources_icons_rc
