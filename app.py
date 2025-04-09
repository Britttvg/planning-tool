from src.pages import excel
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import os
import git
from dotenv import load_dotenv

st.set_page_config(page_title="Planning tool", page_icon=":calendar:", layout="wide")

### Menu ###
with st.sidebar:
    # The option_menu should not be wrapped in a list; use it directly
    choice = option_menu(
        "Menu",
        [
            f"Week {datetime.today().isocalendar()[1]} - Dev",
            f"Week {datetime.today().isocalendar()[1]} - Support - Exposure",
            f"Week {datetime.today().isocalendar()[1]} - Q Dev",
        ],
        # Icons from https://icons.getbootstrap.com
        icons=[
            "file-earmark-spreadsheet",
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


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Load environment variables from .env file
load_dotenv()

def commit_and_push_changes(data_url):
    """Function to commit and push changes to GitHub."""
    success_placeholder = st.empty()
    success_placeholder.empty()  # Clear the message
    try:
        repo = git.Repo()
        repo.git.remote("set-url", "origin", f"https://{GITHUB_TOKEN}@github.com/Britttvg/planning-tool.git")
        repo.git.checkout('main')
        repo.remotes.origin.pull()

        # Add, commit, and push the changes to the repository
        repo.git.add(data_url)
        repo.index.commit(f'Update CSV {data_url}, time {datetime.now()}')
        repo.remotes.origin.push()

        # Temporary success message
        success_placeholder.success(f"Data {data_url} saved and pushed to git.")
    except Exception as e:
        st.warning(f"Error saving data: {e}")
   
def password_entered():
    """Checks whether a password entered by the user is correct."""
    st.session_state["password_correct"] = st.session_state["password"] == st.secrets["password"]
  
def check_password():
    """Returns `True` if the user had the correct password."""
    # Initialize session state if not already initialized
    if "password" not in st.session_state:
        st.session_state["password"] = ""
    
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    # Show input for password.
    st.text_input("Voer wachtwoord in", type="password", on_change=password_entered, key="password")
    
    if st.button("Submit", key="password_button"):
        password_entered()

    if "password_correct" in st.session_state and not st.session_state["password_correct"] and st.session_state["password"]:
        st.error("😕 Onjuist wachtwoord")
    
    return False

if not check_password():
    st.stop()

#########################
######### PAGES #########
#########################

if choice == f"Week {datetime.today().isocalendar()[1]} - Dev":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)  
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_dev.csv")
    st.title(":blue[Dev]")
    excel.show_excel("src/data/data_planning_dev.csv")

        
if choice == f"Week {datetime.today().isocalendar()[1]} - Support - Exposure":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)  
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_support.csv")
    st.title(":orange[Support - Exposure]")
    excel.show_excel("src/data/data_planning_support.csv")

if choice == f"Week {datetime.today().isocalendar()[1]} - Q Dev":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)  
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_q_dev.csv")
    st.title(":green[Q Dev]")
    excel.show_excel("src/data/data_planning_q_dev.csv")