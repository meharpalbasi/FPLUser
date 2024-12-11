import streamlit as st 

def donate_message():
    """A 'Buy Me a Coffee' message with a link to the donation page displayed
    inline"""
    html_content = """
    <div style="display: flex; align-items: center; gap: 10px;">
        <span>If you like this work and want to support me</span>
        <a
            href="https://www.buymeacoffee.com/mbas"
            target="_blank"
            style="
                background-color: #FFDD00;
                color: black;
                padding: 10px 20px;
                text-decoration: none;
                font-weight: bold;
                border-radius: 5px;
            "
        >
            Buy Me a Coffee ☕
        </a>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)