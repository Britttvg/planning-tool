from src.pages import excel, ical
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import hmac
import os
import git
from dotenv import load_dotenv
import time

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
        
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Voer wachtwoord in",
        type="password",
        on_change=password_entered,
        key="password",
    )
    
    # Use Markdown with HTML to style text as a button
    button_html = """
    <button class="submit_button">
        Submit
    </button>
    """

    # Display the "button" using st.markdown
    st.markdown(button_html, unsafe_allow_html=True)

    if "password_correct" in st.session_state:
        st.error("😕 Onjuist wachtwoord")
    return False


if not check_password():
    st.stop()

#########################
######### PAGES #########
#########################
    
# Display a custom-styled button
st.markdown("""
    <style>.element-container:has(#button-after) + div button {
    position: fixed;
    right: 0;
    top: 100;
    border: 1px solid red;
    background-color: #fff;
    }</style>""", unsafe_allow_html=True)
    
if choice == f"Week {datetime.today().isocalendar()[1]} - Dev":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_dev.csv")
    st.title(f":blue[Dev]")
    ical_file = ical.create_ical("src/data/data_planning_dev.csv")
    excel.show_excel("src/data/data_planning_dev.csv", ical_file)

        
if choice == f"Week {datetime.today().isocalendar()[1]} - Support - Exposure":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_support.csv")
    st.title(f":orange[Support - Exposure]")
    ical_file = ical.create_ical("src/data/data_planning_support.csv")
    excel.show_excel("src/data/data_planning_support.csv", ical_file)

if choice == f"Week {datetime.today().isocalendar()[1]} - Q Dev":
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button(':bangbang: Push to Git'):
        commit_and_push_changes("src/data/data_planning_q_dev.csv")
    st.title(f":green[Q Dev]")
    ical_file = ical.create_ical("src/data/data_planning_q_dev.csv")
    excel.show_excel("src/data/data_planning_q_dev.csv", ical_file)