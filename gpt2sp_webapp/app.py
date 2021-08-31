import os
import pandas as pd
import streamlit as st
from transformers import GPT2Tokenizer, Pipeline
from GPT2ForSequenceClassification import GPT2ForSequenceClassification as GPT2SP
from data_parser import DataParser
from html_parser import html_parser
from html_table_builder import HTMLTable
from transformers_interpret.explainers.sequence_classification import SequenceClassificationExplainer

FULL_PROJ_NAME = {"Titanium": "Titanium SDK/CLI",
                  "JiraSoftware": "JIRA Software",
                  "AppceleratorStudio": "Appcelerator Studio",
                  "AptanaStudio": "Aptana Studio",
                  "DataManagement": "Data Management",
                  "DuraCloud": "Dura Cloud",
                  "MuleStudio": "Mule Studio",
                  "SpringXD": "Spring XD",
                  "TalendDataQuality": "Talend Data Quality",
                  "TalendESB": "Talend ESB"}
MODEL_NAME = {"Titanium SDK/CLI": "Titanium",
              "JIRA Software": "JiraSoftware",
              "Appcelerator Studio": "AppceleratorStudio",
              "Aptana Studio": "AptanaStudio",
              "Data Management": "DataManagement",
              "Dura Cloud": "DuraCloud",
              "Mule Studio": "MuleStudio",
              "Spring XD": "SpringXD",
              "Talend Data Quality": "TalendDataQuality",
              "Talend ESB": "TalendESB",
              "Usergrid": "usergrid",
              "Mule": "mule",
              "Moodle": "moodle",
              "Mesos": "mesos",
              "Clover": "clover",
              "Bamboo": "bamboo"}

PATH = os.getcwd() + "/gpt2sp_webapp"


def get_gpt2sp_pipeline(model: str) -> Pipeline:
    model = "MickyMike/0-GPT2SP-" + model.lower()
    gpt2sp = GPT2SP.from_pretrained(model)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = '[PAD]'
    return Pipeline(model=gpt2sp, tokenizer=tokenizer)


def get_top_token(token_attributions: list) -> list:
    # word_attributions have a shape of [('word', 0.1234), ...]
    top_index = 0
    top_value = None
    for i in range(len(token_attributions)):
        if top_value is None or token_attributions[i][1] > top_value:
            top_value = token_attributions[i][1]
            top_index = i
    return [str(token_attributions[top_index][0])]


def parse_history(predicted_project: str, predicted_sp: int, selected_tokens: list, n_data=3) -> list:
    parser = DataParser()
    return parser(predicted_project, predicted_sp, selected_tokens, n_data)


def predict_sp(estimator: Pipeline, given_title: str) -> dict:
    return round(estimator(given_title).item(), 0)


def write_history_table(list_of_issues: list):
    html_builder = HTMLTable()
    # show_n_rows depends on n_data
    html, hid_html = html_builder(list_of_issues, show_n_rows=3)
    st.write(html)
    return hid_html


def write_statistics(data: list):
    # data > [num of same proj support (depending on top-n data),
    #         num of diff proj support (depending on top-n data),
    #         support % with 2 digit number or "N/A"]
    if data[2] == "N/A":
        st.markdown(f'% of Supporting Examples: **{data[2]}**')
    else:
        st.markdown(f'% of Supporting Examples: **{int(data[2])}%** calculated by the following formula')


if __name__ == "__main__":
    logo = PATH + "/logo/gpt2sp_logo.png"
    st.set_page_config(page_title="GPT2SP", page_icon=logo)
    checked = False
    pipeline = None
    behavior = None
    dataset = None
    # sidebar
    st.sidebar.title("GPT2SP Web App")
    behavior = st.sidebar.selectbox(label="NAVIGATOR IS HERE:",
                                    options=["GPT2SP: Agile Story Point Estimator", "Dataset Viewer"])
    if behavior == "Dataset Viewer":
        # function title
        st.title("Agile Dataset Viewer")
        dataset = st.selectbox(label="Select the Agile Dataset",
                               options=[FULL_PROJ_NAME["AppceleratorStudio"],
                                        FULL_PROJ_NAME["AptanaStudio"],
                                        "Bamboo",
                                        "Clover",
                                        FULL_PROJ_NAME["DataManagement"],
                                        FULL_PROJ_NAME["DuraCloud"],
                                        FULL_PROJ_NAME["JiraSoftware"],
                                        "Mesos",
                                        "Moodle",
                                        "Mule",
                                        FULL_PROJ_NAME["MuleStudio"],
                                        FULL_PROJ_NAME["SpringXD"],
                                        FULL_PROJ_NAME["TalendDataQuality"],
                                        FULL_PROJ_NAME["TalendESB"],
                                        FULL_PROJ_NAME["Titanium"],
                                        "Usergrid"])
        dataset = MODEL_NAME[dataset]
        dataset = dataset.lower()
        dataset_path = PATH + "/historical_data/" + dataset + ".csv"
        st.dataframe(pd.read_csv(dataset_path))
    elif behavior == "GPT2SP: Agile Story Point Estimator":
        # set up logo and title
        logo_col, _, title_col = st.columns([10, 6, 70])
        with logo_col:
            st.image(logo, 100, 100)
        with title_col:
            st.title("GPT2SP - Agile Story Point Estimator")

        # model select box
        with st.form("model_select_form"):
            model_name = st.selectbox(label="Select the Agile project",
                                      options=[FULL_PROJ_NAME["AppceleratorStudio"],
                                               FULL_PROJ_NAME["AptanaStudio"],
                                               "Bamboo",
                                               "Clover",
                                               FULL_PROJ_NAME["DataManagement"],
                                               FULL_PROJ_NAME["DuraCloud"],
                                               FULL_PROJ_NAME["JiraSoftware"],
                                               "Mesos",
                                               "Moodle",
                                               "Mule",
                                               FULL_PROJ_NAME["MuleStudio"],
                                               FULL_PROJ_NAME["SpringXD"],
                                               FULL_PROJ_NAME["TalendDataQuality"],
                                               FULL_PROJ_NAME["TalendESB"],
                                               FULL_PROJ_NAME["Titanium"],
                                               "Usergrid"])
            model_name = MODEL_NAME[model_name]
            # user input of project title
            project_title = st.text_input("Enter a task title:", "")
            submitted = st.form_submit_button("Predict Story Point")

        if submitted:
            if not project_title:
                st.error("Please enter a task title!")
                st.stop()
            # load model
            with st.spinner("Loading model from the server, this may take a while..."):
                pipeline = get_gpt2sp_pipeline(model_name)
                st.success('Model Loaded Successfully!')
            # do inference
            story_point = predict_sp(pipeline, project_title)
            # inference complete
            st.balloons()
            st.write("Suggested Story Point: ", story_point)
            # interpret the prediction
            with st.spinner("Generating Explanations..."):
                explainer = SequenceClassificationExplainer(pipeline.model, pipeline.tokenizer)
                word_attributions = explainer(project_title)
                top_token = get_top_token(word_attributions)
                explanation_html = explainer.visualize()
                explanation_html = html_parser(explanation_html.data)
                st.write(explanation_html)
                st.markdown(f"**'{str(top_token[0])}'** is the most influential token contributing to the estimation")
            with st.spinner("Parsing historical data based on the top token '%s'" % str(top_token[0])):
                # parsed_issues: 2D list > [[project, issue id, issue title, sp], ...]
                # counting: list > [historical data in ths same project, historical data in the diff project]
                parsed_issues, counting = parse_history(model_name.lower(), story_point, top_token, n_data=3)
                # if no historical token is parsed
                if counting[0] == 0 and counting[1] == 0:
                    st.error("No similar historical data in training datasets")
                    st.stop()
                st.success("Similar historical issues found!")
                if counting[0] >= 3:
                    st.markdown("**%s** issues from the same project"
                                % str(counting[0]))
                else:
                    st.markdown("**%s** issues from the same project and **%s** issues from the different project"
                                % (str(counting[0]), str(counting[1])))
                st.markdown("that have the **_same_ _token_** and **_same_ _story_ _point_** as the predicted issue")
                write_statistics(counting)
                st.latex(r'''\frac{\#\mathrm{past\_issues}(\mathrm{same\_project, same\_token, same\_SP})}{\#\mathrm{past\_issues}(\mathrm{same\_project,same\_token})}\times100\%''')
                st.markdown(f"Here are the best 3 supporting examples!")
                hidden_html = write_history_table(parsed_issues)
            # see if there is hidden table to show
            if hidden_html == "NA":
                st.stop()
            st.button("show all")
            # find a way for show all button ....
