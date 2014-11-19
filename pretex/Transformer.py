# coding=utf-8
from __future__ import unicode_literals
import copy
import io
import json
import re
import textwrap
import pkg_resources
from .trafos import transform_auto_align, transform_main


def get_inside_str(s):
    return textwrap.dedent(s)[1:-1]


class Transformer(object):
    def __init__(self):
        self.config = self.get_default_config()


    @staticmethod
    def get_default_config():
        config = {key: "enabled" for key in
                  ["arrow", "approx", "leq", "sub_superscript", "geq", "ll",
                   "gg", "neq", "cdot", "braket", "dots", "frac", "auto_align"]}
        config.update({key: "disabled" for key in ["dot", "html"]})
        config["braket_style"] = "small"
        return config


    def get_transformed_math(self, content, env_type):
        """ the actual transformations with the math contents """

        trafos = []
        content, trafos_auto_align = transform_auto_align(content, self.config, env_type)
        content, trafos_main = transform_main(content, self.config)
        trafos.extend(trafos_main)
        trafos.extend(trafos_auto_align)
        return content, trafos


    @staticmethod
    def get_file_parts(file_str):
        pattern_begin_document = re.compile(r"""
            (\n|^)[^%\n]*?
            \\begin\ *\{document\}
            """, re.VERBOSE)

        pattern_end_document = re.compile(r"""
            (\n|^)[^%\n]*?
            \\end\ *\{document\}
            """, re.VERBOSE)

        match = pattern_begin_document.search(file_str)
        if match:
            before_document = file_str[:match.end()]
            file_str = file_str[match.end():]
        else:
            before_document = ""

        match = pattern_end_document.search(file_str)
        if match:
            after_document = file_str[match.start()+1:]
            file_str = file_str[:match.start()+1]
        else:
            after_document = ""

        return before_document, file_str, after_document


    @staticmethod
    def hide_comments(document_str):
        pattern_comments = re.compile(r"""
            (
              (?<!\\)(?:%.*)
              (?:\n%.*)*
            )
            """, re.VERBOSE)

        comments_saved = []

        def repl_comments(match_obj):
            return_str = "%" + str(repl_comments.comment_number) + " "
            comments_saved.append(match_obj.group(0))
            repl_comments.comment_number += 1
            return return_str

        repl_comments.comment_number = 0
        return pattern_comments.sub(repl_comments, document_str), comments_saved


    @staticmethod
    def hide_math_texts(document_str):
        pattern_mtext = re.compile(r"""
            \\(?:text|label|mbox|textrm)
            \ *?
            \{(?:.|\n)*?\}
            """, re.VERBOSE)

        mtexts_saved = []

        def repl_matexts(match_obj):
            return_str = "%t" + str(repl_matexts.mtext_number) + " "
            mtexts_saved.append(match_obj.group(0))
            repl_matexts.mtext_number += 1
            return return_str

        repl_matexts.mtext_number = 0
        return pattern_mtext.sub(repl_matexts, document_str), mtexts_saved


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
            math_content, trafos = self.get_transformed_math(math_match.group("content"), env_type)
            doc_tree.append({"type": "math_env",
                             "content": math_content, "pretexes": trafos})

            # iteration
            document_str = math_match.group("env_closing") + document_str[math_match.end():]
            math_match = re_extract_math.search(document_str, len(math_match.group("env_closing")))

        doc_tree.append({"type": "text", "content": document_str})
        return doc_tree


    def get_transformed_tree(self, content, filename="unknown"):
        before_document, document_content, after_document = self.get_file_parts(content)
        document_content, saved_comments = self.hide_comments(document_content)
        document_content, saved_mtexts = self.hide_math_texts(document_content)
        doc_tree = self.get_pretextec_tree(document_content)

        # Add the rest from document and insert header/footer at the edges
        doc_tree[0]["content"] = before_document + doc_tree[0]["content"]
        doc_tree[-1]["content"] = doc_tree[-1]["content"] + after_document

        for el in doc_tree:
            if saved_comments:
                el["content"] = re.compile(r"%\d+ ").sub(lambda x: saved_comments.pop(0), el["content"])
            if saved_mtexts:
                el["content"] = re.compile(r"%t\d+ ").sub(lambda x: saved_mtexts.pop(0), el["content"])

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

