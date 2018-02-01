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
Spine Toolbox project class.

:authors: Pekka Savolainen <pekka.t.savolainen@vtt.fi>, Erkka Rinne <erkka.rinne@vtt.fi>
:date:   10.1.2018
"""

import os
import logging
import json
from PySide2.QtCore import Qt
from metaobject import MetaObject
from helpers import project_dir
from data_store import DataStore
from data_connection import DataConnection
from tool import Tool
from view import View
from tool_candidates import GAMSTool


class SpineToolboxProject(MetaObject):
    """Class for Spine Toolbox projects."""

    def __init__(self, parent, name, description, configs, ext='.proj'):
        """Class constructor.

        Args:
            parent (ToolboxUI): Parent of this project
            name (str): Project name
            description (str): Project description
            ext (str): Project save file extension (.proj)
        """
        super().__init__(name, description)
        self._parent = parent
        self._configs = configs
        self.project_dir = os.path.join(project_dir(self._configs), self.short_name)
        self.filename = self.short_name + ext
        self.path = os.path.join(project_dir(self._configs), self.filename)
        self.dirty = False  # TODO: Indicates if project has changed since loading
        self.project_contents = dict()
        if not os.path.exists(self.project_dir):
            try:
                os.makedirs(self.project_dir, exist_ok=True)
            except OSError:
                logging.error("Could not create project directory: {0}".format(self.project_dir))
        else:
            # TODO: Notice that project already exists...
            pass

    def set_name(self, name):
        """Change project name. Calls superclass method.

        Args:
            name (str): Project name
        """
        super().set_name(name)

    def set_description(self, desc):
        """Change project description. Calls superclass method.

        Args:
            desc (str): Project description
        """
        super().set_description(desc)

    def change_filename(self, new_filename):
        """Change the save filename associated with this project.

        Args:
            new_filename (str): Filename used in saving the project. No full path. Example 'project.proj'
        """
        # TODO: Add check that file extension is supported (.proj)
        self.filename = new_filename
        self.path = os.path.join(project_dir(self._configs), self.filename)

    def save(self, tool_def_paths):
        """Collect project information and objects
        into a dictionary and write to a JSON file.

        Args:
            tool_def_paths (list): List of paths to tool definition files
        """
        # Clear dictionary
        saved_dict = dict()  # This is written to JSON file
        project_dict = dict()  # Dictionary for storing project info
        project_dict['name'] = self.name
        project_dict['description'] = self.description
        project_dict['tool_candidates'] = tool_def_paths
        item_dict = dict()  # Dictionary for storing project items
        n = 0
        # Traverse all items in project model
        top_level_items = self._parent.project_item_model.findItems('*', Qt.MatchWildcard, column=0)
        for top_level_item in top_level_items:
            top_level_item_txt = top_level_item.data(Qt.DisplayRole)
            # logging.debug("Children of {0}".format(top_level_item.data(Qt.DisplayRole)))
            item_dict[top_level_item_txt] = dict()
            if top_level_item.hasChildren():
                n_children = top_level_item.rowCount()
                for i in range(n_children):
                    n += 1
                    child = top_level_item.child(i, 0)
                    child_data = child.data(Qt.UserRole)
                    name = child_data.name
                    # logging.debug("{0}".format(child.data(Qt.DisplayRole)))
                    item_dict[top_level_item_txt][name] = dict()
                    item_dict[top_level_item_txt][name]["short name"] = child_data.short_name
                    item_dict[top_level_item_txt][name]["description"] = child_data.description
                    if child_data.item_type == "Tool":
                        if not child_data.tool():  # TODO: Make Tool getter method
                            item_dict[top_level_item_txt][name]["tool"] = ""
                        else:
                            item_dict[top_level_item_txt][name]["tool"] = child_data.tool().name
                    else:
                        item_dict[top_level_item_txt][name]["data"] = child_data.get_data()
        # Save project stuff
        saved_dict['project'] = project_dict
        saved_dict['objects'] = item_dict
        # Write into JSON file
        with open(self.path, 'w') as fp:
            json.dump(saved_dict, fp, indent=4)
        logging.debug("{0} items saved".format(n))

    def load(self, item_dict):
        """Populate project item model with items loaded from project file.

        Args:
            item_dict (dict): Dictionary containing all project items in JSON format

        Returns:
            Boolean value depending on operation success.
        """
        data_stores = item_dict['Data Stores']
        data_connections = item_dict['Data Connections']
        tools = item_dict['Tools']
        views = item_dict['Views']
        n = len(data_stores.keys()) + len(data_connections.keys()) + len(tools.keys()) + len(views.keys())
        self._parent.msg.emit("Project contains {0} items".format(n))
        # Recreate Data Stores
        for name in data_stores.keys():
            short_name = data_stores[name]['short name']
            desc = data_stores[name]['description']
            data = data_stores[name]['data']
            # logging.debug("{} - {} '{}' data:{}".format(name, short_name, desc, data))
            data_store = DataStore(name, desc, self)
            data_store.set_data(data)
            # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
            ds_sw = self._parent.ui.mdiArea.addSubWindow(data_store.get_widget(), Qt.SubWindow)
            self._parent.project_refs.append(data_store)  # Save reference or signals don't stick
            self._parent.add_item_to_model("Data Stores", name, data_store)
            ds_sw.show()
        # Recreate Data Connections
        for name in data_connections.keys():
            short_name = data_connections[name]['short name']
            desc = data_connections[name]['description']
            data = data_connections[name]['data']
            # logging.debug("{} - {} '{}' data:{}".format(name, short_name, desc, data))
            data_connection = DataConnection(name, desc, self)
            data_connection.set_data(data)
            # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
            dc_sw = self._parent.ui.mdiArea.addSubWindow(data_connection.get_widget(), Qt.SubWindow)
            self._parent.project_refs.append(data_connection)  # Save reference or signals don't stick
            self._parent.add_item_to_model("Data Connections", name, data_connection)
            dc_sw.show()
        # Recreate Tools
        for name in tools.keys():
            short_name = tools[name]['short name']
            desc = tools[name]['description']
            tool_name = tools[name]['tool']
            # Find tool candidate from model
            tool_candidate = self._parent.tool_candidate_model.find_tool(tool_name)
            # Clarifications for user
            if not tool_name == "" and not tool_candidate:
                self._parent.msg_error.emit("Tool <b>{0}</b> should have a Tool candidate <b>{1}</b> but "
                                            "it was not found. Add it to Tool candidates and reopen "
                                            "project.".format(name, tool_name))
            tool = Tool(name, desc, self, tool_candidate)  # Can handle None as well
            # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
            tool_sw = self._parent.ui.mdiArea.addSubWindow(tool.get_widget(), Qt.SubWindow)
            self._parent.project_refs.append(tool)  # Save reference or signals don't stick
            self._parent.add_item_to_model("Tools", name, tool)
            tool_sw.show()
        # Recreate Views
        for name in views.keys():
            short_name = views[name]['short name']
            desc = views[name]['description']
            data = views[name]['data']
            # logging.debug("{} - {} '{}' data:{}".format(name, short_name, desc, data))
            view = View(name, desc, self)
            view.set_data(data)
            # Add QWidget -> QMdiSubWindow -> QMdiArea. Returns the added QMdiSubWindow
            view_sw = self._parent.ui.mdiArea.addSubWindow(view.get_widget(), Qt.SubWindow)
            self._parent.project_refs.append(view)  # Save reference or signals don't stick
            self._parent.add_item_to_model("Views", name, view)
            view_sw.show()
        return True

    def load_tool(self, jsonfile):
        """Create a Tool candidate according to a tool definition file.

        Args:
            jsonfile (str): Path of the tool definition file

        Returns:
            Instance of a subclass if Tool
        """
        try:
            with open(jsonfile, 'r') as fp:
                try:
                    definition = json.load(fp)
                except ValueError:
                    self._parent.msg_error.emit("Tool definition file not valid")
                    logging.exception("Loading JSON data failed")
                    return None
        except FileNotFoundError:
            self._parent.msg_error.emit("Tool definition file <b>{0}</b> not found".format(jsonfile))
            return None
        try:
            _type = definition['type'].lower()
        except KeyError:
            self._parent.msg_error.emit("No type of tool defined in tool definition file. Should be "
                                        "GAMS, Julia or executable")
            return None
        # Infer path from JSON file. This assumes that main model file is in the same directory as the tool definition file
        path = os.path.dirname(jsonfile)  # TODO: Is this needed?
        if _type == "gams":
            # self._parent.msg_warning.emit("GAMS tools not supported yet. path:{0} jsonfile:{1}".format(path, jsonfile))
            return GAMSTool.load(self._parent, path, definition)
        elif _type == "julia":
            self._parent.msg_warning.emit("Julia tools not supported yet")
            return None
        #     return JuliaTool.load(path, definition, self._parent)
        elif _type == 'executable':
            self._parent.msg_warning.emit("Executable tools not supported yet")
            return None
        #     return ExecutableTool.load(path, definition, self._parent)  # Get rid of self._parent
        else:
            self._parent.msg_warning.emit("Tool type <b>{}</b> not available".format(_type))
            return None
