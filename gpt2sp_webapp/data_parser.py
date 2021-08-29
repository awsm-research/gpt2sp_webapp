import pandas as pd
from transformers import GPT2Tokenizer


class DataParser:
    def __init__(self):
        self.predicted_project = None
        self.predicted_sp = None
        self.selected_tokens = None
        self.n_data = None

        self.DATA_PATH = "./historical_data/"
        self.token_file = "./training_tokens_non_unique.csv"
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        # 2D list > [[project, issue id hyperlink, issue id, issue title, sp], ...]
        self.parsed_issues = []
        self.parsed_count = 0
        # [historical data in ths same project, historical data in the diff project]
        self.same_diff_count = [0, 0, "N/A"]
        self.project_name_map = {"Titanium": "Titanium SDK/CLI",
                                 "JiraSoftware": "JIRA Software",
                                 "AppceleratorStudio": "Appcelerator Studio",
                                 "AptanaStudio": "Aptana Studio",
                                 "DataManagement": "Data Management",
                                 "DuraCloud": "Dura Cloud",
                                 "MuleStudio": "Mule Studio",
                                 "SpringXD": "Spring XD",
                                 "TalendDataQuality": "Talend Data Quality",
                                 "TalendESB": "Talend ESB"}
        self.link_map = {"titanium": "https://jira.appcelerator.org/browse/",
                         "jirasoftware": "https://jira.atlassian.com/browse/",
                         "appceleratorstudio": "https://jira.appcelerator.org/browse/",
                         "aptanastudio": "https://jira.appcelerator.org/browse/",
                         # deprecated
                         "datamanagement": "",
                         "duracloud": "https://jira.duraspace.org/browse/",
                         "mule": "https://www.mulesoft.org/jira/browse/",
                         "mulestudio": "https://www.mulesoft.org/jira/browse/",
                         "springxd": "https://jira.spring.io/browse/",
                         "talenddataquality": "https://jira.talendforge.org/browse/",
                         "talendesb": "https://jira.talendforge.org/browse/",
                         "bamboo": "https://jira.atlassian.com/browse/",
                         "clover": "https://jira.atlassian.com/browse/",
                         "moodle": "https://tracker.moodle.org/browse/",
                         "mesos": "https://issues.apache.org/jira/browse/",
                         "usergrid": "https://issues.apache.org/jira/browse/"}

    def __call__(self, predicted_project: str, predicted_sp: int, selected_tokens: list, n_data=3) -> list:
        self.predicted_project = predicted_project
        self.predicted_sp = predicted_sp
        self.selected_tokens = selected_tokens
        self.n_data = n_data

        self.parse_same_project()
        return self.parsed_issues, self.same_diff_count

    def highlight_token(self, title: str):
        return title.replace(self.selected_tokens[0],
                            f"""<mark style="background-color:hsl(120, 75%, 50%);opacity:1.0;line-height:1.75"><font color="black">{self.selected_tokens[0]}</font></mark>""")

    def load_df(self, path="default") -> pd.DataFrame:
        if path == "default":
            path = self.DATA_PATH + self.token_file
        return pd.read_csv(path)

    def parse_same_project(self):
        df = self.load_df()
        # find same project and same token
        df = df.loc[(df['Project'] == self.predicted_project)
                    & (df['Token'] == self.selected_tokens[0])]
        # remove duplicate issue ID in case of one issue has the same token appearing more than once
        df = df.drop_duplicates(subset=['ISSUE-ID'])
        total = len(df)
        # find same token with same sp in the same project
        df = df.loc[(df['SP ground-truth'] == self.predicted_sp)]
        # remove duplicate issue ID in case of one issue has the same token appearing more than once
        df = df.drop_duplicates(subset=['ISSUE-ID'])
        total_with_same_sp = len(df)
        self.same_diff_count[2] = round((total_with_same_sp / total) * 100, 0)
        # store the issue keys
        for _, row in df.iterrows():
            self.parsed_issues.append([row['Project'],
                                       self.link_map[self.predicted_project.lower()] + row['ISSUE-ID'],
                                       row['ISSUE-ID']])
            self.parsed_count += 1
            self.same_diff_count[0] += 1
        if self.n_data <= self.parsed_count:
            return self.parse_issue_title()
        else:
            # search diff project for more support data
            return self.parse_diff_project()

    def parse_diff_project(self):
        df = self.load_df()
        # find same token with same sp in the diff project
        df = df.loc[(df['Project'] != self.predicted_project)
                    & (df['SP ground-truth'] == self.predicted_sp)
                    & (df['Token'] == self.selected_tokens[0])]
        # remove duplicate issue ID in case of one issue has the same token appearing more than once
        df = df.drop_duplicates(subset=['ISSUE-ID'])
        # store the issue keys
        for _, row in df.iterrows():
            if self.parsed_count == self.n_data:
                break
            self.parsed_issues.append([row['Project'],
                                       self.link_map[self.predicted_project.lower()] + row['ISSUE-ID'],
                                       row['ISSUE-ID']])
            self.parsed_count += 1
            self.same_diff_count[1] += 1
        # if no records were found
        if self.parsed_count == 0:
            return "IssueNotFound"
        else:
            # search for description if at least one issue was found
            self.parse_issue_title()

    def parse_issue_title(self):
        for i in range(len(self.parsed_issues)):
            issue = self.parsed_issues[i]
            # issue is a list > [project, issue id hyperlink, issue id, issue title, sp]
            project = issue[0]
            key = issue[2]
            df = self.load_df(self.DATA_PATH + project + ".csv")
            df = df.loc[df["issuekey"] == key]
            title = df["title"].tolist()[0]
            title = self.highlight_token(title)
            self.parsed_issues[i].append(title)
            self.parsed_issues[i].append(df["storypoint"].tolist()[0])


#d = DataParser()
#d("titanium", 5.0, ["Windows"])