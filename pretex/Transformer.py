# coding=utf-8
from __future__ import unicode_literals
import copy
import io
import json
import re
import textwrap
import pkg_resources
from functools import partial
from .trafos import transform_auto_align, transform_main


def get_inside_str(s):
    return textwrap.dedent(s)[1:-1]

def get_document_contents(file_str):    
    match_begin = re.search(r"\\begin\ *\{document\}", file_str)
    match_end = re.search(r"\\end\ *\{document\}", file_str)
    if match_begin and match_end:
        before_document = file_str[:match_begin.end()]
        after_document = file_str[match_end.start():]
        document_content = file_str[match_begin.end():match_end.start()]
    else:
        before_document = ""
        after_document = ""
        document_content = file_str

    return before_document, document_content, after_document


def strip_comments(ss):
    def strip_line_comment(line):
        return re.split(r"(?<!\\)%", line)[0]
    return "\n".join(map(strip_line_comment, ss.split("\n")))


def hide_math_stuff(document_str):
    pattern = re.compile(r"""
          \\(?:text|label|mbox|textrm)
          \ *?
          \{(?:.|\n)*?\}
        """, re.VERBOSE)

    stuff_saved = []
    def repl(match_obj):
        stuff_saved.append(match_obj.group(0))
        return "%e "
    return_str = pattern.sub(repl, document_str)
    return return_str, stuff_saved


def get_default_config():
    config = {key: "enabled" for key in
              ["arrow", "approx", "leq", "sub_superscript", "geq", "ll",
               "gg", "neq", "cdot", "braket", "dots", "frac", "auto_align", "substack"]}
    config.update({key: "disabled" for key in ["dot", "brackets", "html"]})
    config["braket_style"] = "small"
    return config


def get_transformed_math(content, config, env_type=None ):
        """ the actual transformations with the math contents """

        trafos = []
        content, trafos_auto_align = transform_auto_align(content, config, env_type)
        content, trafos_main = transform_main(content, config)
        trafos.extend(trafos_main)
        trafos.extend(trafos_auto_align)
        return content, trafos


class Transformer(object):
    def __init__(self):
        self.config = get_default_config()
        

    def get_pretextec_tree(self, document_str):
        re_extract_math = re.compile(r"""
            (?P<env_opening>
              (?<!\\)(?P<dd>\$\$) |
              (?<!\\)(?P<sd>\$) |
              (?<!\\)(?P<braces>\\\() |
              (?<!\\)(?P<braces_sq>\\\[) |
              \\begin\ *?{
                (?P<env_name>(?:
                  equation|align|math|displaymath|eqnarray|gather|flalign|multiline|alignat
                )\*?)}
            )

            (?P<content>
              (?:\n|\\\$|[^\$])+?
            )

            (?P<env_closing>
              (?(dd)\$\$|(?!)) |
              (?(sd)\$|(?!)) |
              (?(braces)\\\)|(?!)) |
              (?(braces_sq)\\\]|(?!)) |
              (?(env_name)\\end\ *?{(?P=env_name)}|(?!))
            )
            """, re.VERBOSE)

        doc_tree = []
        math_match = re_extract_math.search(document_str)
        while math_match:  # Can't use finditer() because document_str is changed during iteration
            # text part
            before_document = document_str[:math_match.start()] + math_match.group("env_opening")
            doc_tree.append({"type": "text", "content": before_document})

            # math part
            env_type = math_match.group("env_name") or "inline"
            math_content, trafos = get_transformed_math(math_match.group("content"), self.config, env_type)
            doc_tree.append({"type": "math_env",
                             "content": math_content, "pretexes": trafos})

            # iteration
            document_str = math_match.group("env_closing") + document_str[math_match.end():]
            math_match = re_extract_math.search(document_str, len(math_match.group("env_closing")))

        doc_tree.append({"type": "text", "content": document_str})
        return doc_tree


    def get_transformed_tree(self, content, filename="unknown"):
        before_document, document_content, after_document = get_document_contents(content)
        document_content = strip_comments(document_content)
        document_content, saved_stuff = hide_math_stuff(document_content)
        doc_tree = self.get_pretextec_tree(document_content)

        # Add the rest from document and insert header/footer at the edges
        doc_tree[0]["content"] = before_document + doc_tree[0]["content"]
        doc_tree[-1]["content"] = doc_tree[-1]["content"] + after_document

        if saved_stuff:
            for el in doc_tree:
                el["content"] = re.compile(r"%[ce] ").sub(lambda x: saved_stuff.pop(0), el["content"])

        if self.config["html"] == "enabled":
            self.viz_output(doc_tree, filename)

        return doc_tree


    def get_transformed_str(self, content, filename="unknown"):
        doc_tree = self.get_transformed_tree(content, filename)
        document_content_new = "".join([element["content"] for element in doc_tree])
        return document_content_new


    @staticmethod
    def viz_output(tree, filename="unknown"):
        html_str = ""
        for elem in tree:
            content = elem["content"]
            for rep in [(r"<", r"&lt;"), (r">", r"&gt;")]:
                content = content.replace(*rep)
            extra_str = " "
            class_str = elem["type"]
            if elem["type"] == "math_env" and elem["pretexes"]:
                pretexes_str = "<br>".join(["- type: "+trafo["type"] for trafo in elem["pretexes"]])
                class_str += " pretexted"
                extra_str = 'onmousemove="showCoords(event, \'{pretexes}\');" onmouseover="document.getElementById(\'ibox\').className=\' \';" onmouseout="document.getElementById(\'ibox\').className=\'invisible\';"'.format(pretexes=pretexes_str)
            html_str += r'<span class="{class_str}" {extra_str}>{content}</span>'.format(
                class_str=class_str, content=content, extra_str=extra_str)

        html_content = r"<pre>{tree_converted}</pre>".format(tree_converted=html_str)

        script_filename = pkg_resources.resource_filename("pretex", 'viz/script.js')
        style_filename = pkg_resources.resource_filename("pretex", 'viz/style.css')
        with io.open(script_filename, 'r', encoding='utf-8') as file_in:
            script_str = file_in.read()
        with io.open(style_filename, 'r', encoding='utf-8') as file_in:
            style_str = file_in.read()

        viz_template = get_inside_str(r'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>preTeX</title>
                <style>{style_str}</style>
                <script>{script_str}</script>
                </head>
            <body>
            <p>Detected math is colored. Those who were changed in <span class="pretexted">this color</span>, the others <span class="math_env">like this</span>. Mouseover on the changed ones reveals some information.</p>
            <p>Filename: {filename}</p>
            <hr>

            {content}
            <div id="ibox" class="invisible" style="position: absolute; background:hsl(0,0%,90%); padding:5px;">fsdf</div>
            </body>
            </html>
            ''').format(content=html_content, script_str=script_str, style_str=style_str, filename=filename)

        dot_position = filename.rfind(".")
        output_filename = filename[:dot_position] + "_viz.html"
        with io.open(output_filename, 'w', encoding='utf-8') as file_out:
            file_out.write(viz_template)

