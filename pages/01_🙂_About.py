import pandas as pd 
import requests 
import streamlit as st 
from func.utils import donate_message 

url = "https://raw.githubusercontent.com/meharpalbasi/meharpalbasi/main/README.md"
response = requests.get(url)
readme_content = response.text if response.status_code == 200 else ""

# Render the README content
st.markdown(readme_content, unsafe_allow_html=True)
st.header("")
st.divider()
donate_message()