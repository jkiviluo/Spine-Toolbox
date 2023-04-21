# -*- coding: utf-8 -*-
######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

################################################################################
## Form generated from reading UI file 'spine_db_editor_window.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDockWidget, QFrame,
    QGraphicsView, QHBoxLayout, QHeaderView, QMainWindow,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from spinetoolbox.spine_db_editor.widgets.custom_qgraphicsviews import EntityQGraphicsView
from spinetoolbox.spine_db_editor.widgets.custom_qtableview import (FrozenTableView, ItemMetadataTableView, MetadataTableView, ParameterDefinitionTableView,
    ParameterValueTableView, PivotTableView)
from spinetoolbox.spine_db_editor.widgets.custom_qtreeview import (AlternativeTreeView, ScenarioTreeView, EntityTreeView, ParameterValueListTreeView, ToolFeatureTreeView)
from spinetoolbox import resources_icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(969, 1167)
        MainWindow.setLayoutDirection(Qt.LeftToRight)
        MainWindow.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.GroupedDragging)
        self.actionCommit = QAction(MainWindow)
        self.actionCommit.setObjectName(u"actionCommit")
        self.actionCommit.setEnabled(True)
        icon = QIcon()
        icon.addFile(u":/icons/menu_icons/check.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCommit.setIcon(icon)
        self.actionRollback = QAction(MainWindow)
        self.actionRollback.setObjectName(u"actionRollback")
        self.actionRollback.setEnabled(False)
        icon1 = QIcon()
        icon1.addFile(u":/icons/menu_icons/times.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRollback.setIcon(icon1)
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionClose.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(u":/icons/menu_icons/window-close.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionClose.setIcon(icon2)
        self.actionImport = QAction(MainWindow)
        self.actionImport.setObjectName(u"actionImport")
        self.actionImport.setEnabled(False)
        icon3 = QIcon()
        icon3.addFile(u":/icons/menu_icons/database-import.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionImport.setIcon(icon3)
        self.actionExport = QAction(MainWindow)
        self.actionExport.setObjectName(u"actionExport")
        self.actionExport.setEnabled(False)
        icon4 = QIcon()
        icon4.addFile(u":/icons/menu_icons/database-export.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExport.setIcon(icon4)
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        self.actionCopy.setEnabled(False)
        icon5 = QIcon()
        icon5.addFile(u":/icons/menu_icons/copy.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionCopy.setIcon(icon5)
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        self.actionPaste.setEnabled(False)
        icon6 = QIcon()
        icon6.addFile(u":/icons/menu_icons/paste.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionPaste.setIcon(icon6)
        self.actionStacked_style = QAction(MainWindow)
        self.actionStacked_style.setObjectName(u"actionStacked_style")
        self.actionStacked_style.setEnabled(True)
        icon7 = QIcon()
        icon7.addFile(u":/icons/menu_icons/table.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionStacked_style.setIcon(icon7)
        self.actionGraph_style = QAction(MainWindow)
        self.actionGraph_style.setObjectName(u"actionGraph_style")
        self.actionGraph_style.setEnabled(True)
        icon8 = QIcon()
        icon8.addFile(u":/icons/project-diagram.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionGraph_style.setIcon(icon8)
        self.actionView_history = QAction(MainWindow)
        self.actionView_history.setObjectName(u"actionView_history")
        self.actionView_history.setEnabled(True)
        icon9 = QIcon()
        icon9.addFile(u":/icons/menu_icons/history.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionView_history.setIcon(icon9)
        self.actionMass_remove_items = QAction(MainWindow)
        self.actionMass_remove_items.setObjectName(u"actionMass_remove_items")
        self.actionMass_remove_items.setEnabled(False)
        icon10 = QIcon()
        icon10.addFile(u":/icons/menu_icons/cube_minus.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionMass_remove_items.setIcon(icon10)
        self.actionExport_session = QAction(MainWindow)
        self.actionExport_session.setObjectName(u"actionExport_session")
        self.actionExport_session.setEnabled(False)
        self.actionExport_session.setIcon(icon4)
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        icon11 = QIcon()
        icon11.addFile(u":/icons/menu_icons/cog.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSettings.setIcon(icon11)
        self.actionUser_guide = QAction(MainWindow)
        self.actionUser_guide.setObjectName(u"actionUser_guide")
        icon12 = QIcon()
        icon12.addFile(u":/icons/menu_icons/question-circle.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionUser_guide.setIcon(icon12)
        self.actionUndo = QAction(MainWindow)
        self.actionUndo.setObjectName(u"actionUndo")
        self.actionUndo.setEnabled(False)
        icon13 = QIcon()
        icon13.addFile(u":/icons/menu_icons/undo.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionUndo.setIcon(icon13)
        self.actionRedo = QAction(MainWindow)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionRedo.setEnabled(False)
        icon14 = QIcon()
        icon14.addFile(u":/icons/menu_icons/redo.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionRedo.setIcon(icon14)
        self.actionNew_db_file = QAction(MainWindow)
        self.actionNew_db_file.setObjectName(u"actionNew_db_file")
        icon15 = QIcon()
        icon15.addFile(u":/icons/menu_icons/file.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionNew_db_file.setIcon(icon15)
        self.actionOpen_db_file = QAction(MainWindow)
        self.actionOpen_db_file.setObjectName(u"actionOpen_db_file")
        icon16 = QIcon()
        icon16.addFile(u":/icons/menu_icons/folder-open-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionOpen_db_file.setIcon(icon16)
        self.actionAdd_db_file = QAction(MainWindow)
        self.actionAdd_db_file.setObjectName(u"actionAdd_db_file")
        self.actionAdd_db_file.setIcon(icon16)
        self.actionVacuum = QAction(MainWindow)
        self.actionVacuum.setObjectName(u"actionVacuum")
        icon17 = QIcon()
        icon17.addFile(u":/icons/menu_icons/broom.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.actionVacuum.setIcon(icon17)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        MainWindow.setCentralWidget(self.centralwidget)
        self.alternative_dock_widget = QDockWidget(MainWindow)
        self.alternative_dock_widget.setObjectName(u"alternative_dock_widget")
        self.alternative_dock_widget.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockWidgetContents_15 = QWidget()
        self.dockWidgetContents_15.setObjectName(u"dockWidgetContents_15")
        self.verticalLayout_18 = QVBoxLayout(self.dockWidgetContents_15)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.alternative_tree_view = AlternativeTreeView(self.dockWidgetContents_15)
        self.alternative_tree_view.setObjectName(u"alternative_tree_view")
        self.alternative_tree_view.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.alternative_tree_view.setDragEnabled(True)
        self.alternative_tree_view.setDragDropMode(QAbstractItemView.DragOnly)
        self.alternative_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.alternative_tree_view.setUniformRowHeights(True)

        self.verticalLayout_18.addWidget(self.alternative_tree_view)

        self.alternative_dock_widget.setWidget(self.dockWidgetContents_15)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.alternative_dock_widget)
        self.dockWidget_parameter_value_list = QDockWidget(MainWindow)
        self.dockWidget_parameter_value_list.setObjectName(u"dockWidget_parameter_value_list")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.treeView_parameter_value_list = ParameterValueListTreeView(self.dockWidgetContents)
        self.treeView_parameter_value_list.setObjectName(u"treeView_parameter_value_list")
        self.treeView_parameter_value_list.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.treeView_parameter_value_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_parameter_value_list.setUniformRowHeights(True)
        self.treeView_parameter_value_list.header().setVisible(True)

        self.verticalLayout.addWidget(self.treeView_parameter_value_list)

        self.dockWidget_parameter_value_list.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_parameter_value_list)
        self.dockWidget_parameter_value = QDockWidget(MainWindow)
        self.dockWidget_parameter_value.setObjectName(u"dockWidget_parameter_value")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tableView_parameter_value = ParameterValueTableView(self.dockWidgetContents_2)
        self.tableView_parameter_value.setObjectName(u"tableView_parameter_value")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tableView_parameter_value.sizePolicy().hasHeightForWidth())
        self.tableView_parameter_value.setSizePolicy(sizePolicy1)
        self.tableView_parameter_value.setMouseTracking(True)
        self.tableView_parameter_value.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.tableView_parameter_value.setLayoutDirection(Qt.LeftToRight)
        self.tableView_parameter_value.setTabKeyNavigation(False)
        self.tableView_parameter_value.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tableView_parameter_value.setSortingEnabled(False)
        self.tableView_parameter_value.setWordWrap(False)
        self.tableView_parameter_value.horizontalHeader().setHighlightSections(False)
        self.tableView_parameter_value.horizontalHeader().setStretchLastSection(True)
        self.tableView_parameter_value.verticalHeader().setVisible(False)
        self.tableView_parameter_value.verticalHeader().setHighlightSections(False)

        self.verticalLayout_5.addWidget(self.tableView_parameter_value)

        self.dockWidget_parameter_value.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_parameter_value)
        self.dockWidget_parameter_definition = QDockWidget(MainWindow)
        self.dockWidget_parameter_definition.setObjectName(u"dockWidget_parameter_definition")
        self.dockWidgetContents_5 = QWidget()
        self.dockWidgetContents_5.setObjectName(u"dockWidgetContents_5")
        self.verticalLayout_10 = QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.tableView_parameter_definition = ParameterDefinitionTableView(self.dockWidgetContents_5)
        self.tableView_parameter_definition.setObjectName(u"tableView_parameter_definition")
        sizePolicy1.setHeightForWidth(self.tableView_parameter_definition.sizePolicy().hasHeightForWidth())
        self.tableView_parameter_definition.setSizePolicy(sizePolicy1)
        self.tableView_parameter_definition.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.tableView_parameter_definition.setLayoutDirection(Qt.LeftToRight)
        self.tableView_parameter_definition.setTabKeyNavigation(False)
        self.tableView_parameter_definition.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tableView_parameter_definition.setSortingEnabled(False)
        self.tableView_parameter_definition.setWordWrap(False)
        self.tableView_parameter_definition.horizontalHeader().setHighlightSections(False)
        self.tableView_parameter_definition.horizontalHeader().setStretchLastSection(True)
        self.tableView_parameter_definition.verticalHeader().setVisible(False)
        self.tableView_parameter_definition.verticalHeader().setHighlightSections(False)

        self.verticalLayout_10.addWidget(self.tableView_parameter_definition)

        self.dockWidget_parameter_definition.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_parameter_definition)
        self.dockWidget_entity_tree = QDockWidget(MainWindow)
        self.dockWidget_entity_tree.setObjectName(u"dockWidget_entity_tree")
        self.dockWidget_entity_tree.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockWidgetContents_6 = QWidget()
        self.dockWidgetContents_6.setObjectName(u"dockWidgetContents_6")
        self.verticalLayout_4 = QVBoxLayout(self.dockWidgetContents_6)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.treeView_entity = EntityTreeView(self.dockWidgetContents_6)
        self.treeView_entity.setObjectName(u"treeView_entity")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.treeView_entity.sizePolicy().hasHeightForWidth())
        self.treeView_entity.setSizePolicy(sizePolicy2)
        self.treeView_entity.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.treeView_entity.setEditTriggers(QAbstractItemView.EditKeyPressed)
        self.treeView_entity.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView_entity.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.treeView_entity.setIconSize(QSize(20, 20))
        self.treeView_entity.setUniformRowHeights(True)

        self.verticalLayout_4.addWidget(self.treeView_entity)

        self.dockWidget_entity_tree.setWidget(self.dockWidgetContents_6)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_entity_tree)
        self.dockWidget_entity_graph = QDockWidget(MainWindow)
        self.dockWidget_entity_graph.setObjectName(u"dockWidget_entity_graph")
        self.dockWidgetContents_8 = QWidget()
        self.dockWidgetContents_8.setObjectName(u"dockWidgetContents_8")
        self.verticalLayout_7 = QVBoxLayout(self.dockWidgetContents_8)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.graphicsView = EntityQGraphicsView(self.dockWidgetContents_8)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy1.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy1)
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.setFrameShape(QFrame.NoFrame)
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)

        self.verticalLayout_7.addWidget(self.graphicsView)

        self.dockWidget_entity_graph.setWidget(self.dockWidgetContents_8)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_entity_graph)
        self.dockWidget_pivot_table = QDockWidget(MainWindow)
        self.dockWidget_pivot_table.setObjectName(u"dockWidget_pivot_table")
        self.dockWidgetContents_10 = QWidget()
        self.dockWidgetContents_10.setObjectName(u"dockWidgetContents_10")
        self.verticalLayout_13 = QVBoxLayout(self.dockWidgetContents_10)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.pivot_table = PivotTableView(self.dockWidgetContents_10)
        self.pivot_table.setObjectName(u"pivot_table")
        self.pivot_table.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.pivot_table.setTabKeyNavigation(False)

        self.verticalLayout_13.addWidget(self.pivot_table)

        self.dockWidget_pivot_table.setWidget(self.dockWidgetContents_10)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_pivot_table)
        self.dockWidget_frozen_table = QDockWidget(MainWindow)
        self.dockWidget_frozen_table.setObjectName(u"dockWidget_frozen_table")
        self.dockWidgetContents_11 = QWidget()
        self.dockWidgetContents_11.setObjectName(u"dockWidgetContents_11")
        self.verticalLayout_14 = QVBoxLayout(self.dockWidgetContents_11)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.frozen_table = FrozenTableView(self.dockWidgetContents_11)
        self.frozen_table.setObjectName(u"frozen_table")
        self.frozen_table.setAcceptDrops(True)
        self.frozen_table.setTabKeyNavigation(False)
        self.frozen_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.frozen_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.frozen_table.horizontalHeader().setVisible(False)
        self.frozen_table.verticalHeader().setVisible(False)

        self.verticalLayout_14.addWidget(self.frozen_table)

        self.dockWidget_frozen_table.setWidget(self.dockWidgetContents_11)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_frozen_table)
        self.dockWidget_exports = QDockWidget(MainWindow)
        self.dockWidget_exports.setObjectName(u"dockWidget_exports")
        self.dockWidget_exports.setMaximumSize(QSize(524287, 64))
        self.dockWidget_exports.setFeatures(QDockWidget.DockWidgetClosable)
        self.dockWidget_exports.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.dockWidgetContents_12 = QWidget()
        self.dockWidgetContents_12.setObjectName(u"dockWidgetContents_12")
        self.horizontalLayout_3 = QHBoxLayout(self.dockWidgetContents_12)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_exports = QHBoxLayout()
        self.horizontalLayout_exports.setSpacing(1)
        self.horizontalLayout_exports.setObjectName(u"horizontalLayout_exports")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_exports.addItem(self.horizontalSpacer)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_exports)

        self.dockWidget_exports.setWidget(self.dockWidgetContents_12)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidget_exports)
        self.dockWidget_tool_feature_tree = QDockWidget(MainWindow)
        self.dockWidget_tool_feature_tree.setObjectName(u"dockWidget_tool_feature_tree")
        self.dockWidgetContents_13 = QWidget()
        self.dockWidgetContents_13.setObjectName(u"dockWidgetContents_13")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents_13)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.treeView_tool_feature = ToolFeatureTreeView(self.dockWidgetContents_13)
        self.treeView_tool_feature.setObjectName(u"treeView_tool_feature")
        self.treeView_tool_feature.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.treeView_tool_feature.setDragEnabled(True)
        self.treeView_tool_feature.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeView_tool_feature.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.verticalLayout_2.addWidget(self.treeView_tool_feature)

        self.dockWidget_tool_feature_tree.setWidget(self.dockWidgetContents_13)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_tool_feature_tree)
        self.metadata_dock_widget = QDockWidget(MainWindow)
        self.metadata_dock_widget.setObjectName(u"metadata_dock_widget")
        self.metadata_dock_contents = QWidget()
        self.metadata_dock_contents.setObjectName(u"metadata_dock_contents")
        self.verticalLayout_11 = QVBoxLayout(self.metadata_dock_contents)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.metadata_table_view = MetadataTableView(self.metadata_dock_contents)
        self.metadata_table_view.setObjectName(u"metadata_table_view")
        self.metadata_table_view.setSortingEnabled(True)
        self.metadata_table_view.verticalHeader().setVisible(False)

        self.verticalLayout_11.addWidget(self.metadata_table_view)

        self.metadata_dock_widget.setWidget(self.metadata_dock_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.metadata_dock_widget)
        self.item_metadata_dock_widget = QDockWidget(MainWindow)
        self.item_metadata_dock_widget.setObjectName(u"item_metadata_dock_widget")
        self.item_metadata_dock_contents = QWidget()
        self.item_metadata_dock_contents.setObjectName(u"item_metadata_dock_contents")
        self.verticalLayout_9 = QVBoxLayout(self.item_metadata_dock_contents)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.item_metadata_table_view = ItemMetadataTableView(self.item_metadata_dock_contents)
        self.item_metadata_table_view.setObjectName(u"item_metadata_table_view")
        self.item_metadata_table_view.setEnabled(False)
        self.item_metadata_table_view.setSortingEnabled(True)
        self.item_metadata_table_view.verticalHeader().setVisible(False)

        self.verticalLayout_9.addWidget(self.item_metadata_table_view)

        self.item_metadata_dock_widget.setWidget(self.item_metadata_dock_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.item_metadata_dock_widget)
        self.scenario_dock_widget = QDockWidget(MainWindow)
        self.scenario_dock_widget.setObjectName(u"scenario_dock_widget")
        self.dockWidgetContents_9 = QWidget()
        self.dockWidgetContents_9.setObjectName(u"dockWidgetContents_9")
        self.verticalLayout_12 = QVBoxLayout(self.dockWidgetContents_9)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.scenario_tree_view = ScenarioTreeView(self.dockWidgetContents_9)
        self.scenario_tree_view.setObjectName(u"scenario_tree_view")
        self.scenario_tree_view.setAcceptDrops(True)
        self.scenario_tree_view.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.scenario_tree_view.setDragEnabled(True)
        self.scenario_tree_view.setDragDropMode(QAbstractItemView.DragDrop)
        self.scenario_tree_view.setDefaultDropAction(Qt.MoveAction)
        self.scenario_tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.scenario_tree_view.setUniformRowHeights(True)

        self.verticalLayout_12.addWidget(self.scenario_tree_view)

        self.scenario_dock_widget.setWidget(self.dockWidgetContents_9)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.scenario_dock_widget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionCommit.setText(QCoreApplication.translate("MainWindow", u"&Commit...", None))
#if QT_CONFIG(shortcut)
        self.actionCommit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Return", None))
#endif // QT_CONFIG(shortcut)
        self.actionRollback.setText(QCoreApplication.translate("MainWindow", u"Roll&back", None))
#if QT_CONFIG(shortcut)
        self.actionRollback.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Backspace", None))
#endif // QT_CONFIG(shortcut)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionImport.setText(QCoreApplication.translate("MainWindow", u"I&mport...", None))
#if QT_CONFIG(tooltip)
        self.actionImport.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Import data from file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionExport.setText(QCoreApplication.translate("MainWindow", u"&Export...", None))
#if QT_CONFIG(tooltip)
        self.actionExport.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Export data into file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"Cop&y", None))
#if QT_CONFIG(shortcut)
        self.actionCopy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"P&aste", None))
#if QT_CONFIG(shortcut)
        self.actionPaste.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionStacked_style.setText(QCoreApplication.translate("MainWindow", u"T&able", None))
#if QT_CONFIG(tooltip)
        self.actionStacked_style.setToolTip(QCoreApplication.translate("MainWindow", u"Table", None))
#endif // QT_CONFIG(tooltip)
        self.actionGraph_style.setText(QCoreApplication.translate("MainWindow", u"&Graph", None))
#if QT_CONFIG(tooltip)
        self.actionGraph_style.setToolTip(QCoreApplication.translate("MainWindow", u"Graph", None))
#endif // QT_CONFIG(tooltip)
        self.actionView_history.setText(QCoreApplication.translate("MainWindow", u"&History...", None))
        self.actionMass_remove_items.setText(QCoreApplication.translate("MainWindow", u"P&urge...", None))
#if QT_CONFIG(tooltip)
        self.actionMass_remove_items.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Mass-remove items</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionExport_session.setText(QCoreApplication.translate("MainWindow", u"E&xport session...", None))
#if QT_CONFIG(tooltip)
        self.actionExport_session.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Export current session (changes since last commit) into file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Settings...", None))
#if QT_CONFIG(shortcut)
        self.actionSettings.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+,", None))
#endif // QT_CONFIG(shortcut)
        self.actionUser_guide.setText(QCoreApplication.translate("MainWindow", u"User guide", None))
#if QT_CONFIG(shortcut)
        self.actionUser_guide.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.actionUndo.setText(QCoreApplication.translate("MainWindow", u"Un&do", None))
        self.actionRedo.setText(QCoreApplication.translate("MainWindow", u"&Redo", None))
        self.actionNew_db_file.setText(QCoreApplication.translate("MainWindow", u"&New...", None))
#if QT_CONFIG(tooltip)
        self.actionNew_db_file.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>New database file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpen_db_file.setText(QCoreApplication.translate("MainWindow", u"&Open...", None))
#if QT_CONFIG(tooltip)
        self.actionOpen_db_file.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Open database file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.actionAdd_db_file.setText(QCoreApplication.translate("MainWindow", u"Add...", None))
#if QT_CONFIG(tooltip)
        self.actionAdd_db_file.setToolTip(QCoreApplication.translate("MainWindow", u"Add database file to the current view", None))
#endif // QT_CONFIG(tooltip)
        self.actionVacuum.setText(QCoreApplication.translate("MainWindow", u"Vacuum", None))
        self.alternative_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Alternative tree", None))
#if QT_CONFIG(accessibility)
        self.alternative_tree_view.setAccessibleName(QCoreApplication.translate("MainWindow", u"alternative tree", None))
#endif // QT_CONFIG(accessibility)
        self.dockWidget_parameter_value_list.setWindowTitle(QCoreApplication.translate("MainWindow", u"Parameter value list", None))
#if QT_CONFIG(accessibility)
        self.treeView_parameter_value_list.setAccessibleName(QCoreApplication.translate("MainWindow", u"parameter value list", None))
#endif // QT_CONFIG(accessibility)
        self.dockWidget_parameter_value.setWindowTitle(QCoreApplication.translate("MainWindow", u"Parameter value", None))
#if QT_CONFIG(accessibility)
        self.tableView_parameter_value.setAccessibleName(QCoreApplication.translate("MainWindow", u"relationship parameter value", None))
#endif // QT_CONFIG(accessibility)
        self.dockWidget_parameter_definition.setWindowTitle(QCoreApplication.translate("MainWindow", u"Parameter definition", None))
#if QT_CONFIG(accessibility)
        self.tableView_parameter_definition.setAccessibleName(QCoreApplication.translate("MainWindow", u"relationship parameter definition", None))
#endif // QT_CONFIG(accessibility)
        self.dockWidget_entity_tree.setWindowTitle(QCoreApplication.translate("MainWindow", u"Entity tree", None))
#if QT_CONFIG(accessibility)
        self.treeView_entity.setAccessibleName(QCoreApplication.translate("MainWindow", u"object tree", None))
#endif // QT_CONFIG(accessibility)
        self.dockWidget_entity_graph.setWindowTitle(QCoreApplication.translate("MainWindow", u"Entity graph", None))
        self.dockWidget_pivot_table.setWindowTitle(QCoreApplication.translate("MainWindow", u"Pivot table", None))
        self.dockWidget_frozen_table.setWindowTitle(QCoreApplication.translate("MainWindow", u"Frozen table", None))
        self.dockWidget_exports.setWindowTitle(QCoreApplication.translate("MainWindow", u"Exports", None))
        self.dockWidget_tool_feature_tree.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tool/Feature tree", None))
        self.metadata_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Metadata", None))
        self.item_metadata_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Item metadata", None))
        self.scenario_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Scenario tree", None))
#if QT_CONFIG(accessibility)
        self.scenario_tree_view.setAccessibleName(QCoreApplication.translate("MainWindow", u"scenario tree", None))
#endif // QT_CONFIG(accessibility)
    # retranslateUi

