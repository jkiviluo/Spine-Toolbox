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
Contains ToolInstance class.

:authors: P. Savolainen (VTT), E. Rinne (VTT)
:date:   1.2.2018
"""

import os
import sys
import shutil
from PySide2.QtCore import QObject, Signal, Slot
from . import qsubprocess
from .config import GAMS_EXECUTABLE, JULIA_EXECUTABLE, PYTHON_EXECUTABLE


class ToolInstance(QObject):
    """Class for Tool instances.

    Args:
        toolbox (ToolboxUI): QMainWindow instance
        tool_template (ToolTemplate): the tool template for this instance
        basedir (str): the path to the directory where this instance should run

    Class Variables:
        instance_finished_signal (Signal): Signal to emit when a Tool instance has finished processing
    """

    instance_finished_signal = Signal(int, name="instance_finished_signal")

    def __init__(self, toolbox, tool_template, basedir):
        """class constructor."""
        super().__init__()  # TODO: Should this be QObject.__init__(self) like in MetaObject class?
        self._toolbox = toolbox
        self.tool_template = tool_template
        self.basedir = basedir
        self.tool_process = None
        self.program = None  # Program to start in the subprocess
        self.args = list()  # List of command line arguments for the program

    def terminate_instance(self):
        """Terminates Tool instance execution."""
        if not self.tool_process:
            self._toolbox.project().execution_instance.project_item_execution_finished_signal.emit(-2)
            return
        # Disconnect tool_process signals
        try:
            self.tool_process.execution_finished_signal.disconnect()
        except AttributeError:
            pass
        try:
            self.tool_process.subprocess_finished_signal.disconnect()
        except AttributeError:
            pass
        self.tool_process.terminate_process()

    def remove(self):
        """[Obsolete] Removes Tool instance files from work directory."""
        shutil.rmtree(self.basedir, ignore_errors=True)

    def prepare(self):
        """Prepare this instance for execution.
        Implement in subclasses to perform specific initialization.
        """
        raise NotImplementedError

    def execute(self):
        """Execute this instance that must have been prepared prealably.
        Implement in subclasses.
        """
        raise NotImplementedError

    @Slot(int, name="handle_execution_finished")
    def handle_execution_finished(self, ret):
        """Handles execution finished.

        Args:
            ret (int)
        """
        raise NotImplementedError

    def append_cmdline_args(self):
        """Appends Tool template command line args into instance args list.

        Args:
            instance (ToolInstance)
        """
        self.args += self.tool_template.get_cmdline_args()


class GAMSToolInstance(ToolInstance):
    """Class for GAMS Tool instances.

    Args:
        toolbox (ToolboxUI): QMainWindow instance
        tool_template (ToolTemplate): the tool template for this instance
        basedir (str): the path to the directory where this instance should run
    """

    def prepare(self):
        """Prepare this instance for execution.
        """
        gams_path = self._toolbox.qsettings().value("appSettings/gamsPath", defaultValue="")
        if gams_path != '':
            gams_exe = gams_path
        else:
            gams_exe = GAMS_EXECUTABLE
        self.program = gams_exe
        self.args.append(self.tool_template.main_prgm)
        self.args.append("curDir=")
        self.args.append("{0}".format(self.basedir))
        self.args.append("logoption=3")  # TODO: This should be an option in Settings
        self.append_cmdline_args()  # Append Tool specific cmd line args into args list

    def execute(self):
        """Execute this instance that must have been prepared prealably.
        """
        self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
        self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
        # self.tool_process.start_process(workdir=os.path.split(self.program)[0])
        # TODO: Check if this sets the curDir argument. Is the curDir arg now useless?
        self.tool_process.start_process(workdir=self.basedir)

    @Slot(int, name="handle_execution_finished")
    def handle_execution_finished(self, ret):
        """Handles execution finished.

        Args:
            ret (int)
        """
        self.tool_process.subprocess_finished_signal.disconnect(self.handle_execution_finished)
        if self.tool_process.process_failed:  # process_failed should be True if ret != 0
            if self.tool_process.process_failed_to_start:
                self._toolbox.msg_error.emit(
                    "\t<b>{0}</b> failed to start. Make sure that "
                    "GAMS is installed properly on your computer "
                    "and GAMS directory is given in Settings (F1).".format(self.tool_process.program())
                )
            else:
                try:
                    return_msg = self.tool_template.return_codes[ret]
                    self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
                except KeyError:
                    self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:  # Return code 0: success
            self._toolbox.msg.emit("\tTool template execution finished")
        self.tool_process.deleteLater()
        self.tool_process = None
        self.instance_finished_signal.emit(ret)


class JuliaToolInstance(ToolInstance):
    """Class for Julia Tool instances.

    Args:
        toolbox (ToolboxUI): QMainWindow instance
        tool_template (ToolTemplate): the tool template for this instance
        basedir (str): the path to the directory where this instance should run
    """

    def __init__(self, toolbox, tool_template, basedir):
        super().__init__(toolbox, tool_template, basedir)
        self.julia_repl_command = None

    def prepare(self):
        """Prepare this instance for execution.
        """
        # Prepare command "julia --project={PROJECT_DIR} script.jl"
        # Do this regardless of the `useEmbeddedJulia` setting since we may need to fallback
        # to `julia --project={PROJECT_DIR} script.jl`
        julia_path = self._toolbox.qsettings().value("appSettings/juliaPath", defaultValue="")
        if julia_path != "":
            julia_exe = julia_path
        else:
            julia_exe = JULIA_EXECUTABLE
        julia_project_path = self._toolbox.qsettings().value("appSettings/juliaProjectPath", defaultValue="")
        if julia_project_path == "":
            julia_project_path = "@."
        work_dir = self.basedir
        script_path = os.path.join(work_dir, self.tool_template.main_prgm)
        self.program = julia_exe
        self.args.append(f"--project={julia_project_path}")
        self.args.append(script_path)
        self.append_cmdline_args()
        use_embedded_julia = self._toolbox.qsettings().value("appSettings/useEmbeddedJulia", defaultValue="2")
        if use_embedded_julia == "2":
            # Prepare Julia REPL command
            # TODO: See if this can be simplified
            mod_work_dir = work_dir.__repr__().strip("'")
            args = r'["' + r'", "'.join(self.tool_template.get_cmdline_args()) + r'"]'
            self.julia_repl_command = (
                r'cd("{}");'
                r'empty!(ARGS);'
                r'append!(ARGS, {});'
                r'include("{}")'.format(mod_work_dir, args, self.tool_template.main_prgm)
            )

    def execute(self):
        """Execute this instance that must have been prepared prealably.
        """
        if self._toolbox.qsettings().value("appSettings/useEmbeddedJulia", defaultValue="2") == "2":
            self.tool_process = self._toolbox.julia_repl
            self.tool_process.execution_finished_signal.connect(self.handle_repl_execution_finished)
            # self._toolbox.msg.emit("\tCommand:<b>{0}</b>".format(self.julia_repl_command))
            self.tool_process.execute_instance(self.julia_repl_command)
        else:
            self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
            self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
            # On Julia the Qprocess workdir must be set to the path where the main script is
            # Otherwise it doesn't find input files in subdirectories
            self.tool_process.start_process(workdir=self.basedir)

    @Slot(int, name="handle_repl_execution_finished")
    def handle_repl_execution_finished(self, ret):
        """Handles repl-execution finished.

        Args:
            ret (int): Tool specification process return value
        """
        if ret != 0:
            if self.tool_process.execution_failed_to_start:
                # TODO: This should be a choice given to the user. It's a bit confusing now.
                self._toolbox.msg.emit("")
                self._toolbox.msg_warning.emit("\tSpawning a new process for executing the Tool specification")
                self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
                self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
                self.tool_process.start_process(workdir=self.basedir)
                return
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
            except KeyError:
                self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:
            self._toolbox.msg.emit("\tTool specification execution finished")
        self.tool_process = None
        self.instance_finished_signal.emit(ret)

    @Slot(int, name="handle_execution_finished")
    def handle_execution_finished(self, ret):
        """Handles execution finished.

        Args:
            ret (int): Tool specification process return value
        """
        self.tool_process.subprocess_finished_signal.disconnect(self.handle_execution_finished)
        if self.tool_process.process_failed:  # process_failed should be True if ret != 0
            if self.tool_process.process_failed_to_start:
                self._toolbox.msg_error.emit(
                    "\t<b>{0}</b> failed to start. Make sure that "
                    "Julia is installed properly on your computer.".format(self.tool_process.program())
                )
            else:
                try:
                    return_msg = self.tool_specification.return_codes[ret]
                    self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
                except KeyError:
                    self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:  # Return code 0: success
            self._toolbox.msg.emit("\tTool specification execution finished")
        self.tool_process.deleteLater()
        self.tool_process = None
        self.instance_finished_signal.emit(ret)


class PythonToolInstance(ToolInstance):
    """Class for Python Tool instances.

    Args:
        toolbox (ToolboxUI): QMainWindow instance
        tool_template (ToolTemplate): the tool template for this instance
        basedir (str): the path to the directory where this instance should run
    """

    def __init__(self, toolbox, tool_template, basedir):
        super().__init__(toolbox, tool_template, basedir)
        self.ipython_command_list = list()

    def prepare(self):
        """Prepare this instance for execution.
        """
        # Prepare command "python script.py"
        python_path = self._toolbox.qsettings().value("appSettings/pythonPath", defaultValue="")
        if python_path != "":
            python_cmd = python_path
        else:
            python_cmd = PYTHON_EXECUTABLE
        work_dir = self.basedir
        script_path = os.path.join(work_dir, self.tool_template.main_prgm)
        self.program = python_cmd
        self.args.append(script_path)  # TODO: Why are we doing this?
        self.append_cmdline_args()
        use_embedded_python = self._toolbox.qsettings().value("appSettings/useEmbeddedPython", defaultValue="0")
        if use_embedded_python == "2":
            # Prepare a command list (FIFO queue) with two commands for Python Console
            # 1st cmd: Change current work directory
            # 2nd cmd: Run script with given args
            # Cast args in list to strings and combine them to a single string
            args = " ".join([str(x) for x in self.tool_template.get_cmdline_args()])
            cd_work_dir_cmd = "%cd -q {0} ".format(work_dir)  # -q: quiet
            run_script_cmd = "%run \"{0}\" {1}".format(self.tool_template.main_prgm, args)
            # Populate FIFO command queue
            self.ipython_command_list.append(cd_work_dir_cmd)
            self.ipython_command_list.append(run_script_cmd)

    def execute(self):
        """Execute this instance that must have been prepared prealably.
        """
        if self._toolbox.qsettings().value("appSettings/useEmbeddedPython", defaultValue="0") == "2":
            self.tool_process = self._toolbox.python_repl
            self.tool_process.execution_finished_signal.connect(self.handle_console_execution_finished)
            k_tuple = self.tool_process.python_kernel_name()
            if not k_tuple:
                self.handle_console_execution_finished(-999)
                return
            kern_name = k_tuple[0]
            kern_display_name = k_tuple[1]
            # Check if this kernel is already running
            if self.tool_process.kernel_manager and self.tool_process.kernel_name == kern_name:
                self.tool_process.execute_instance(self.ipython_command_list)
            else:
                # Append command to buffer and start executing when kernel is up and running
                self.tool_process.commands = self.ipython_command_list
                self.tool_process.launch_kernel(kern_name, kern_display_name)
        else:
            self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
            self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
            self.tool_process.start_process(workdir=self.basedir)

    @Slot(int, name="handle_console_execution_finished")
    def handle_console_execution_finished(self, ret):
        """Handles console-execution finished.

        Args:
            ret (int): Tool specification process return value
        """
        if ret != 0:
            if self.tool_process.execution_failed_to_start:
                # TODO: This should be a choice given to the user. It's a bit confusing now.
                self._toolbox.msg.emit("")
                self._toolbox.msg_warning.emit("\tSpawning a new process for executing the Tool specification")
                self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
                self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
                self.tool_process.start_process(workdir=self.basedir)
                return
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
            except KeyError:
                self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:
            self._toolbox.msg.emit("\tTool specification execution finished")
        self.tool_process = None
        self.instance_finished_signal.emit(ret)

    @Slot(int, name="handle_execution_finished")
    def handle_execution_finished(self, ret):
        """Handles execution finished.

        Args:
            ret (int): Tool specification process return value
        """
        self.tool_process.subprocess_finished_signal.disconnect(self.handle_execution_finished)
        if self.tool_process.process_failed:  # process_failed should be True if ret != 0
            if self.tool_process.process_failed_to_start:
                self._toolbox.msg_error.emit(
                    "\t<b>{0}</b> failed to start. Make sure that "
                    "Python is installed properly on your computer.".format(self.tool_process.program())
                )
            else:
                try:
                    return_msg = self.tool_specification.return_codes[ret]
                    self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
                except KeyError:
                    self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:  # Return code 0: success
            self._toolbox.msg.emit("\tTool specification execution finished")
        self.tool_process.deleteLater()
        self.tool_process = None
        self.instance_finished_signal.emit(ret)


class ExecutableToolInstance(ToolInstance):
    """Class for Executable Tool instances.

    Args:
        toolbox (ToolboxUI): QMainWindow instance
        tool_template (ToolTemplate): the tool template for this instance
        basedir (str): the path to the directory where this instance should run
    """

    def prepare(self):
        """Prepare this instance for execution.
        """
        batch_path = os.path.join(self.basedir, self.tool_template.main_prgm)
        if sys.platform != "win32":
            self.program = "sh"
            self.args.append(batch_path)
        else:
            self.program = batch_path
        self.append_cmdline_args()  # Append Tool specific cmd line args into args list

    def execute(self):
        """Execute this instance that must have been prepared prealably.
        """
        self.tool_process = qsubprocess.QSubProcess(self._toolbox, self.program, self.args)
        self.tool_process.subprocess_finished_signal.connect(self.handle_execution_finished)
        self.tool_process.start_process(workdir=self.basedir)

    @Slot(int, name="handle_execution_finished")
    def handle_execution_finished(self, ret):
        """Handles execution finished.

        Args:
            ret (int): Tool specification process return value
        """
        self.tool_process.subprocess_finished_signal.disconnect(self.handle_execution_finished)
        if self.tool_process.process_failed:  # process_failed should be True if ret != 0
            if self.tool_process.process_failed_to_start:
                self._toolbox.msg_error.emit("\t<b>{0}</b> failed to start.".format(self.tool_process.program()))
            else:
                try:
                    return_msg = self.tool_specification.return_codes[ret]
                    self._toolbox.msg_error.emit("\t<b>{0}</b> [exit code:{1}]".format(return_msg, ret))
                except KeyError:
                    self._toolbox.msg_error.emit("\tUnknown return code ({0})".format(ret))
        else:  # Return code 0: success
            self._toolbox.msg.emit("\tTool specification execution finished")
        self.tool_process.deleteLater()
        self.tool_process = None
        self.instance_finished_signal.emit(ret)
