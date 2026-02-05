import requests
import streamlit as st


def get_model1_response(input_test:str) -> str:
    response = requests.post(
        url="http://localhost:8000/poem/invoke",
        json={"input": {"topic": input_test}}
    )
    response.raise_for_status()
    data = response.json()
    return data.get("output", "")

def get_model2_response(input_test:str) -> str:
    response = requests.post(
        url="http://localhost:8000/eassy/invoke",
        json={"input": {"topic": input_test}}
    )
    response.raise_for_status()
    data = response.json()
    return data.get("output", "")


st.title("Langchain API Client")
input_text = st.text_input("Enter a topic:")
if input_text:
    st.write("Getting response from model 1...")
    model1_response = get_model1_response(input_text)
    st.write("Model 1 Response: ", model1_response)

    st.write("Getting response from model 2...")
    model2_response = get_model2_response(input_text)
    st.write("Model 2 Response: ", model2_response)