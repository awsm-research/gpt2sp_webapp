import streamlit as st
from transformers import GPT2Tokenizer, Pipeline
from GPT2ForSequenceClassification import GPT2ForSequenceClassification as GPT2SP
from transformers_interpret.explainers.sequence_classification import SequenceClassificationExplainer


def get_gpt2sp_pipeline(model: str) -> Pipeline:
    model = "MickyMike/0-GPT2SP-" + model.lower()
    gpt2sp = GPT2SP.from_pretrained(model)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = '[PAD]'
    return Pipeline(model=gpt2sp, tokenizer=tokenizer)


def predict_sp(estimator: Pipeline, given_title: str) -> dict:
    return round(estimator(given_title).item(), 0)


if __name__ == "__main__":
    pipeline = None
    # app title
    st.title('GPT2SP - Agile Story Point Estimator')
    # model select box
    with st.form("model_select_form"):
        model_name = st.selectbox(label="Select the Agile project",
                                  options=["AppceleratorStudio",
                                           "AptanaStudio",
                                           "Bamboo",
                                           "Clover",
                                           "DataManagement",
                                           "DuraCloud",
                                           "JiraSoftware",
                                           "Mesos",
                                           "Moodle",
                                           "Mule",
                                           "MuleStudio",
                                           "SpringXD",
                                           "TalendDataQuality",
                                           "TalendESB",
                                           "Titanium",
                                           "UserGrid"])

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
                explanation_html = explainer.visualize()
                st.write(explanation_html)
