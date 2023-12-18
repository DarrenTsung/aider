import os

from pathlib import Path
from aider import utils

class InChatFiles:
    def __init__(self, additional_lines_around_mentioned_line_number=10):
        # Dictionary of absolute_file_names to ranges to send as part of the context.
        #
        # For example: {"/user/aider/main.py": [(2, 10), (15, 20)]} would
        # mean that we should send lines 2-10 (inclusive) and 15-20 of aider/main.py.
        #
        # Note that the ranges should be sorted and merged.
        #
        # This feature is disabled if add_line_numbers_to_content is False, since
        # sending partial files is confusing without line numbers.
        self.absolute_file_names_to_ranges = {}
        self.absolute_file_names = set()
        self.additional_lines_around_mentioned_line_number = additional_lines_around_mentioned_line_number
        self.root = ""

    def yield_files_and_content(self, io):
        for absolute_fname in list(self.absolute_file_names):
            content = self.io.read_text(absolute_fname)

            if content is None:
                relative_fname = self.convert_absolute_to_relative(absolute_fname)
                io.tool_error(f"Dropping {relative_fname} from the chat.")
                self.absolute_file_names.remove(absolute_fname)
            else:
                yield absolute_fname, content

    def get_files_content(self, fence, add_line_numbers_to_content=False):
        file_content_outputs = []
        for absolute_fname, content in self.yield_files_and_content():
            relative_fname = self.convert_absolute_to_relative(absolute_fname)
            output = ""
            if add_line_numbers_to_content and absolute_fname in self.absolute_file_names_to_ranges:
                output += f"{relative_fname}:{','.join([f'{start}-{end}' for start, end in self.absolute_file_names_to_ranges[absolute_fname]])}"
            else:
                output += relative_fname
            output += f"\n{fence[0]}\n"
            if add_line_numbers_to_content:
                content_by_lines = content.splitlines()
                if absolute_fname in self.absolute_file_names_to_ranges:
                    for (start, end) in self.absolute_file_names_to_ranges[absolute_fname]:
                        line_number = start
                        for content_line in content_by_lines[start:end + 1]:
                            output += f"{line_number}|\t{content_line}\n"
                            line_number += 1
                        output += "..."
                else:
                    line_number = 1
                    for content_line in content_by_lines:
                        output += f"{line_number}|\t{content_line}\n"
                        line_number += 1
            else:
                output += content
            output += f"{fence[1]}"
            file_content_outputs.append(output)

        return "\n\n".join(file_content_outputs)


    def get_root(self):
        return self.root

    def convert_relative_to_absolute(self, relative_path):
        absolute_path = Path(self.root) / relative_path
        return utils.safe_abs_path(absolute_path)

    def convert_absolute_to_relative(self, absolute_path):
        return os.path.relpath(absolute_path, self.root)

    def set_root_from_repo(self, repo):
        self.root = repo.root

    def update_root_from_files(self):
        in_chat_files = self.files()

        root = os.getcwd()
        if len(in_chat_files) == 1:
            root = os.path.dirname(list(in_chat_files)[0])
        elif in_chat_files:
            root = os.path.commonpath(list(in_chat_files))

        self.root = root

    def add_relative_file(self, relative_filename):
        self.absolute_file_names.add(self.convert_relative_to_absolute(relative_filename))


    def add_file(self, absolute_fname):
        self.absolute_file_names.add(absolute_fname)

    def add_file_with_ranges(self, absolute_fname, ranges):
        self.absolute_file_names.add(absolute_fname)
        self.absolute_file_names_to_ranges[absolute_fname] = ranges

    def remove_file(self, absolute_fname):
        self.absolute_file_names.discard(absolute_fname)
        self.absolute_file_names_to_ranges.pop(absolute_fname, None)

    def has_files(self):
        return len(self.absolute_file_names) > 0

    def files(self):
        return self.absolute_file_names

    def relative_files(self):
        return set([self.convert_absolute_to_relative(fname) for fname in self.absolute_file_names])

    def get_inchat_files_with_ranges(self):
        return self.absolute_file_names_to_ranges

    def set_additional_lines_around_mentioned_line_number(self, number):
        self.additional_lines_around_mentioned_line_number = number
