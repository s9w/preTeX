# coding=utf-8
import copy
import io
import json
import re
import textwrap
from .trafos import transform_auto_align, transform_main


def get_inside_str(s):
    return textwrap.dedent(s)[1:-1]


class Transformer(object):
    def __init__(self):
        self.tree = dict()
        self.config = self.get_default_config()

    @staticmethod
    def get_default_config():
        config = {key: "enabled" for key in
                  ["arrow", "approx", "leq", "sub_superscript", "geq", "ll",
                   "gg", "neq", "cdot", "braket", "dots", "frac"]}
        config.update({key: "disabled" for key in ["auto_align", "dot"]})
        config["braket_style"] = "small"
        return config


    def get_transformed_math(self, content, env_type):
        """ the actual transformations with the math contents """

        # changes = dict()
        # math_string = transform_auto_align(math_string, self.config, env_type)
        content, trafos = transform_main(content, self.config)
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

        # document_match = pattern_document.search(file_str)
        # if document_match:
        #     before_document, document_content, after_document = document_match.groups()
        # else:
        #     before_document, document_content, after_document = ("", file_str, "")
        # return before_document, document_content, after_document


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


    def get_transformed_tree(self, content):
        before_document, document_content, after_document = self.get_file_parts(content)
        document_content, saved_comments = self.hide_comments(document_content)
        document_content, saved_mtexts = self.hide_math_texts(document_content)
        doc_tree = self.get_pretextec_tree(document_content)

        # Add the rest from document and insert header/footer at the edges
        doc_tree[0]["content"] = before_document + doc_tree[0]["content"]
        doc_tree[-1]["content"] = doc_tree[-1]["content"] + after_document
        # print("doc_tree", json.dumps(doc_tree, sort_keys=True, indent=4, separators=(',', ': ')))

        for el in doc_tree:
            if saved_comments:
                el["content"] = re.compile(r"%\d+ ").sub(lambda x: saved_comments.pop(0), el["content"])
            if saved_mtexts:
                el["content"] = re.compile(r"%t\d+ ").sub(lambda x: saved_mtexts.pop(0), el["content"])
        return doc_tree


    def get_transformed_str(self, content):
        doc_tree = self.get_transformed_tree(content)
        document_content_new = "".join([element["content"] for element in doc_tree])
        return document_content_new


    @staticmethod
    def viz_output(tree):
        html_str = ""
        for elem in tree:
            content = elem["content"].replace("\n", "<br>")
            title_str = ""
            class_str = elem["type"]
            if elem["type"] == "math_env" and elem["pretexes"]:
                title_str = "pretexted"
                class_str += " pretexted"
            html_str += r'<span class="{class_str}" title="{title_str}">{content}</span>'.format(class_str=class_str, title_str=title_str, content=content)

        html_content = r"<div>{tree_converted}</div>".format(tree_converted=html_str)

        viz_template = get_inside_str(r'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <link rel="stylesheet" href="style.css">
                <script src="script.js" type="text/javascript"></script>
                </head>
            <body onload="body_ready()">
            <script>
            </script>
            {content}
            </body>
            </html>
            ''').format(content=html_content)

        with io.open("viz/viz.html", 'w', encoding='utf-8') as file_out:
            file_out.write(viz_template)

