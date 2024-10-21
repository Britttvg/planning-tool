from src.pages import excel
import streamlit as st
from streamlit_option_menu import option_menu
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
            f"Week {datetime.today().isocalendar()[1]} - Support - Exposure",
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

# The correct password
correct_password = "src/auth.txt"

# Initialize session state for password check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


@st.dialog("Voer wachtwoord in")
def password_dialog():
    password_input = st.text_input("Wachtwoord", type="password")
    if st.button("Submit"):
        if password_input == correct_password:
            st.session_state.authenticated = True
            st.rerun()  # Refresh the app state
        else:
            st.error("Onjuist wachtwoord.")


if st.session_state.authenticated == False:
    password_dialog()

#########################
######### PAGES #########
#########################

if choice == f"Week {datetime.today().isocalendar()[1]} - Dev":
    st.title(f":blue[Week {datetime.today().isocalendar()[1]} - Dev]")
    if st.session_state.authenticated:
        excel.show_excel("src/data/data_planning_dev.csv")
    else:
        st.warning("You need to be authenticated to view this page.")

if choice == f"Week {datetime.today().isocalendar()[1]} - Support - Exposure":
    st.title(f":orange[Week {datetime.today().isocalendar()[1]} - Support - Exposure]")
    if st.session_state.authenticated:
        excel.show_excel("src/data/data_planning_support.csv")
    else:
        st.warning("You need to be authenticated to view this page.")
