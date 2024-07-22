import streamlit as st

api_key = st.secrets["AZURE_OPENAI_API_KEY"],
api_version = st.secrets["OPENAI_API_VERSION"],
azure_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"],
model = st.secrets["AZURE_OPENAI_DEPLOYMENT"]
