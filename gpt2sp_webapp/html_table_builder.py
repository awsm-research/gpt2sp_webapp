from IPython.core.display import HTML


class HTMLTable:
    def __init__(self):
        self.table = """<table width: 100%><table>"""
        self.hidden_table = """<table width: 100%><table>"""
        self.has_hidden_table = False

    def __call__(self, list_of_issues: list, show_n_rows: int) -> HTML:
        self.build_table(list_of_issues, show_n_rows)
        if not self.has_hidden_table:
            self.hidden_table = "NA"
        return self.table, self.hidden_table

    def build_table(self, list_of_issues: list, show_n_rows: int):
        self.insert_header_row()
        if len(list_of_issues) > show_n_rows:
            to_show = list_of_issues[:show_n_rows]
            to_hide = list_of_issues[show_n_rows:]
            # building hidden table if we have more data
            self.insert_hidden_header_row()
            for issue in to_hide:
                self.insert_hidden_record_row(issue)
            self.hidden_table += "</table>"
            self.hidden_table = HTML(self.hidden_table)
            self.has_hidden_table = True
        else:
            to_show = list_of_issues
        for issue in to_show:
            self.insert_record_row(issue)
        self.table += "</table>"
        self.table = HTML(self.table)

    def insert_header_row(self):
        self.table += """<tr><th>Project</th><th>Issue ID</th><th>Issue Title</th><th>Story Point</th></tr>"""

    def insert_hidden_header_row(self):
        self.hidden_table += """<tr><th>Project</th><th>Issue ID</th><th>Issue Title</th><th>Story Point</th></tr>"""

    def insert_hidden_record_row(self, issue: list):
        self.hidden_table += """<tr><th>%s</th><th><a href="%s" target="_blank">%s</a></th><th>%s</th><th>%s</th></tr>""" \
                             % (issue[0], issue[1], issue[2], issue[3], issue[4])

    def insert_record_row(self, issue: list):
        self.table += """<tr><th>%s</th><th><a href="%s" target="_blank">%s</a></th><th>%s</th><th>%s</th></tr>""" \
                      % (issue[0], issue[1], issue[2], issue[3], issue[4])
