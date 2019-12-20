######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Exporter project item.

:author: A. Soininen (VTT)
:date:   5.9.2019
"""

from copy import deepcopy
import logging
import pathlib
import os.path
from PySide2.QtCore import QObject, Signal, Slot
from spinedb_api.database_mapping import DatabaseMapping
from spinetoolbox.project_item import ProjectItem, ProjectItemResource
from spinetoolbox.spine_io import gdx_utils
from spinetoolbox.spine_io.exporters import gdx
from .settings_state import SettingsState
from .widgets.gdx_export_settings import GdxExportSettings
from .widgets.export_list_item import ExportListItem
from .worker import Worker


class Exporter(ProjectItem):
    """
    This project item handles all functionality regarding exporting a database to a file.

    Currently, only .gdx format is supported.
    """

    _missing_output_file_notification = (
        "Output file name(s) missing. See the settings in the Exporter Properties panel."
    )

    def __init__(self, toolbox, name, description, settings_packs, x=0.0, y=0.0):
        """
        Args:
            toolbox (ToolboxUI): a ToolboxUI instance
            name (str): item name
            description (str): item description
            settings_packs (list): dicts mapping database URL to _SettingsPack objects
            x (float): initial X coordinate of item icon
            y (float): initial Y coordinate of item icon
        """
        super().__init__(toolbox, name, description, x, y)
        self._settings_packs = dict()
        self._workers = dict()
        if settings_packs is None:
            settings_packs = list()
        for pack in settings_packs:
            url = pack["database_url"]
            settings_pack = _SettingsPack.from_dict(pack, url)
            self._settings_packs[url] = settings_pack
        self._activated = False
        self._project.db_mngr.session_committed.connect(self._update_settings_after_db_commit)

    @staticmethod
    def item_type():
        """See base class."""
        return "Exporter"

    @staticmethod
    def category():
        """See base class."""
        return "Exporters"

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers."""
        s = {self._properties_ui.open_directory_button.clicked: self.open_directory}
        return s

    def activate(self):
        """Restores selections and connects signals."""
        self._properties_ui.item_name_label.setText(self.name)
        self._update_properties_tab()
        super().connect_signals()
        self._activated = True

    def deactivate(self):
        """Saves selections and disconnects signals."""
        if not super().disconnect_signals():
            logging.error("Item %s deactivation failed.", self.name)
            return False
        self._activated = False
        return True

    def _update_properties_tab(self):
        """Updates the database list in the properties tab."""
        database_list_storage = self._properties_ui.databases_list_layout
        while not database_list_storage.isEmpty():
            widget_to_remove = database_list_storage.takeAt(0)
            widget_to_remove.widget().deleteLater()
        for url, pack in self._settings_packs.items():
            item = ExportListItem(url, pack.output_file_name, pack.state)
            database_list_storage.addWidget(item)
            item.open_settings_clicked.connect(self._show_settings)
            item.file_name_changed.connect(self._update_out_file_name)
            pack.state_changed.connect(item.settings_state_changed)

    def execute_forward(self, resources):
        """See base class."""
        database_urls = [r.url for r in resources if r.type_ == "database"]
        gams_system_directory = self._resolve_gams_system_directory()
        if gams_system_directory is None:
            self._toolbox.msg_error.emit("<b>{}</b>: Cannot proceed. No GAMS installation found.".format(self.name))
            return False
        for url in database_urls:
            settings_pack = self._settings_packs.get(url, None)
            if settings_pack is None:
                self._toolbox.msg_error.emit(f"<b>{self.name}</b>: No export settings defined for database {url}.")
                return False
            if not settings_pack.output_file_name:
                self._toolbox.msg_error.emit(
                    "<b>{}</b>: No file name given to export database {}.".format(self.name, url)
                )
                return False
            if settings_pack.state == SettingsState.FETCHING:
                self._toolbox.msg_error.emit(f"<b>{self.name}</b>: Settings not ready for database {url}.")
                return False
            out_path = os.path.join(self.data_dir, settings_pack.output_file_name)
            database_map = DatabaseMapping(url)
            try:
                gdx.to_gdx_file(
                    database_map,
                    out_path,
                    settings_pack.additional_domains,
                    settings_pack.settings,
                    settings_pack.indexing_settings,
                    gams_system_directory,
                )
            except gdx.GdxExportException as error:
                self._toolbox.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
                return False
            finally:
                database_map.connection.close()
            self._toolbox.msg_success.emit("File <b>{0}</b> written".format(out_path))
        return True

    def _do_handle_dag_changed(self, resources):
        """See base class."""
        database_urls = [r.url for r in resources if r.type_ == "database"]
        self._check_state(clear_before_check=False)
        if set(database_urls) == set(self._settings_packs.keys()):
            return
        # Drop settings packs without connected databases.
        for database_url, pack in self._settings_packs.items():
            if database_url not in database_urls:
                if pack.settings_window is not None:
                    pack.settings_window.close()
                    pack.settings_window.deleteLater()
                del self._settings_packs[database_url]
        # Add new databases.
        for database_url in database_urls:
            if database_url not in self._settings_packs:
                self._settings_packs[database_url] = _SettingsPack("")
                self._start_worker(database_url)
        if self._activated:
            self._update_properties_tab()

    def _start_worker(self, database_url):
        worker = self._workers.get(database_url, None)
        if worker is not None and worker.isRunning():
            worker.requestInterruption()
            worker.wait()
        elif worker is None:
            worker = Worker(database_url)
            worker.settings_read.connect(self._update_export_settings)
            worker.indexing_settings_read.connect(self._update_indexing_settings)
            worker.finished.connect(self._worker_finished)
            self._workers[database_url] = worker
        self._settings_packs[database_url].state = SettingsState.FETCHING
        worker.start()

    @Slot(str, "QVariant")
    def _update_export_settings(self, database_url, settings):
        if database_url not in self._settings_packs:
            return
        self._settings_packs[database_url].settings = settings

    @Slot(str, "QVariant")
    def _update_indexing_settings(self, database_url, indexing_settings):
        if database_url not in self._settings_packs:
            return
        self._settings_packs[database_url].indexing_settings = indexing_settings

    @Slot(str)
    def _worker_finished(self, database_url):
        if database_url in self._workers:
            worker = self._workers[database_url]
            worker.wait()
            worker.deleteLater()
            del self._workers[database_url]
            if database_url in self._settings_packs:
                settings_pack = self._settings_packs[database_url]
                if settings_pack.settings_window is not None:
                    self._send_settings_to_window(database_url)
                settings_pack.state = SettingsState.OK
            self._check_state()

    def _check_state(self, clear_before_check=True):
        if clear_before_check:
            self.clear_notifications()
        self._check_missing_file_names()
        self._check_missing_parameter_indexing()

    def _check_missing_file_names(self):
        for pack in self._settings_packs.values():
            if not pack.output_file_name:
                self.add_notification(Exporter._missing_output_file_notification)
                break

    def _check_missing_parameter_indexing(self):
        notification_added = False
        for pack in self._settings_packs.values():
            if pack.state != SettingsState.FETCHING:
                pack.state = SettingsState.OK
                for setting in pack.indexing_settings.values():
                    if setting.indexing_domain is None:
                        if not notification_added:
                            self.add_notification("Parameter indexing settings need to be updated.")
                        pack.state = SettingsState.INDEXING_PROBLEM
                        break

    @Slot(str)
    def _show_settings(self, database_url):
        """Opens the item's settings window."""
        settings_pack = self._settings_packs[database_url]
        if settings_pack.state == SettingsState.FETCHING:
            return
        # Give window its own settings and indexing domains so Cancel doesn't change anything here.
        settings = deepcopy(settings_pack.settings)
        indexing_settings = deepcopy(settings_pack.indexing_settings)
        additional_parameter_indexing_domains = list(settings_pack.additional_domains)
        if settings_pack.settings_window is None:
            settings_pack.settings_window = GdxExportSettings(
                settings, indexing_settings, additional_parameter_indexing_domains, database_url, self._toolbox
            )
            settings_pack.settings_window.settings_accepted.connect(self._update_settings_from_settings_window)
            settings_pack.settings_window.settings_rejected.connect(self._dispose_settings_window)
            settings_pack.settings_window.reset_requested.connect(self._reset_settings_window)
            settings_pack.state_changed.connect(settings_pack.settings_window.settings_state_changed)
        settings_pack.settings_window.show()

    @Slot(str)
    def _reset_settings_window(self, database_url):
        """Sends new settings to Gdx Export Settings window."""
        self._start_worker(database_url)

    @Slot(str)
    def _dispose_settings_window(self, database_url):
        """Deletes rejected export settings windows."""
        self._settings_packs[database_url].settings_window = None

    @Slot(str, str)
    def _update_out_file_name(self, file_name, database_path):
        """Updates the output file name for given database"""
        self._settings_packs[database_path].output_file_name = file_name
        self._check_state()

    @Slot(str)
    def _update_settings_from_settings_window(self, database_path):
        """Updates the export settings for given database from the settings window."""
        settings_pack = self._settings_packs[database_path]
        settings_pack.settings = settings_pack.settings_window.settings
        settings_pack.indexing_settings = settings_pack.settings_window.indexing_settings
        settings_pack.additional_domains = settings_pack.settings_window.new_domains
        self._check_state()

    def item_dict(self):
        """Returns a dictionary corresponding to this item's configuration."""
        d = super().item_dict()
        packs = list()
        for url, pack in self._settings_packs.items():
            pack_dict = pack.to_dict()
            pack_dict["database_url"] = url
            packs.append(pack_dict)
        d["settings_packs"] = packs
        return d

    def _send_settings_to_window(self, database_url):
        """Resets settings in given export settings window."""
        settings_pack = self._settings_packs[database_url]
        window = settings_pack.settings_window
        settings = deepcopy(settings_pack.settings)
        indexing_settings = deepcopy(settings_pack.indexing_settings)
        additional_parameter_indexing_domains = list(settings_pack.additional_domains)
        window.reset_settings(settings, indexing_settings, additional_parameter_indexing_domains)

    def update_name_label(self):
        """See `ProjectItem.update_name_label()`."""
        self._properties_ui.item_name_label.setText(self.name)

    def _resolve_gams_system_directory(self):
        """Returns GAMS system path from Toolbox settings or None if GAMS default is to be used."""
        path = self._toolbox.qsettings().value("appSettings/gamsPath", defaultValue=None)
        if not path:
            path = gdx_utils.find_gams_directory()
        if path is not None and os.path.isfile(path):
            path = os.path.dirname(path)
        return path

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._toolbox.msg.emit(
                "Link established. Data Store <b>{0}</b> will be "
                "exported to a .gdx file by <b>{1}</b> when executing.".format(source_item.name, self.name)
            )
        else:
            super().notify_destination(source_item)

    @Slot("QVariant")
    def _update_settings_after_db_commit(self, committed_db_maps):
        """Refreshes export settings for databases after data has been committed to them."""
        for db_map in committed_db_maps:
            url = str(db_map.db_url)
            if url in self._settings_packs:
                self._start_worker(url)

    @staticmethod
    def default_name_prefix():
        """See base class."""
        return "Exporter"

    def output_resources_forward(self):
        """See base class."""
        files = [pack.output_file_name for pack in self._settings_packs.values()]
        paths = [os.path.join(self.data_dir, file_name) for file_name in files]
        resources = [ProjectItemResource(self, "file", url=pathlib.Path(path).as_uri()) for path in paths]
        return resources

    def tear_down(self):
        """See base class."""
        self._project.db_mngr.session_committed.disconnect(self._update_settings_after_db_commit)


class _SettingsPack(QObject):

    state_changed = Signal("QVariant")

    def __init__(self, output_file_name):
        super().__init__()
        self.output_file_name = output_file_name
        self.settings = None
        self.indexing_settings = None
        self.additional_domains = list()
        self.settings_window = None
        self._state = SettingsState.FETCHING

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self.state_changed.emit(state)

    def to_dict(self):
        d = dict()
        d["output_file_name"] = self.output_file_name
        d["state"] = self.state.value
        if self.state == SettingsState.FETCHING:
            return d
        d["settings"] = self.settings.to_dict()
        d["indexing_settings"] = gdx.indexing_settings_to_dict(self.indexing_settings)
        d["additional_domains"] = [domain.to_dict() for domain in self.additional_domains]
        return d

    @staticmethod
    def from_dict(pack_dict, database_url):
        pack = _SettingsPack(pack_dict["output_file_name"])
        pack.state = SettingsState(pack_dict["state"])
        if pack.state == SettingsState.FETCHING:
            return pack
        pack.settings = gdx.Settings.from_dict(pack_dict["settings"])
        db_map = DatabaseMapping(database_url)
        pack.indexing_settings = gdx.indexing_settings_from_dict(pack_dict["indexing_settings"], db_map)
        db_map.connection.close()
        pack.additional_domains = [gdx.Set.from_dict(set_dict) for set_dict in pack_dict["additional_domains"]]
        return pack
