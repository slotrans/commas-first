import sublime
import sublime_plugin

import subprocess

# Design note:
#   Obviously commas-first is itself written in Python, and could be inlined here,
#   which would avoid the need for subprocess and the attendant overhead of executing
#   a new interpreter. I prefer not to depend on that fact, though. Running an outside
#   process isolates this plugin from all of the implementation details of commas-first
#   itself, and that is worth the (tiny) bit of overhead.

# TODO: should be a setting
COMMAND_PATH = "/path/to/commas-first.sh"


class CommasFirstFormatterCommand(sublime_plugin.TextCommand): # reference as "commas_first_formatter"
    def run(self, edit, mode):
        selection_regions = self.view.sel()

        for region in selection_regions:
            if region.empty():
                # nothing to do
                continue

            selected_text = self.view.substr(region)
            formatted_text = self.execute_formatter(selected_text, mode)
            self.view.replace(edit, region, formatted_text)

    def execute_formatter(self, input_text, mode):
        if mode == "TRIM_LEADING_WHITESPACE":
            cmd = [COMMAND_PATH, "--trim-leading-whitespace"]
        elif mode == "COMPACT_EXPRESSIONS":
            cmd = [COMMAND_PATH, "--compact-expressions"]
        else:
            cmd = [COMMAND_PATH]

        # note: ST plugins run in Python 3.3, subprocess was pretty different then...
        # docs https://docs.python.org/3.3/library/subprocess.html
        # also note you can opt in to Python 3.8 thusly https://www.sublimetext.com/docs/api_environments.html
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_b, stderr_b = process.communicate(input=input_text.encode("utf-8"))

        if process.returncode == 0:
            return stdout_b.decode("utf-8")
        else:
            return "".join([
                input_text,
                "\n",
                "/* CommasFirst returned {}, stderr follows:".format(process.returncode),
                stderr_b.decode("utf-8"),
                "*/",
            ])
