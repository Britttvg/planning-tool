from src.pages import excel
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import os
import git
from dotenv import load_dotenv
import pandas as pd

st.set_page_config(page_title="Planning tool", page_icon=":calendar:", layout="wide")

### Menu ###
with st.sidebar:
    # The option_menu should not be wrapped in a list; use it directly
    choice = option_menu(
        "Menu",
        [
            f"Week {datetime.today().isocalendar()[1]} - Dev",
        ],
        # Icons from https://icons.getbootstrap.com
        icons=[
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

def merge_all_edits(original_path: str) -> pd.DataFrame:
    """Merge original CSV with all per-week edits from tmp_data/."""
    df_original = pd.read_csv(original_path)
    df_original["Datum"] = pd.to_datetime(df_original["Datum"], dayfirst=False)
    
    edited_files = [f for f in os.listdir("tmp_data") if f.endswith(".csv") and f.startswith("week_")]

    for f in edited_files:
        try:
            df_edit = pd.read_csv(os.path.join("tmp_data", f))
            df_edit["Datum"] = pd.to_datetime(df_edit["Datum"], dayfirst=False)

            # Use "Datum" as unique identifier to match and update rows
            df_edit.set_index("Datum", inplace=True)
            df_original.set_index("Datum", inplace=True)

            df_original.update(df_edit)

            # Reset index back to columns
            df_original.reset_index(inplace=True)
        except Exception as e:
            st.warning(f"Error merging {f}: {e}")

    df_original["Week"] = df_original["Datum"].dt.isocalendar().week
    df_original["Jaar"] = df_original["Datum"].dt.year.astype(int)
    return df_original


def save_merged_to_repo_file(merged_df: pd.DataFrame, save_path: str):
    """Save merged DataFrame to repo-tracked file (for commit)."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    merged_df.to_csv(save_path, index=False)


def commit_and_push_changes(source_data_path: str):
    """Function to commit and push changes to GitHub."""
    success_placeholder = st.empty()
    success_placeholder.empty()  # Clear the message
    try:
        merged = merge_all_edits(source_data_path)
        save_merged_to_repo_file(merged, source_data_path)
        
        repo = git.Repo()
        repo.git.remote("set-url", "origin", f"https://{GITHUB_TOKEN}@github.com/Britttvg/planning-tool.git")
        repo.git.checkout('main')
        repo.remotes.origin.pull()

        # Add, commit, and push the changes to the repository
        repo.git.add(source_data_path)
        repo.index.commit(f'Update CSV {source_data_path}, time {datetime.now()}')
        repo.remotes.origin.push()

        # Temporary success message
        success_placeholder.success(f"Data {source_data_path} saved and pushed to git.")
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