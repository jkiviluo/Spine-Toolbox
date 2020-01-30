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
Contains Tool specification classes.

:authors: P. Savolainen (VTT), E. Rinne (VTT), M. Marin (KTH)
:date:   24.1.2018
"""

from collections import ChainMap
import logging
import os
import re
from collections import OrderedDict
from .metaobject import MetaObject
from .config import REQUIRED_KEYS, OPTIONAL_KEYS, LIST_REQUIRED_KEYS
from .tool_instance import GAMSToolInstance, JuliaToolInstance, PythonToolInstance, ExecutableToolInstance


class ToolSpecification(MetaObject):
    """Super class for all tool specifications."""

    def __init__(
        self,
        toolbox,
        name,
        tooltype,
        path,
        includes,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execute_in_work=True,
    ):
        """

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            name (str): Name of the tool
            tooltype (str): Type of Tool (e.g. Python, Julia, ..)
            path (str): Path to tool
            includes (list): List of files belonging to the tool specification (relative to 'path')
            description (str): Description of the Tool specification
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (str, optional): Tool command line arguments (read from tool definition file)
            execute_in_work (bool): Execute in work folder
        """
        super().__init__(name, description)
        self._toolbox = toolbox
        self.tooltype = tooltype
        if not os.path.exists(path):
            pass
        else:
            self.path = path
        self.includes = includes
        if cmdline_args is not None:
            if isinstance(cmdline_args, str):
                # Old project files may have the command line arguments as plain strings.
                self.cmdline_args = self.split_cmdline_args(cmdline_args)
            else:
                self.cmdline_args = cmdline_args
        else:
            self.cmdline_args = []
        self.inputfiles = set(inputfiles) if inputfiles else set()
        self.inputfiles_opt = set(inputfiles_opt) if inputfiles_opt else set()
        self.outputfiles = set(outputfiles) if outputfiles else set()
        self.return_codes = {}
        self.def_file_path = ''  # JSON tool definition file path
        self.execute_in_work = execute_in_work

    def set_return_code(self, code, description):
        """Sets a return code and an associated text description for the tool specification.

        Args:
            code (int): Return code
            description (str): Description
        """
        self.return_codes[code] = description

    def set_def_path(self, path):
        """Sets the file path for this tool specification.

        Args:
            path (str): Absolute path to the specification file.
        """
        self.def_file_path = path

    def get_def_path(self):
        """Returns tool specification file path."""
        return self.def_file_path

    @staticmethod
    def check_definition(ui, data):
        """Checks that a tool specification contains
        the required keys and that it is in correct format.

        Args:
            ui (ToolboxUI): QMainWindow instance
            data (dict): Tool specification

        Returns:
            Dictionary or None if there was a problem in the tool definition.
        """
        kwargs = dict()
        for p in REQUIRED_KEYS + OPTIONAL_KEYS:
            try:
                kwargs[p] = data[p]
            except KeyError:
                if p in REQUIRED_KEYS:
                    ui.msg_error.emit("Required keyword '{0}' missing".format(p))
                    return None
            # Check that some values are lists
            if p in LIST_REQUIRED_KEYS:
                try:
                    if not isinstance(data[p], list):
                        ui.msg_error.emit("Keyword '{0}' value must be a list".format(p))
                        return None
                except KeyError:
                    pass
        return kwargs

    def get_cmdline_args(self, optional_input_files, input_urls, output_urls):
        """
        Returns tool's command line args as list.

        Replaces special tags in arguments:

        - @@optional_inputs@@ expands to a space-separated list of Tool's optional input files
        - @@url:<Data Store name>@@ expands to the URL provided by a named data store
        - @@url_inputs@@ expands to a space-separated list of Tool's input database URLs
        - @@url_outputs@@ expands to a space-separated list of Tool's output database URLs

        Args:
            optional_input_files (list): a list of Tool's optional input file names
            input_urls (dict): a mapping from URL provider (input Data Store name) to URL string
            output_urls (dict): a mapping from URL provider (output Data Store name) to URL string
        Returns:
            list: a list of expanded command line arguments
        """

        def expand_list(arg, tag, things, expanded_args):
            preface, tag_found, postscript = arg.partition(tag)
            if tag_found:
                if things:
                    first_input_arg = preface + things[0]
                    expanded_args.append(first_input_arg)
                    expanded_args += things[1:]
                    expanded_args[-1] = expanded_args[-1] + postscript
                else:
                    expanded_args.append(preface + postscript)
                return True
            return False

        expanded_args = list()
        named_data_store_tag_fingerprint = re.compile("@@url:.+@@")
        all_urls = ChainMap(input_urls, output_urls)
        input_url_list = list(input_urls.values())
        output_url_list = list(output_urls.values())
        for arg in self.cmdline_args:
            if expand_list(arg, "@@optional_inputs@@", optional_input_files, expanded_args):
                continue
            if expand_list(arg, "@@url_inputs@@", input_url_list, expanded_args):
                continue
            if expand_list(arg, "@@url_outputs@@", output_url_list, expanded_args):
                continue
            match = named_data_store_tag_fingerprint.search(arg)
            if match:
                preface = arg[: match.start()]
                tag = match.group()
                postscript = arg[match.end() :]
                data_store_name = tag[6:-2]
                try:
                    url = all_urls[data_store_name]
                except KeyError:
                    raise RuntimeError(f"Cannot replace tag '{tag}' since '{data_store_name}' was not found.")
                expanded_args.append(preface + url + postscript)
            else:
                expanded_args.append(arg)
        return expanded_args

    def create_tool_instance(self, basedir):
        """Returns an instance of the tool specification configured to run in the given directory.
        Needs to be implemented in subclasses.

        Args:
            basedir (str): Path to directory where the instance will run
        """
        raise NotImplementedError

    @staticmethod
    def split_cmdline_args(arg_string):
        """
        Splits a string of command line into a list of tokens.

        Things in single ('') and double ("") quotes are kept as single tokens
        while the quotes themselves are stripped away.
        Thus, `--file="a long quoted 'file' name.txt` becomes ["--file=a long quoted 'file' name.txt"]

        Args:
            arg_string (str): command line arguments as a string
        Returns:
            list: a list of tokens
        """
        # The expandable tags may include whitespaces, particularly in Data Store names.
        # We replace the tags temporarily by '@@@' to simplify splitting
        # and put them back to the args list after the string has been split.
        tag_safe = list()
        tag_fingerprint = re.compile("@@url:.+?@@")
        match = tag_fingerprint.search(arg_string)
        while match:
            tag_safe.append(match.group())
            arg_string = arg_string[: match.start()] + "@@@" + arg_string[match.end() :]
            match = tag_fingerprint.search(arg_string)
        tokens = list()
        current_word = ""
        quoted_context = False
        for character in arg_string:
            if character in ("'", '"') and not quoted_context:
                quoted_context = character
            elif character == quoted_context:
                quoted_context = False
            elif not character.isspace() or quoted_context:
                current_word = current_word + character
            else:
                tokens.append(current_word)
                current_word = ""
        if current_word:
            tokens.append(current_word)
        for index, token in enumerate(tokens):
            preface, tag_token, prologue = token.partition("@@@")
            if tag_token:
                tokens[index] = preface + tag_safe.pop(0) + prologue
        return tokens


class GAMSTool(ToolSpecification):
    """Class for GAMS tool specifications."""

    def __init__(
        self,
        toolbox,
        name,
        tooltype,
        path,
        includes,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execute_in_work=True,
    ):
        """

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            name (str): GAMS Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path').  # TODO: Change to src_files
            First file in the list is the main GAMS program.
            description (str): GAMS Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (str, optional): GAMS tool command line arguments (read from tool definition file)
        """
        super().__init__(
            toolbox,
            name,
            tooltype,
            path,
            includes,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
            execute_in_work,
        )
        main_file = includes[0]
        # Add .lst file to list of output files
        self.lst_file = os.path.splitext(main_file)[0] + '.lst'
        self.outputfiles.add(self.lst_file)
        # Split main_prgm to main_dir and main_prgm
        # because GAMS needs to run in the directory of the main program
        # TODO: This does not work because main_file is always just file name
        self.main_dir, self.main_prgm = os.path.split(main_file)
        self.gams_options = OrderedDict()
        self.return_codes = {
            0: "Normal return",
            1: "Solver is to be called the system should never return this number",  # ??
            2: "There was a compilation error",
            3: "There was an execution error",
            4: "System limits were reached",
            5: "There was a file error",
            6: "There was a parameter error",
            7: "There was a licensing error",
            8: "There was a GAMS system error",
            9: "GAMS could not be started",
            10: "Out of memory",
            11: "Out of disk",
            62097: "Simulation interrupted by user",  # Not official
        }

    def __repr__(self):
        """[OBSOLETE]. Returns instance of this class as a string."""
        return "GAMSTool('{}')".format(self.name)

    def update_gams_options(self, key, value):
        """[OBSOLETE?] Updates GAMS command line options. Only 'cerr and 'logoption' keywords supported.

        Args:
            key (str): Option name
            value (int, float): Option value
        """
        # Supported GAMS logoption values
        # 3 writes LOG output to standard output
        # 4 writes LOG output to a file and standard output  [Not supported in GAMS v24.0]
        if key in ['logoption', 'cerr']:
            self.gams_options[key] = "{0}={1}".format(key, value)
        else:
            logging.error("Updating GAMS options failed. Unknown key: %s", key)

    @staticmethod
    def load(toolbox, path, data):
        """Creates a GAMSTool according to a tool specification file.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions

        Returns:
            GAMSTool instance or None if there was a problem in the tool specification file.
        """
        kwargs = GAMSTool.check_definition(toolbox, data)
        if kwargs is not None:
            # Return an executable model instance
            return GAMSTool(toolbox=toolbox, path=path, **kwargs)
        return None

    def create_tool_instance(self, basedir):
        """Returns an instance of this tool specification that is configured to run in the given directory.

        Args:
            basedir (str): the path to the directory where the instance will run
        """
        return GAMSToolInstance(self._toolbox, self, basedir)


class JuliaTool(ToolSpecification):
    """Class for Julia tool specifications."""

    def __init__(
        self,
        toolbox,
        name,
        tooltype,
        path,
        includes,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execute_in_work=True,
    ):
        """
        Args:

            toolbox (ToolboxUI): QMainWindow instance
            name (str): Julia Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path').  # TODO: Change to src_files
            First file in the list is the main Julia program.
            description (str): Julia Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (str, optional): Julia tool command line arguments (read from tool definition file)
        """
        super().__init__(
            toolbox,
            name,
            tooltype,
            path,
            includes,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
            execute_in_work,
        )
        main_file = includes[0]
        self.main_dir, self.main_prgm = os.path.split(main_file)
        self.julia_options = OrderedDict()
        self.return_codes = {0: "Normal return"}  # Not official

    def __repr__(self):
        """[OBSOLETE]. Returns instance of this class as a string."""
        return "JuliaTool('{}')".format(self.name)

    def update_julia_options(self, key, value):
        """[OBSOLETE?] Updates Julia command line options.

        Args:
            key (str): Option name
            value (int, float): Option value
        """

    @staticmethod
    def load(toolbox, path, data):
        """Creates a JuliaTool according to a tool specification file.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions

        Returns:
            JuliaTool instance or None if there was a problem in the tool definition file.
        """
        kwargs = JuliaTool.check_definition(toolbox, data)
        if kwargs is not None:
            # Return an executable model instance
            return JuliaTool(toolbox=toolbox, path=path, **kwargs)
        return None

    def create_tool_instance(self, basedir):
        """Returns an instance of this tool specification that is configured to run in the given directory.

        Args:
            basedir (str): the path to the directory where the instance will run
        """
        return JuliaToolInstance(self._toolbox, self, basedir)


class PythonTool(ToolSpecification):
    """Class for Python tool specifications."""

    def __init__(
        self,
        toolbox,
        name,
        tooltype,
        path,
        includes,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execute_in_work=True,
    ):
        """
        Args:

            toolbox (ToolboxUI): QMainWindow instance
            name (str): Python Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path').  # TODO: Change to src_files
            First file in the list is the main Python program.
            description (str): Python Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (str, optional): Python tool command line arguments (read from tool definition file)
        """
        super().__init__(
            toolbox,
            name,
            tooltype,
            path,
            includes,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
            execute_in_work,
        )
        main_file = includes[0]
        self.main_dir, self.main_prgm = os.path.split(main_file)
        self.python_options = OrderedDict()
        self.return_codes = {0: "Normal return"}  # Not official

    def __repr__(self):
        """[OBSOLETE]. Returns instance of this class as a string."""
        return "PythonTool('{}')".format(self.name)

    def update_python_options(self, key, value):
        """[OBSOLETE?] Updates Python command line options.

        Args:
            key (str): Option name
            value (int, float): Option value
        """

    @staticmethod
    def load(toolbox, path, data):
        """Creates a PythonTool according to a tool specification file.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions

        Returns:
            PythonTool instance or None if there was a problem in the tool definition file.
        """
        kwargs = PythonTool.check_definition(toolbox, data)
        if kwargs is not None:
            # Return an executable model instance
            return PythonTool(toolbox=toolbox, path=path, **kwargs)
        return None

    def create_tool_instance(self, basedir):
        """Returns an instance of this tool specification that is configured to run in the given directory.

        Args:
            basedir (str): the path to the directory where the instance will run
        """
        return PythonToolInstance(self._toolbox, self, basedir)


class ExecutableTool(ToolSpecification):
    """Class for Executable tool specifications."""

    def __init__(
        self,
        toolbox,
        name,
        tooltype,
        path,
        includes,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execute_in_work=True,
    ):
        """
        Args:

            toolbox (ToolboxUI): QMainWindow instance
            name (str): Tool name
            tooltype (str): Tool specification type
            path (str): Path to main script file
            includes (list): List of files belonging to the tool (relative to 'path').  # TODO: Change to src_files
            First file in the list is the main script file.
            description (str): Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (str, optional): Tool command line arguments (read from tool definition file)
        """
        super().__init__(
            toolbox,
            name,
            tooltype,
            path,
            includes,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
            execute_in_work,
        )
        main_file = includes[0]
        # TODO: This does not do anything because main_file is always just file name
        self.main_dir, self.main_prgm = os.path.split(main_file)
        self.options = OrderedDict()
        self.return_codes = {0: "Normal exit", 1: "Error happened"}

    def __repr__(self):
        """[OBSOLETE]. Returns instance of this class as a string."""
        return "ExecutableTool('{}')".format(self.name)

    @staticmethod
    def load(toolbox, path, data):
        """Creates an ExecutableTool according to a tool specification file.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            path (str): Base path to tool files
            data (dict): Tool specification

        Returns:
            ExecutableTool instance or None if there was a problem in the tool specification.
        """
        kwargs = ExecutableTool.check_definition(toolbox, data)
        if kwargs is not None:
            # Return an executable model instance
            return ExecutableTool(toolbox=toolbox, path=path, **kwargs)
        return None

    def create_tool_instance(self, basedir):
        """Returns an instance of this tool specification that is configured to run in the given directory.

        Args:
            basedir (str): the path to the directory where the instance will run
        """
        return ExecutableToolInstance(self._toolbox, self, basedir)
