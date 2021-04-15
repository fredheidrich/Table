"""

Explode table.

License: public domain
Author: Fred Heidrich 016/04/2021

IDEAS

OVERVIEW 

- multiple selection

- tightly pack

"""

import sublime
import sublime_plugin


__version__ = "0.1dev160421"
VERSION = __version__


class TableFormatCommand(sublime_plugin.TextCommand):
    
    def run(self, edit, delimiter=","):

        sel = self.view.sel()
        old_sel = [s for s in sel]

        is_selection_empty = False
        for s in self.view.sel():
            our_sel = s
            if s.empty():
                is_selection_empty = True
                self.view.window().run_command("expand_selection_to_paragraph", args={ })
                new_sel = self.view.sel()
                if len(new_sel) == 1:
                    our_sel = new_sel[0]
                else:
                    # todo/fred: diagnose
                    assert False

            text = self.view.substr(our_sel)

            self.view.sel().clear()
            lines = text.splitlines(keepends=False)

            # note/fred: this is [col][row]
            max_col_widths = []

            max_col_count = 0
            max_char_count = 0
            col_index = 0

            for line in lines:
                line_length = len(line)
                max_char_count = line_length if line_length > max_char_count else max_char_count
                    
                cols = line.split(delimiter)
                col_widths = [len(c.strip()) for c in cols]
                for col_index, col_width in enumerate(col_widths):
                    if len(max_col_widths) < (col_index + 1):
                        max_col_widths.append(0)

                    if col_width > max_col_widths[col_index]:
                        max_col_widths[col_index] = col_width

                col_count = len(cols)
                max_col_count = col_count if col_count > max_col_count else max_col_count

            if max_col_count > 1:
                new_text = ""
                lines = text.splitlines(keepends=False)
                for line in lines:

                    cols = line.split(delimiter)
                    if len(cols) == 1:
                        new_text += line + "\n"
                        continue

                    if len(cols) < max_col_count:
                        cols += [""] * (max_col_count - len(cols))

                    new_line = (delimiter + " ").join(
                        [
                            col.strip().ljust(max_col_widths[col_index])
                            for col_index, col in enumerate(cols) if len(cols) > 1
                        ]
                    )
                    new_text += new_line + "\n"

                num = self.view.insert(edit, our_sel.begin(), new_text)
                self.view.erase(edit, sublime.Region(our_sel.begin() + num, our_sel.end() + num))
                dsel = num - (our_sel.end() - our_sel.begin()) - 1

                if not is_selection_empty:
                    self.view.sel().add(sublime.Region(our_sel.begin(), our_sel.end() + dsel))
                else:
                    self.view.sel().add(our_sel.end() + dsel)

                # print("----")
                # print("cols: {}, chars: {}".format(max_col_count, max_char_count))

            # print(max_char_count)
