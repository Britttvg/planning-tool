import streamlit as st
import pandas as pd
import datetime
import git
import os
import threading
from dotenv import load_dotenv


# Mapping for full day names to abbreviations
day_abbreviations = {
    "Maandag": "Ma",
    "Dinsdag": "Di",
    "Woensdag": "Wo",
    "Donderdag": "Do",
    "Vrijdag": "Vr",
    "Zaterdag": "Za",
    "Zondag": "Zo",
}

column_config = {
    "Dag": st.column_config.TextColumn(disabled=True),
    "Datum": st.column_config.DateColumn(disabled=True, format="DD-MM-YYYY"),
    "Week": st.column_config.NumberColumn(disabled=True),
    "Jaar": st.column_config.NumberColumn(disabled=True, format="%d"),
    # All other columns can remain editable, so no need to specify them here
}

# Global timer reference
push_timer = None

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Load environment variables from .env file
load_dotenv()

# Concatenate data from all weeks into a single DataFrame and offer a download button
def download_all_weeks_csv(data_url):
    """Function to concatenate all weeks' data into a single CSV for download."""
    # Load all data from the CSV
    all_data = pd.read_csv(data_url)

    # Convert 'Datum' to datetime if needed
    if all_data["Datum"].dtype == "object":
        all_data["Datum"] = pd.to_datetime(all_data["Datum"], dayfirst=False)

    # Prepare CSV for download
    csv_data = all_data.to_csv(index=False).encode("utf-8")

    base_name = data_url.split("/")[-1].split(".")[0]
    # Download button for the entire data CSV
    st.download_button(
        label="Download alle data (CSV)",
        icon=":material/download:",
        data=csv_data,
        file_name=f"all_weeks_{base_name}.csv",
        mime="text/csv",
    )

def commit_and_push_changes(data_url, week):
    """Function to commit and push changes to GitHub."""
    try:
        repo = git.Repo()
        repo.git.remote("set-url", "origin", f"https://{GITHUB_TOKEN}@github.com/Britttvg/planning-tool.git")
        repo.git.checkout('main')
        repo.remotes.origin.pull()

        # Add, commit, and push the changes to the repository
        repo.git.add(data_url)
        repo.index.commit(f'Update CSV {data_url}, week {week}, time {datetime.datetime.now()}')
        repo.remotes.origin.push()

        st.success(f"Data saved and pushed for week {week}.")
    except Exception as e:
        st.warning(f"Error saving data: {e}")

def start_push_timer(data_url, week, interval=300):
    """Function to start a timer that commits and pushes changes after `interval` seconds."""
    # If the timer is already running, don't start it again
    if "timer_started" not in st.session_state or not st.session_state.timer_started:
        st.session_state.timer_started = True
        threading.Timer(interval, commit_and_push_changes, [data_url, week]).start()
        st.info(f"Timer started. The commit will be pushed in {interval} seconds.")
    else:
        st.warning("Timer is already running. It will not be restarted.")
    
def update_csv(edited_data, week, data_url):
    """Function to update the CSV file with the edited data."""
    try:
        original_data = pd.read_csv(data_url)
        
        original_data['Datum'] = pd.to_datetime(original_data['Datum']).dt.date.astype(str)
        edited_data['Datum'] = pd.to_datetime(edited_data['Datum']).dt.date.astype(str)
        
        # Overwrite the relevant rows in the original_data with the edited group
        original_data.update(edited_data)

        # Save the concatenated DataFrame back to the CSV file
        original_data.to_csv(data_url, index=False)
        
        commit_and_push_changes(data_url, week)
        
        # Restart the push timer to push changes every 5 minutes (300 seconds)
        # start_push_timer(data_url, week, interval=300)
        
        st.success(f"Data saved for week {week}.")
    except Exception as e:
        st.warning(f"Error saving data: {e}")


# def drop_rows(data_url, data, indices):
#     """Function to drop rows that are from past weeks and save the updated data."""
#     new_week_data = data.drop(indices, axis=0)
#     data.reset_index(drop=True, inplace=True)
#     new_week_data.to_csv(data_url, index=False)
#     st.rerun()
#     return new_week_data


def reset_session_state_week():
    """Function to reset session state for week data."""
    for key in list(st.session_state.keys()):
        if key.startswith("week_"):
            del st.session_state[key]


def highlight_apeldoorn(val):
    """Function to apply color styling to cells containing 'Apeldoorn'."""
    if "Apeldoorn" in str(val) or "apeldoorn" in str(val):
        return (
            f'<span style="background-color: #A9D08E; font-weight: bold">{val}</span>'
        )
    elif "Thuis" in str(val) or "thuis" in str(val):
        return f'<span style="background-color: #9BC2E6;">{val}</span>'
    elif ("Vrij" in str(val) or "vrij" in str(val)) and not "Vrijdag" in str(val):
        return f'<span style="background-color: #F4B084;">{val}</span>'
    return val


def toggle_view_state(view_key, week_key, group):
    st.session_state[view_key] = not st.session_state[view_key]
    st.session_state[week_key] = group.copy()


def show_excel(data_url, ical_file):

    st.download_button(
        label="iCal",
        icon=":material/download:",
        data=ical_file,
        file_name="data_planning.ics",
        mime="text/calendar",
    )

    # Save the data_url choice in session state
    if (
        "data_url_choice" not in st.session_state
        or st.session_state["data_url_choice"] != data_url
    ):
        st.session_state["data_url_choice"] = data_url

        # Reset session state for week data if data_url choice changes
        reset_session_state_week()

    # Display today's date
    st.write(
        f"**:calendar: Vandaag**: {datetime.datetime.now().date().strftime('%A %d-%m-%Y')}"
    )

    saved_data = pd.read_csv(data_url)

    # Convert 'Datum' to datetime
    saved_data["Datum"] = pd.to_datetime(saved_data["Datum"], dayfirst=False)

    # Extract week number and year
    saved_data["Week"] = saved_data["Datum"].dt.isocalendar().week
    saved_data["Jaar"] = saved_data["Datum"].dt.year.astype(int)

    # Identify the indices of rows to drop (where week number < current week)
    # if (saved_data["Week"] < datetime.datetime.now().isocalendar().week).any():
    #     saved_data = drop_rows(
    #         data_url,
    #         saved_data.iloc[1:],  # Skip the headers
    #         saved_data.iloc[1:][
    #             saved_data["Week"] < datetime.datetime.now().isocalendar().week
    #         ].index,
    #     )

    # Group by week (year currently not used)
    weeks = saved_data.groupby(["Jaar", "Week"])

    for (_, week), group in weeks:
        if week >= datetime.datetime.now().isocalendar().week:
            # Display a subheader for each week
            st.subheader(f"Week {week}")

            # Count occurrences of 'Apeldoorn' per day of the week for all relevant columns
            occurrences_per_day = {}

            # Get all columns except 'Dag' and 'Datum'
            relevant_columns = group.columns.difference(["Dag", "Datum"])

            # Track each week separately in session state
            week_key = f"week_{week}"

            if week_key not in st.session_state:
                st.session_state[week_key] = group.copy()

            # Create a toggle for view mode
            view_key = f"view_{week}"
            if view_key not in st.session_state:
                st.session_state[view_key] = False  # Default is editable mode

            # Toggle button to switch between views
            st.toggle(
                label=":art:",
                value=st.session_state[view_key],
                key=f"toggle_{week}",
                on_change=toggle_view_state,
                args=(view_key, week_key, group),
            )

            for index, row in group.iterrows():
                day = row["Dag"]  # Assuming 'Dag' column contains the day of the week
                if day not in occurrences_per_day:
                    occurrences_per_day[day] = 0  # Initialize count for the day

                # Check each relevant column for occurrences of 'Apeldoorn'
                for col in relevant_columns:
                    if "Apeldoorn" in str(row[col]) or "apeldoorn" in str(row[col]):
                        occurrences_per_day[day] += 1  # Increment count if found

            # Prepare the output string to display counts in a single line
            occurrences_str = " | ".join(
                f"**{day_abbreviations.get(day, day)} :{'red' if count == 0 else 'green'}[{count}]**"
                for day, count in occurrences_per_day.items()
            )

            # Display the counts in a single line
            st.write(f"**Apeldoorn** | {occurrences_str} |")
            # Display based on the current view mode
            if st.session_state[view_key]:

                # View mode: Display with color styling for 'Apeldoorn'
                styled_data = group.copy().astype(
                    str
                )  # Ensure all data is string for replacement
                styled_data["Datum"] = pd.to_datetime(
                    styled_data["Datum"], format="%Y-%m-%d", errors="coerce"
                )
                # Format the dates to "DD-MM-YYYY", leave other values unchanged
                styled_data["Datum"] = (
                    styled_data["Datum"].dt.strftime("%d-%m-%Y").fillna(group["Datum"])
                )
                styled_data = styled_data.map(highlight_apeldoorn)

                # Render the DataFrame as HTML using st.write()
                st.write(
                    styled_data.to_html(escape=False, index=False),
                    unsafe_allow_html=True,
                )

            else:
                data_editor2 = st.data_editor(
                    st.session_state[
                        week_key
                    ],  # Use the session state version of the group
                    hide_index=True,  # Hide the index column
                    key=f"data_editor_dev_{week}",  # Unique key for each editor
                    column_config=column_config,  # Disable editing for 'Datum'
                )

                data_editor2 = data_editor2.fillna("-")

                # If data is changed, update the CSV file
                if not data_editor2.equals(st.session_state[week_key]):
                    # Call update_csv to save the changes for the specific week using the unique name
                    update_csv(data_editor2, week, data_url)
    # Call the download function after processing all weeks in `show_excel`
    download_all_weeks_csv(data_url)
