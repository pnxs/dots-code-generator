#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import sys


def expand_list(seq, format_string, beg="", mid="", end=""):
    if len(seq) == 0:
        return ""
    ret = beg
    new_list = []
    for e in seq:
        new_list.append(str.format(format_string, e))
    ret += mid.join(new_list)
    ret += end
    return ret


class DdlTemplate:
    def __init__(self, template_directory, output_file):
        self.env = Environment(loader=FileSystemLoader(template_directory),
                               extensions=[])
        self.env.filters["expand_list"] = expand_list
        self.env.lstrip_blocks = True
        self.env.trim_blocks =  True
        self.env.keep_trailing_newline = True
        if output_file is "-":
            self.output_file = sys.stdout
        else:
            self.output_file = open(output_file, "w")

    def render(self, template_file, variables):
        t = self.env.get_template(template_file)
        self.output_file.write(t.render(variables))
