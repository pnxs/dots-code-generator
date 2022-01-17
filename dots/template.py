from jinja2 import Environment, FileSystemLoader
import sys
import re


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


def make_camel_case(source):
    # print("Source:", source)
    regex = re.compile("[^_]_[A-Za-z0-9]")
    while True:
        m = regex.search(source)
        if m:
            source = source[: m.start()+1] + source[m.end()-1].upper() + source[m.end():]
        else:
            break
    # print("Result:", source)
    return source


def make_snake_case_upper(source):
    return re.sub("((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))", r'_\1', source).upper()


class DdlTemplate:
    def __init__(self, template_directory, output_file):
        self.env = Environment(loader=FileSystemLoader(template_directory),
                               extensions=["jinja2.ext.do"])
        self.env.filters["expand_list"] = expand_list
        self.env.filters["camel_caselizer"] = make_camel_case
        self.env.filters["SNAKE_CASELIZER"] = make_snake_case_upper
        self.env.lstrip_blocks = True
        self.env.trim_blocks = True
        self.env.keep_trailing_newline = True
        if output_file == "-":
            self.output_file = sys.stdout
        else:
            self.output_file = open(output_file, "w")

    def render(self, template_file, variables):
        t = self.env.get_template(template_file)
        self.output_file.write(t.render(variables))
        self.output_file.close()
