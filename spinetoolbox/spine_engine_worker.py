######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains SpineEngineWorker.

:authors: M. Marin (KTH)
:date:   14.10.2020
"""

import copy
from PySide2.QtCore import Signal, Slot, QObject, QThread
from PySide2.QtWidgets import QMessageBox
from spine_engine.spine_engine import ItemExecutionFinishState
from .spine_engine_manager import make_engine_manager
from .helpers import get_upgrade_db_promt_text


@Slot(list)
def _handle_dag_execution_started(project_items):
    for item in project_items:
        item.get_icon().execution_icon.mark_execution_waiting()


@Slot(object, object)
def _handle_node_execution_started(item, direction):
    icon = item.get_icon()
    if direction == "FORWARD":
        icon.execution_icon.mark_execution_started()
        if hasattr(icon, "animation_signaller"):
            icon.animation_signaller.animation_started.emit()


@Slot(object, object, object, object)
def _handle_node_execution_finished(item, direction, state, item_state):
    icon = item.get_icon()
    if direction == "FORWARD":
        icon.execution_icon.mark_execution_finished(item_state)
        if hasattr(icon, "animation_signaller"):
            icon.animation_signaller.animation_stopped.emit()
        if state == "RUNNING":
            excluded = item_state == ItemExecutionFinishState.EXCLUDED
            icon.run_execution_leave_animation(excluded)


@Slot(object, str, str)
def _handle_event_message_arrived(item, filter_id, msg_type, msg_text):
    item.add_event_message(filter_id, msg_type, msg_text)


@Slot(object, str, str)
def _handle_process_message_arrived(item, filter_id, msg_type, msg_text):
    item.add_process_message(filter_id, msg_type, msg_text)


@Slot(dict, object)
def _handle_prompt_arrived(prompt, engine_mngr):
    prompt_type = prompt["type"]
    if prompt_type == "upgrade_db":
        url = prompt["url"]
        current = prompt["current"]
        expected = prompt["expected"]
        text, info_text = get_upgrade_db_promt_text(url, current, expected)
    else:
        text = prompt["text"]
    item_name = prompt["item_name"]
    box_title = f"{item_name}"
    box = QMessageBox(
        QMessageBox.Question, box_title, text, buttons=QMessageBox.Yes | QMessageBox.No, parent=qApp.activeWindow()
    )
    if info_text:
        box.setInformativeText(info_text)
    answer = box.exec_()
    accepted = answer == QMessageBox.Yes
    engine_mngr.answer_prompt(item_name, accepted)


class SpineEngineWorker(QObject):

    finished = Signal()
    _dag_execution_started = Signal(list)
    _node_execution_started = Signal(object, object)
    _node_execution_finished = Signal(object, object, object, object)
    _event_message_arrived = Signal(object, str, str, str)
    _process_message_arrived = Signal(object, str, str, str)
    _prompt_arrived = Signal(dict, object)

    def __init__(self, engine_server_address, engine_data, dag, dag_identifier, project_items):
        """
        Args:
            engine_server_address (str): Address of engine server if any
            engine_data (dict): engine data
            dag (DirectedGraphHandler)
            dag_identifier (str)
            project_items (dict): mapping from project item name to :class:`ProjectItem`
        """
        super().__init__()
        self._engine_data = engine_data
        self._engine_mngr = make_engine_manager(engine_server_address)
        self.dag = dag
        self.dag_identifier = dag_identifier
        self._engine_final_state = "UNKNOWN"
        self._executing_items = []
        self._project_items = project_items
        self.event_messages = {}
        self.process_messages = {}
        self.successful_executions = []
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.do_work)

    @property
    def engine_data(self):
        """Engine data dictionary."""
        return self._engine_data

    def get_engine_data(self):
        """Returns the engine data. Together with ``self.set_engine_data()`` it can be used to modify
        the workflow after it's initially created. We use it at the moment for creating Julia sysimages.

        Returns:
            dict
        """
        return copy.deepcopy(self._engine_data)

    def set_engine_data(self, engine_data):
        """Sets the engine data.

        Args:
            engine_data (dict): New data
        """
        self._engine_data = engine_data

    @Slot(object, str, str)
    def _handle_event_message_arrived(self, item, filter_id, msg_type, msg_text):
        self.event_messages.setdefault(msg_type, []).append(msg_text)

    @Slot(object, str, str)
    def _handle_process_message_arrived(self, item, filter_id, msg_type, msg_text):
        self.process_messages.setdefault(msg_type, []).append(msg_text)

    def stop_engine(self):
        self._engine_mngr.stop_engine()

    def engine_final_state(self):
        return self._engine_final_state

    def thread(self):
        return self._thread

    def _connect_log_signals(self, silent):
        if silent:
            self._event_message_arrived.connect(self._handle_event_message_arrived)
            self._process_message_arrived.connect(self._handle_process_message_arrived)
            return
        self._dag_execution_started.connect(_handle_dag_execution_started)
        self._node_execution_started.connect(_handle_node_execution_started)
        self._node_execution_finished.connect(_handle_node_execution_finished)
        self._event_message_arrived.connect(_handle_event_message_arrived)
        self._process_message_arrived.connect(_handle_process_message_arrived)
        self._prompt_arrived.connect(_handle_prompt_arrived)

    def start(self, silent=False):
        """Connects log signals.

        Args:
            silent (bool, optional): If True, log messages are not forwarded to the loggers
                but saved in internal dicts.
        """
        self._connect_log_signals(silent)
        self._dag_execution_started.emit(list(self._project_items.values()))
        self._thread.start()

    @Slot()
    def do_work(self):
        """Does the work and emits finished when done."""
        self._engine_mngr.run_engine(self._engine_data)
        while True:
            event_type, data = self._engine_mngr.get_engine_event()
            self._process_event(event_type, data)
            if event_type == "dag_exec_finished":
                self._engine_final_state = data
                break
        self.finished.emit()

    def _process_event(self, event_type, data):
        handler = {
            "exec_started": self._handle_node_execution_started,
            "exec_finished": self._handle_node_execution_finished,
            "event_msg": self._handle_event_msg,
            "process_msg": self._handle_process_msg,
            "standard_execution_msg": self._handle_standard_execution_msg,
            "persistent_execution_msg": self._handle_persistent_execution_msg,
            "kernel_execution_msg": self._handle_kernel_execution_msg,
            "prompt": self._handle_prompt,
        }.get(event_type)
        if handler is None:
            return
        handler(data)

    def _handle_prompt(self, prompt):
        self._prompt_arrived.emit(prompt, self._engine_mngr)

    def _handle_standard_execution_msg(self, msg):
        item = self._project_items[msg["item_name"]]
        if msg["type"] == "execution_failed_to_start":
            msg_text = f"Program <b>{msg['program']}</b> failed to start: {msg['error']}"
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_error", msg_text)
        elif msg["type"] == "execution_started":
            self._event_message_arrived.emit(
                item, msg["filter_id"], "msg", f"\tStarting program <b>{msg['program']}</b>"
            )
            self._event_message_arrived.emit(item, msg["filter_id"], "msg", f"\tArguments: <b>{msg['args']}</b>")
            self._event_message_arrived.emit(
                item, msg["filter_id"], "msg_warning", "\tExecution is in progress. See messages below (stdout&stderr)"
            )

    def _handle_persistent_execution_msg(self, msg):
        item = self._project_items[msg["item_name"]]
        if msg["type"] == "persistent_started":
            item.persistent_console_requested.emit(msg["filter_id"], msg["key"], msg["language"])
        elif msg["type"] == "persistent_failed_to_start":
            msg_text = (
                f"\tUnable to start persistent process <b>{msg['args']}</b>: {msg['error']}."
                "Please go to Settings->Tools and check your setup."
            )
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_error", msg_text)
        elif msg["type"] == "stdin":
            item.persistent_stdin_available.emit(msg["filter_id"], msg["data"])
        elif msg["type"] == "stdout":
            item.persistent_stdout_available.emit(msg["filter_id"], msg["data"])
        elif msg["type"] == "stderr":
            item.persistent_stderr_available.emit(msg["filter_id"], msg["data"])
        elif msg["type"] == "execution_started":
            self._event_message_arrived.emit(
                item, msg["filter_id"], "msg", f"\tStarting execution on persistent process <b>{msg['args']}</b>"
            )
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_warning", "See Console for messages.")

    def _handle_kernel_execution_msg(self, msg):
        item = self._project_items[msg["item_name"]]
        if msg["type"] == "kernel_started":
            item.jupyter_console_requested.emit(msg["filter_id"], msg["kernel_name"], msg["connection_file"])
        elif msg["type"] == "kernel_spec_not_found":
            msg_text = (
                f"\tUnable to find specification for kernel <b>{msg['kernel_name']}</b>. "
                "Please go to Settings->Tools to select a valid kernel."
            )
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_error", msg_text)
        elif msg["type"] == "execution_failed_to_start":
            msg_text = f"\tExecution on kernel <b>{msg['kernel_name']}</b> failed to start: {msg['error']}"
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_error", msg_text)
        elif msg["type"] == "execution_started":
            self._event_message_arrived.emit(
                item, msg["filter_id"], "msg", f"\tStarting execution on kernel <b>{msg['kernel_name']}</b>"
            )
            self._event_message_arrived.emit(item, msg["filter_id"], "msg_warning", "See Console for messages.")

    def _handle_process_msg(self, data):
        self._do_handle_process_msg(**data)

    def _do_handle_process_msg(self, item_name, filter_id, msg_type, msg_text):
        item = self._project_items[item_name]
        self._process_message_arrived.emit(item, filter_id, msg_type, msg_text)

    def _handle_event_msg(self, data):
        self._do_handle_event_msg(**data)

    def _do_handle_event_msg(self, item_name, filter_id, msg_type, msg_text):
        item = self._project_items[item_name]
        self._event_message_arrived.emit(item, filter_id, msg_type, msg_text)

    def _handle_node_execution_started(self, data):
        self._do_handle_node_execution_started(**data)

    def _do_handle_node_execution_started(self, item_name, direction):
        """Starts item icon animation when executing forward."""
        item = self._project_items[item_name]
        self._executing_items.append(item)
        self._node_execution_started.emit(item, direction)

    def _handle_node_execution_finished(self, data):
        self._do_handle_node_execution_finished(**data)

    def _do_handle_node_execution_finished(self, item_name, direction, state, item_state):
        item = self._project_items[item_name]
        if item_state == ItemExecutionFinishState.SUCCESS:
            self.successful_executions.append((item, direction, state))
        self._executing_items.remove(item)
        self._node_execution_finished.emit(item, direction, state, item_state)

    def clean_up(self):
        for item in self._executing_items:
            self._node_execution_finished.emit(item, None, None, None)
        self._thread.quit()
        self._thread.wait()
        self._thread.deleteLater()
        self.deleteLater()
