
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(page_title="TraderSync Clone Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
        }

        .stSidebar {
            background-color: #161b22;
        }

        .st-bb, .st-at, .st-ae, .st-af, .st-ag {
            background-color: #161b22 !important;
            color: #e6edf3 !important;
        }

        .stButton>button {
            background-color: #238636;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1em;
        }

        .stButton>button:hover {
            background-color: #2ea043;
        }

        .css-1v3fvcr {
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Upload file
st.sidebar.title("📁 Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload your closedPositionsTab.csv", type="csv")

# [rest of the code remains unchanged from your current version]
