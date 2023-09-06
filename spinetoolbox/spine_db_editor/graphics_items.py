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

"""
Classes for drawing graphics items on graph view's QGraphicsScene.
"""
from PySide6.QtCore import Qt, Signal, Slot, QLineF, QRectF
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QStyle,
    QApplication,
    QMenu,
)
from PySide6.QtGui import QPen, QBrush, QPainterPath, QPalette, QGuiApplication, QAction
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas  # pylint: disable=no-name-in-module

from spinetoolbox.helpers import DB_ITEM_SEPARATOR
from spinetoolbox.widgets.custom_qwidgets import TitleWidgetAction


def make_figure_graphics_item(scene, z=0, static=True):
    """Creates a FigureCanvas and adds it to the given scene.
    Used for creating heatmaps and associated colorbars.

    Args:
        scene (QGraphicsScene)
        z (int, optional): z value. Defaults to 0.
        static (bool, optional): if True (the default) the figure canvas is not movable

    Returns:
        QGraphicsProxyWidget: the graphics item that represents the canvas
        Figure: the figure in the canvas
    """
    figure = Figure(tight_layout={"pad": 0})
    axes = figure.gca(xmargin=0, ymargin=0, frame_on=None)
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    canvas = FigureCanvas(figure)
    if static:
        proxy_widget = scene.addWidget(canvas)
        proxy_widget.setAcceptedMouseButtons(Qt.NoButton)
    else:
        proxy_widget = scene.addWidget(canvas, Qt.Window)
    proxy_widget.setZValue(z)
    return proxy_widget, figure


class EntityItem(QGraphicsRectItem):
    def __init__(self, spine_db_editor, x, y, extent, db_map_ids):
        """
        Args:
            spine_db_editor (SpineDBEditor): 'owner'
            x (float): x-coordinate of central point
            y (float): y-coordinate of central point
            extent (int): Preferred extent
            db_map_ids (tuple): tuple of (db_map, id) tuples
        """
        super().__init__()
        self._spine_db_editor = spine_db_editor
        self.db_mngr = spine_db_editor.db_mngr
        self._given_extent = extent
        self._db_map_ids = db_map_ids
        self._dx = self._dy = 0
        self._removed_db_map_ids = ()
        self.arc_items = []
        self.set_pos(x, y)
        self.setPen(Qt.NoPen)
        self._svg_item = QGraphicsSvgItem(self)
        self._svg_item.setZValue(100)
        self._svg_item.setCacheMode(QGraphicsItem.CacheMode.NoCache)  # Needed for the exported pdf to be vector
        self._renderer = None
        self._moved_on_scene = False
        self._bg = None
        self._bg_brush = Qt.NoBrush
        self.setZValue(0)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=True)
        self.setFlag(QGraphicsItem.ItemIsMovable, enabled=True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, enabled=True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, enabled=True)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.ArrowCursor)
        self.setToolTip(self._make_tool_tip())
        self._highlight_color = Qt.transparent
        self._db_map_entity_class_lists = {}
        self.label_item = EntityLabelItem(self)
        self.label_item.setVisible(not self.has_dimensions)
        self.setZValue(0.5 if not self.has_dimensions else 0.25)
        self._extent = None
        self.update_name()

    @property
    def has_dimensions(self):
        return bool(self.element_id_list(self.first_db_map))

    @property
    def db_map_ids(self):
        return tuple(x for x in self._db_map_ids if x not in self._removed_db_map_ids)

    @property
    def original_db_map_ids(self):
        return self._db_map_ids

    @property
    def entity_name(self):
        return self.db_mngr.get_item(self.first_db_map, "entity", self.first_id).get("name", "")

    @property
    def first_entity_class_id(self):
        return self.db_mngr.get_item(self.first_db_map, "entity", self.first_id).get("class_id")

    @property
    def entity_class_name(self):
        return self.db_mngr.get_item(self.first_db_map, "entity_class", self.first_entity_class_id).get("name", "")

    @property
    def dimension_id_list(self):
        # FIXME: where is this used?
        return self.db_mngr.get_item(self.first_db_map, "entity_class", self.first_entity_class_id).get(
            "dimension_id_list", ()
        )

    @property
    def entity_byname(self):
        return self.db_mngr.get_item(self.first_db_map, "entity", self.first_id).get("byname", ())

    @property
    def element_name_list(self):
        return self.db_mngr.get_item(self.first_db_map, "entity", self.first_id).get("element_name_list", ())

    def element_id_list(self, db_map):
        return self.db_mngr.get_item(db_map, "entity", self.entity_id(db_map)).get("element_id_list", ())

    @property
    def first_db_map_id(self):
        return next(iter(self.db_map_ids), (None, None))

    @property
    def first_id(self):
        return self.first_db_map_id[1]

    @property
    def first_db_map(self):
        return self.first_db_map_id[0]

    @property
    def display_data(self):
        return self.entity_name

    @property
    def display_database(self):
        return ",".join([db_map.codename for db_map in self.db_maps])

    @property
    def db_maps(self):
        return list(db_map for db_map, _id in self.db_map_ids)

    def entity_class_id(self, db_map):
        return self.db_mngr.get_item(db_map, "entity", self.entity_id(db_map)).get("class_id")

    def entity_id(self, db_map):
        return dict(self.db_map_ids).get(db_map)

    def db_map_data(self, db_map):
        # NOTE: Needed by EditEntitiesDialog
        return self.db_mngr.get_item(db_map, "entity", self.entity_id(db_map))

    def db_map_id(self, db_map):
        # NOTE: Needed by EditEntitiesDialog
        return self.entity_id(db_map)

    def db_items(self, db_map):
        for db_map_, id_ in self.db_map_ids:
            if db_map_ == db_map:
                yield dict(class_id=self.entity_class_id(db_map), id=id_)

    def boundingRect(self):
        return super().boundingRect() | self.childrenBoundingRect()

    def set_pos(self, x, y):
        x, y = self._snap(x, y)
        self.setPos(x, y)
        self.update_arcs_line()

    def move_by(self, dx, dy):
        self._dx += dx
        self._dy += dy
        dx, dy = self._snap(self._dx, self._dy)
        if dx == dy == 0:
            return
        self.moveBy(dx, dy)
        self._dx -= dx
        self._dy -= dy
        self.update_arcs_line()
        ent_items = {arc_item.ent_item for arc_item in self.arc_items}
        for ent_item in ent_items:
            ent_item.update_entity_pos()

    def _snap(self, x, y):
        if self._spine_db_editor.qsettings.value("appSettings/snapEntities", defaultValue="false") != "true":
            return (x, y)
        grid_size = self._given_extent
        x = round(x / grid_size) * grid_size
        y = round(y / grid_size) * grid_size
        return (x, y)

    def _has_name(self):
        return bool(self.label_item.toPlainText())

    def _do_update_name(self):
        db_map_ids_by_name = {}
        for db_map, id_ in self.db_map_ids:
            name = self._spine_db_editor.get_item_name(db_map, id_)
            db_map_ids_by_name.setdefault(name, []).append((db_map, id_))
        if len(db_map_ids_by_name) == 1:
            name = next(iter(db_map_ids_by_name))
            self.label_item.setPlainText(name)
            return True
        current_name = self.label_item.toPlainText()
        self._db_map_ids = tuple(db_map_ids_by_name.get(current_name, ()))
        return False

    def color(self):
        for db_map, id_ in self.db_map_ids:
            color = self._spine_db_editor.get_item_color(db_map, id_)
            try:
                return int(1000 * color)
            except Exception:  # pylint: disable=broad-except
                pass

    def _update_all(self):
        if not self._has_name():
            self.label_item.hide()
            self._extent = 0.2 * self._given_extent
        else:
            if not self.has_dimensions:
                self.label_item.show()
                self._extent = self._given_extent
            else:
                self.label_item.hide()
                self._extent = 0.5 * self._given_extent
        self.setRect(-0.5 * self._extent, -0.5 * self._extent, self._extent, self._extent)
        self.refresh_icon()
        self._init_bg()

    def _init_bg(self):
        bg_rect = QRectF(-0.5 * self._extent, -0.5 * self._extent, self._extent, self._extent)
        if not self.has_dimensions:
            self._bg = QGraphicsRectItem(bg_rect, self)
            self._bg.setFlag(QGraphicsItem.ItemStacksBehindParent, enabled=True)
        else:
            self._bg = QGraphicsEllipseItem(bg_rect, self)
            self._bg_brush = QGuiApplication.palette().button()
        pen = self._bg.pen()
        pen.setColor(Qt.transparent)
        self._bg.setPen(pen)

    def refresh_icon(self):
        """Refreshes the icon."""
        renderer = self.db_mngr.entity_class_renderer(
            self.first_db_map, self.first_entity_class_id, color_code=self.color()
        )
        self._set_renderer(renderer)

    def _set_renderer(self, renderer):
        self._renderer = renderer
        self._svg_item.setSharedRenderer(renderer)
        size = renderer.defaultSize()
        scale = self._extent / max(size.width(), size.height())
        self._svg_item.setScale(scale)
        rect = self._svg_item.boundingRect()
        self._svg_item.setTransformOriginPoint(rect.center())
        self._svg_item.setPos(-rect.center())

    def update_name(self):
        """Refreshes the name."""
        result = self._do_update_name()
        self._update_all()
        return result

    def _make_tool_tip(self):
        if not self.first_id:
            return None
        return (
            f"""<html><p style="text-align:center;">{self.entity_class_name}<br>"""
            f"""{DB_ITEM_SEPARATOR.join(self.entity_byname)}<br>"""
            f"""@{self.display_database}</p></html>"""
        )

    def default_parameter_data(self):
        """Return data to put as default in a parameter table when this item is selected."""
        if not self.db_map_ids:
            return {}
        return dict(
            entity_class_name=self.entity_class_name,
            entity_byname=DB_ITEM_SEPARATOR.join(self.entity_byname),
            database=self.first_db_map.codename,
        )

    def shape(self):
        """Returns a shape containing the entire bounding rect, to work better with icon transparency."""
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRect(self._bg.boundingRect())
        path.addPolygon(self.label_item.mapToItem(self, self.label_item.boundingRect()))
        return path

    def set_highlight_color(self, color):
        self._highlight_color = color

    def paint(self, painter, option, widget=None):
        """Shows or hides the selection halo."""
        if option.state & (QStyle.StateFlag.State_Selected):
            self._paint_as_selected()
            option.state &= ~QStyle.StateFlag.State_Selected
        else:
            self._paint_as_deselected()
        pen = self._bg.pen()
        pen.setColor(self._highlight_color)
        width = 10 / self.scale()
        pen.setWidth(width)
        self._bg.setPen(pen)
        super().paint(painter, option, widget)

    def _paint_as_selected(self):
        self._bg.setBrush(QGuiApplication.palette().highlight())

    def _paint_as_deselected(self):
        self._bg.setBrush(self._bg_brush)

    def add_arc_item(self, arc_item):
        """Adds an item to the list of arcs.

        Args:
            arc_item (ArcItem)
        """
        self.arc_items.append(arc_item)
        arc_item.update_line()
        self._rotate_svg_item()
        self.update_entity_pos()

    def update_entity_pos(self):
        dim_count = len(self.element_id_list(self.first_db_map))
        if not dim_count:
            return
        el_items = {arc_item.el_item for arc_item in self.arc_items}
        if len(el_items) != dim_count:
            return
        new_pos_x = sum(el_item.pos().x() for el_item in el_items) / dim_count
        new_pos_y = sum(el_item.pos().y() for el_item in el_items) / dim_count
        self.setPos(new_pos_x, new_pos_y)
        self.update_arcs_line()

    def apply_zoom(self, factor):
        """Applies zoom.

        Args:
            factor (float): The zoom factor.
        """
        factor = min(factor, 1)
        self.setScale(factor)

    def apply_rotation(self, angle, center):
        """Applies rotation.

        Args:
            angle (float): The angle in degrees.
            center (QPointF): Rotates around this point.
        """
        line = QLineF(center, self.pos())
        line.setAngle(line.angle() + angle)
        pos = line.p2()
        self.set_pos(pos.x(), pos.y())

    def mouseMoveEvent(self, event):
        """Moves the item and all connected arcs.

        Args:
            event (QGraphicsSceneMouseEvent)
        """
        if event.buttons() & Qt.LeftButton == 0:
            super().mouseMoveEvent(event)
            return
        move_by = event.scenePos() - event.lastScenePos()
        # Move selected items together
        for item in self.scene().selectedItems():
            if isinstance(item, (EntityItem)):
                item.move_by(move_by.x(), move_by.y())

    def update_arcs_line(self):
        """Moves arc items."""
        for item in self.arc_items:
            item.update_line()

    def itemChange(self, change, value):
        """
        Keeps track of item's movements on the scene. Rotates svg item if the relationship is 2D.
        This makes it possible to define e.g. an arow icon for relationships that express direction.

        Args:
            change (GraphicsItemChange): a flag signalling the type of the change
            value: a value related to the change

        Returns:
            the same value given as input
        """
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            self._moved_on_scene = True
            self._rotate_svg_item()
        return super().itemChange(change, value)

    def setVisible(self, on):
        """Sets visibility status for this item and all arc items.

        Args:
            on (bool)
        """
        super().setVisible(on)
        for arc_item in self.arc_items:
            arc_item.setVisible(arc_item.el_item.isVisible() and arc_item.ent_item.isVisible())

    def _make_menu(self):
        menu = self._spine_db_editor.ui.graphicsView.make_items_menu()
        expand_menu = QMenu("Expand", menu)
        expand_menu.triggered.connect(self._expand)
        collapse_menu = QMenu("Collapse", menu)
        collapse_menu.triggered.connect(self._collapse)
        connect_entities_menu = QMenu("Connect entities", menu)
        connect_entities_menu.triggered.connect(self._start_connecting_entities)
        self._refresh_entity_class_lists()
        self._populate_expand_collapse_menu(expand_menu)
        self._populate_expand_collapse_menu(collapse_menu)
        self._populate_connect_entities_menu(connect_entities_menu)
        first = menu.actions()[0]
        first = menu.insertSeparator(first)
        first = menu.insertMenu(first, connect_entities_menu)
        first = menu.insertMenu(first, collapse_menu)
        menu.insertMenu(first, expand_menu)
        menu.addAction("Duplicate", self._duplicate)
        return menu

    def contextMenuEvent(self, e):
        """Shows context menu.

        Args:
            e (QGraphicsSceneMouseEvent): Mouse event
        """
        e.accept()
        if not self.isSelected() and not e.modifiers() & Qt.ControlModifier:
            self.scene().clearSelection()
        self.setSelected(True)
        menu = self._make_menu()
        menu.popup(e.screenPos())

    def remove_db_map_ids(self, db_map_ids):
        """Removes db_map_ids."""
        self._removed_db_map_ids += tuple(db_map_ids)
        self.setToolTip(self._make_tool_tip())

    def add_db_map_ids(self, db_map_ids):
        for db_map_id in db_map_ids:
            if db_map_id not in self._db_map_ids:
                self._db_map_ids += (db_map_id,)
            else:
                self._removed_db_map_ids = tuple(x for x in self._removed_db_map_ids if x != db_map_id)
        self.setToolTip(self._make_tool_tip())

    def _rotate_svg_item(self):
        if len(self.arc_items) != 2:
            self._svg_item.setRotation(0)
            return
        arc1, arc2 = self.arc_items  # pylint: disable=unbalanced-tuple-unpacking
        obj1, obj2 = arc1.el_item, arc2.el_item
        line = QLineF(obj1.pos(), obj2.pos())
        self._svg_item.setRotation(-line.angle())

    def mouseDoubleClickEvent(self, e):
        connect_entities_menu = QMenu(self._spine_db_editor)
        title = TitleWidgetAction("Connect entities", self._spine_db_editor)
        connect_entities_menu.addAction(title)
        connect_entities_menu.triggered.connect(self._start_connecting_entities)
        self._refresh_entity_class_lists()
        self._populate_connect_entities_menu(connect_entities_menu)
        connect_entities_menu.popup(e.screenPos())

    def _duplicate(self):
        self._spine_db_editor.duplicate_entity(self)

    def _refresh_entity_class_lists(self):
        self._db_map_entity_class_lists.clear()
        db_map_entity_ids = {db_map: {id_} for db_map, id_ in self.db_map_ids}
        entity_ids_per_class = {}
        for db_map, ents in self.db_mngr.find_cascading_entities(db_map_entity_ids).items():
            for ent in ents:
                entity_ids_per_class.setdefault((db_map, ent["class_id"]), set()).add(ent["id"])
        db_map_entity_class_ids = {db_map: {self.entity_class_id(db_map)} for db_map in self.db_maps}
        for db_map, ent_clss in self.db_mngr.find_cascading_entity_classes(db_map_entity_class_ids).items():
            for ent_cls in ent_clss:
                ent_cls = ent_cls._extended()
                ent_cls["dimension_id_list"] = list(ent_cls["dimension_id_list"])
                ent_cls["entity_ids"] = entity_ids_per_class.get((db_map, ent_cls["id"]), set())
                self._db_map_entity_class_lists.setdefault(ent_cls["name"], []).append((db_map, ent_cls))

    def _populate_expand_collapse_menu(self, menu):
        """
        Populates the 'Expand' or 'Collapse' menu.

        Args:
            menu (QMenu)
        """
        if not self._db_map_entity_class_lists:
            menu.setEnabled(False)
            return
        menu.setEnabled(True)
        menu.addAction("All")
        menu.addSeparator()
        for name, db_map_ent_cls_lst in sorted(self._db_map_entity_class_lists.items()):
            db_map, ent_cls = next(iter(db_map_ent_cls_lst))
            icon = self.db_mngr.entity_class_icon(db_map, ent_cls["id"])
            menu.addAction(icon, name).setEnabled(
                any(rel_cls["entity_ids"] for (db_map, rel_cls) in db_map_ent_cls_lst)
            )

    def _populate_connect_entities_menu(self, menu):
        """
        Populates the 'Add relationships' menu.

        Args:
            menu (QMenu)
        """
        entity_class_ids_in_graph = {}
        for item in self._spine_db_editor.ui.graphicsView.entity_items:
            if not isinstance(item, EntityItem):
                continue
            for db_map in item.db_maps:
                entity_class_ids_in_graph.setdefault(db_map, set()).add(item.entity_class_id(db_map))
        action_name_icon_enabled = []
        for name, db_map_ent_cls_lst in self._db_map_entity_class_lists.items():
            for db_map, ent_cls in db_map_ent_cls_lst:
                icon = self.db_mngr.entity_class_icon(db_map, ent_cls["id"])
                action_name = name + "@" + db_map.codename
                enabled = set(ent_cls["dimension_id_list"]) <= entity_class_ids_in_graph.get(db_map, set())
                action_name_icon_enabled.append((action_name, icon, enabled))
        for action_name, icon, enabled in sorted(action_name_icon_enabled):
            menu.addAction(icon, action_name).setEnabled(enabled)
        menu.setEnabled(bool(self._db_map_entity_class_lists))

    def _get_db_map_entity_ids_to_expand_or_collapse(self, action):
        db_map_ent_clss = self._db_map_entity_class_lists.get(action.text())
        if db_map_ent_clss is not None:
            return {(db_map, id_) for db_map, ent_cls in db_map_ent_clss for id_ in ent_cls["entity_ids"]}
        return {
            (db_map, id_)
            for class_list in self._db_map_entity_class_lists.values()
            for db_map, ent_cls in class_list
            for id_ in ent_cls["entity_ids"]
        }

    @Slot(QAction)
    def _expand(self, action):
        db_map_entity_ids = self._get_db_map_entity_ids_to_expand_or_collapse(action)
        self._spine_db_editor.added_db_map_entity_ids.update(db_map_entity_ids)
        self._spine_db_editor.build_graph(persistent=True)

    @Slot(QAction)
    def _collapse(self, action):
        db_map_entity_ids = self._get_db_map_entity_ids_to_expand_or_collapse(action)
        self._spine_db_editor.added_db_map_entity_ids.difference_update(db_map_entity_ids)
        self._spine_db_editor.build_graph(persistent=True)

    @Slot(QAction)
    def _start_connecting_entities(self, action):
        class_name, db_name = action.text().split("@")
        db_map_ent_cls_lst = self._db_map_entity_class_lists[class_name]
        db_map, ent_cls = next(
            iter((db_map, ent_cls) for db_map, ent_cls in db_map_ent_cls_lst if db_map.codename == db_name)
        )
        self._spine_db_editor.start_connecting_entities(db_map, ent_cls, self)


class ArcItem(QGraphicsPathItem):
    """Connects a two EntityItems."""

    def __init__(self, ent_item, el_item, width):
        """Initializes item.

        Args:
            ent_item (spinetoolbox.widgets.graph_view_graphics_items.EntityItem): entity item
            el_item (spinetoolbox.widgets.graph_view_graphics_items.EntityItem): element item
            width (float): Preferred line width
        """
        super().__init__()
        self.ent_item = ent_item
        self.el_item = el_item
        self._width = float(width)
        self._pen = self._make_pen()
        self.setPen(self._pen)
        self.setZValue(-2)
        ent_item.add_arc_item(self)
        el_item.add_arc_item(self)
        self.setCursor(Qt.ArrowCursor)
        self.update_line()

    def _make_pen(self):
        pen = QPen()
        pen.setWidth(self._width)
        color = QGuiApplication.palette().color(QPalette.Normal, QPalette.WindowText)
        color.setAlphaF(0.8)
        pen.setColor(color)
        pen.setStyle(Qt.SolidLine)
        pen.setCapStyle(Qt.RoundCap)
        return pen

    def moveBy(self, dx, dy):
        """Does nothing. This item is not moved the regular way, but follows the EntityItems it connects."""

    def update_line(self):
        overlapping_arcs = [arc for arc in self.ent_item.arc_items if arc.el_item == self.el_item]
        count = len(overlapping_arcs)
        path = QPainterPath(self.ent_item.pos())
        if count == 1:
            path.lineTo(self.el_item.pos())
        else:
            rank = overlapping_arcs.index(self)
            line = QLineF(self.ent_item.pos(), self.el_item.pos())
            line.setP1(line.center())
            line = line.normalVector()
            line.setLength(self._width * count)
            line.setP1(2 * line.p1() - line.p2())
            t = rank / (count - 1)
            ctrl_point = line.pointAt(t)
            path.quadTo(ctrl_point, self.el_item.pos())
        self.setPath(path)

    def mousePressEvent(self, event):
        """Accepts the event so it's not propagated."""
        event.accept()

    def other_item(self, item):
        return {self.ent_item: self.el_item, self.el_item: self.ent_item}.get(item)

    def apply_zoom(self, factor):
        """Applies zoom.

        Args:
            factor (float): The zoom factor.
        """
        factor = max(factor, 1)
        scaled_width = self._width / factor
        self._pen.setWidthF(scaled_width)
        self.setPen(self._pen)


class CrossHairsItem(EntityItem):
    """Creates new relationships directly in the graph."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)
        self.setZValue(2)
        self._current_icon = None

    @property
    def entity_class_name(self):
        return None

    @property
    def entity_name(self):
        return None

    def _make_tool_tip(self):
        return "<p>Click on an object to add it to the relationship.</p>"

    def _do_update_name(self):
        return False

    def refresh_icon(self):
        renderer = self.db_mngr.get_icon_mngr(self.first_db_map).icon_renderer("\uf05b", 0)
        self._set_renderer(renderer)

    def set_plus_icon(self):
        self.set_icon("\uf067", Qt.blue)

    def set_check_icon(self):
        self.set_icon("\uf00c", Qt.green)

    def set_normal_icon(self):
        self.set_icon("\uf05b")

    def set_ban_icon(self):
        self.set_icon("\uf05e", Qt.red)

    def set_icon(self, unicode, color=0):
        """Refreshes the icon."""
        if (unicode, color) == self._current_icon:
            return
        renderer = self.db_mngr.get_icon_mngr(self.first_db_map).icon_renderer(unicode, color)
        self._set_renderer(renderer)
        self._current_icon = (unicode, color)

    def _snap(self, x, y):
        return (x, y)

    def mouseMoveEvent(self, event):
        delta = event.scenePos() - self.scenePos()
        self.move_by(delta.x(), delta.y())

    def contextMenuEvent(self, e):
        e.accept()


class CrossHairsEntityItem(EntityItem):
    """Represents the relationship that's being created using the CrossHairsItem."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)

    def _make_tool_tip(self):
        return None

    def _do_update_name(self):
        return False

    def _has_name(self):
        return True

    def refresh_icon(self):
        """Refreshes the icon."""
        el_items = [arc_item.el_item for arc_item in self.arc_items]
        dimension_name_list = tuple(
            el_item.entity_class_name for el_item in el_items if not isinstance(el_item, CrossHairsItem)
        )
        renderer = self.db_mngr.get_icon_mngr(self.first_db_map).multi_class_renderer(dimension_name_list)
        self._set_renderer(renderer)

    def contextMenuEvent(self, e):
        e.accept()


class CrossHairsArcItem(ArcItem):
    """Connects a CrossHairsEntityItem with the CrossHairsItem,
    and with all the EntityItem's in the relationship so far.
    """

    def _make_pen(self):
        pen = super()._make_pen()
        pen.setStyle(Qt.DotLine)
        color = pen.color()
        color.setAlphaF(0.5)
        pen.setColor(color)
        return pen


class EntityLabelItem(QGraphicsTextItem):
    """Provides a label for EntityItem."""

    entity_name_edited = Signal(str)

    def __init__(self, entity_item):
        """Initializes item.

        Args:
            entity_item (spinetoolbox.widgets.graph_view_graphics_items.EntityItem): The parent item.
        """
        super().__init__(entity_item)
        self.entity_item = entity_item
        self._font = QApplication.font()
        self._font.setPointSize(11)
        self.setFont(self._font)
        self.bg = QGraphicsRectItem(self)
        self.bg_color = QGuiApplication.palette().color(QPalette.Normal, QPalette.ToolTipBase)
        self.bg_color.setAlphaF(0.8)
        self.bg.setBrush(QBrush(self.bg_color))
        self.bg.setPen(Qt.NoPen)
        self.bg.setFlag(QGraphicsItem.ItemStacksBehindParent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, enabled=False)
        self.setAcceptHoverEvents(False)

    def boundingRect(self):
        if not self.isVisible():
            return QRectF()
        return super().boundingRect()

    def setPlainText(self, text):
        """Set texts and resets position.

        Args:
            text (str)
        """
        super().setPlainText(text)
        self.reset_position()

    def reset_position(self):
        """Adapts item geometry so text is always centered."""
        rectf = self.boundingRect()
        x = -rectf.width() / 2
        y = rectf.height() + 4
        self.setPos(x, y)
        self.bg.setRect(self.boundingRect())
