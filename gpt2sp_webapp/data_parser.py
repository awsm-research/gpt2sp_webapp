import pandas as pd
from transformers import GPT2Tokenizer


class DataParser:
    def __init__(self, predicted_project: str, predicted_sp: int, selected_tokens: list, n_data=3):
        self.predicted_project = predicted_project
        self.predicted_sp = predicted_sp
        self.selected_tokens = selected_tokens
        self.n_data = n_data

        self.DATA_PATH = "./historical_data/"
        self.token_file = "training_tokens_non_unique.csv"
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        # 2D list > [[project, issue id, project title], ...]
        self.parsed_issues = []
        self.parsed_count = 0

    def __call__(self, *args, **kwargs):
        pass

    def load_df(self, path="default"):
        if path == "default":
            path = self.DATA_PATH + self.token_file
        return pd.read_csv(path)

    def parse_same_project(self):
        df = self.load_df()
        # find same token with same sp in the same project
        df = df.loc[(df['Project'] == self.predicted_project)
                    & (df['SP ground-truth'] == self.predicted_sp)
                    & (df['Token'] == self.selected_tokens[0])]
        # store the issue keys
        for _, row in df.iterrows():
            if self.parsed_count == self.n_data:
                break
            self.parsed_issues.append([row['Project'], row['ISSUE-ID']])
            self.parsed_count += 1
        if self.n_data == self.parsed_count:
            return
        else:
            # search diff project for more support data
            return self.parse_diff_project()

    def parse_diff_project(self):
        df = self.load_df()
        # find same token with same sp in the diff project
        df = df.loc[(df['Project'] != self.predicted_project)
                    & (df['SP ground-truth'] == self.predicted_sp)
                    & (df['Token'] == self.selected_tokens[0])]
        # store the issue keys
        for _, row in df.iterrows():
            if self.parsed_count == self.n_data:
                break
            self.parsed_issues.append([row['Project'], row['ISSUE-ID']])
            self.parsed_count += 1
        # if no records were found
        if self.parsed_count == 0:
            return "IssueNotFound"
        else:
            # search for description if at least one issue was found
            self.parse_issue_title()

    def parse_issue_title(self):
        for i in range(len(self.parsed_issues)):
            issue = self.parsed_issues[i]
            project = issue[0]
            key = issue[1]
            df = self.load_df(self.DATA_PATH + project + ".csv")
            df = df.loc[df["issuekey"] == key]
            self.parsed_issues[i].append(df["title"].tolist()[0])
        return print(self.parsed_issues)


d = DataParser("bamboo", 5, ["VS"])
d.parse_same_project()
