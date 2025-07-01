import streamlit as st
import pandas as pd
import datetime
import os

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

def load_week_data_or_original(group, week, year):
    """Try loading the edited week data from tmp_data; fall back to original."""
    filename = f"week_{week}_{year}.csv"
    file_path = os.path.join("tmp_data", filename)
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            st.warning(f"Error loading saved file for week {week}: {e}")
    return group.copy()

 
def save_edited_week_csv(edited_data, week, year):
    """Save the edited week data to a separate file in tmp_data/."""
    try:
        os.makedirs("tmp_data", exist_ok=True)
        filename = f"week_{week}_{year}.csv"
        file_path = os.path.join("tmp_data", filename)
        edited_data.to_csv(file_path, index=False)
        st.success(f"Data saved for week {week}, {year}")
    except Exception as e:
        st.error(f"Failed to save week {week}, {year}: {e}")


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


def show_excel(data_url):
    # Call the download function after processing all weeks in `show_excel`
    download_all_weeks_csv(data_url)
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

    # Group by week (year currently not used)
    weeks = saved_data.groupby(["Jaar", "Week"])
    # Sort by year and week to display them in chronological order
    sorted_weeks = sorted(weeks, key=lambda x: (x[0], x[1]))

    for (year, week), group in sorted_weeks:
        if week >= datetime.datetime.now().isocalendar().week or (year > datetime.datetime.now().isocalendar().year and week <= datetime.datetime.now().isocalendar().week):
            # Display a subheader for each week
            st.subheader(f"Week {week}")

            # Count occurrences of 'Apeldoorn' per day of the week for all relevant columns
            occurrences_per_day = {}

            # Get all columns except 'Dag' and 'Datum'
            relevant_columns = group.columns.difference(["Dag", "Datum"])

            # Track each week separately in session state
            week_key = f"week_{week}_{year}"

            if week_key not in st.session_state:
                st.session_state[week_key] = load_week_data_or_original(group, week, year)

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
            st.write(f"**Apeldoorn:** {occurrences_str}")

            # Render the data editor
            data_editor2 = st.data_editor(
                st.session_state[week_key],  # Live binding to session state
                hide_index=True,
                key=f"data_editor_dev_{week}_{year}",
                column_config=column_config,
            )

            data_editor2 = data_editor2.fillna("-")

            # Detect changes by comparing session state with the new data
            if not data_editor2.equals(st.session_state[week_key]):
                # Save edited version
                save_edited_week_csv(data_editor2, week, year)
