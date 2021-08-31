from IPython.core.display import HTML


def html_parser(html: str) -> str:
    html = html.replace("""<div style="border-top: 1px solid; margin-top: 5px;             padding-top: 5px; display: inline-block">""",
                        """<div style="display: inline-block">""")
    html = html.replace("<th>True Label</th>", "")
    html = html.replace("""<td><text style="padding-right:2em"><b>0</b></text></td>""", "")
    html = html.replace("""<td><text style="padding-right:2em"><b>NA</b></text></td>""", "")
    html = html.replace("<th>Attribution Label</th>", "")
    html = html.replace("width: 10px", "width: 7px")
    html = html.replace("height: 10px", "height: 7px")
    return to_ipy_HTML(html)


def to_ipy_HTML(html: str) -> HTML:
    return HTML(html)
