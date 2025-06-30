import streamlit as st
import pandas as pd
import datetime
import threading

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
        
        st.success(f"Data locally saved for week {week}.")
    except Exception as e:
        st.warning(f"Error saving data: {e}")


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
                st.session_state[week_key] = group.copy()


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
            
            data_editor2 = st.data_editor(
                st.session_state[
                    week_key
                ],  # Use the session state version of the group
                hide_index=True,  # Hide the index column
                key=f"data_editor_dev_{week}_{year}",  # Unique key for each editor
                column_config=column_config,  # Disable editing for 'Datum'
            )

            data_editor2 = data_editor2.fillna("-")

            # If data is changed, update the CSV file
            if not data_editor2.equals(st.session_state[week_key]):
                # Call update_csv to save the changes for the specific week using the unique name
                update_csv(data_editor2, week, data_url)
                # ✅ Update session state with the latest version
            
            st.session_state[week_key] = data_editor2.copy()