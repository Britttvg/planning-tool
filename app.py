from src.pages import planning, design, excel
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Planning tool", page_icon=":calendar:", layout="centered"
)

### Menu ###
with st.sidebar:
    # The option_menu should not be wrapped in a list; use it directly
    choice = option_menu(
        "Menu",
        [
            f"Week {datetime.today().isocalendar()[1]} - Dev",
            f"Week {datetime.today().isocalendar()[1]} - Support",
        ],
        # Icons from https://icons.getbootstrap.com
        icons=[
            "file-earmark-spreadsheet",
            "file-earmark-spreadsheet",
        ],
        menu_icon="house",
        default_index=0,
        styles={
            "container": {"padding": "5!important"},
            "icon": {"color": "#00000", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#91A2A4",
            },
            "nav-link-selected": {"background-color": "#1a95a5"},
        },
    )

# Inladen CSS
with open("src/style/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#########################
######### PAGES #########
#########################

if choice == f"Week {datetime.today().isocalendar()[1]} - Dev":
    st.title(f":blue[Week {datetime.today().isocalendar()[1]} - Dev]")
    excel.show_excel("src/data/data_planning_dev.csv")

if choice == f"Week {datetime.today().isocalendar()[1]} - Support":
    st.title(f":orange[Week {datetime.today().isocalendar()[1]} - Support]")
    excel.show_excel("src/data/data_planning_support.csv")
