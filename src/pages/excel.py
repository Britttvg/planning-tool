import streamlit as st
import pandas as pd
import datetime
import uuid  # Import the uuid library


def update_csv(edited_data, original_data, week, data_url):
    try:
        # Overwrite the relevant rows in the original_data with the edited group
        original_data.update(edited_data)

        # Save the concatenated DataFrame back to the CSV file
        original_data.to_csv(data_url, index=False)
        st.success(f"Data saved for week {week}.")
    except Exception as e:
        st.warning(f"Error saving data: {e}")


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
    # Save the data_url choice in session state
    if (
        "data_url_choice" not in st.session_state
        or st.session_state["data_url_choice"] != data_url
    ):
        st.session_state["data_url_choice"] = data_url

        # Reset session state for week data if data_url choice changes
        for key in list(st.session_state.keys()):
            if key.startswith("week_"):
                del st.session_state[key]

    # Display today's date
    st.write(
        f"**:calendar: Today**: {datetime.datetime.now().date().strftime('%A %d-%m-%Y')}"
    )

    saved_data = pd.read_csv(data_url)

    # Convert 'Datum' to datetime
    saved_data["Datum"] = pd.to_datetime(saved_data["Datum"], format="%d-%m-%Y")

    # Extract week number and year
    saved_data["Week"] = saved_data["Datum"].dt.isocalendar().week
    saved_data["Year"] = saved_data["Datum"].dt.year.astype(int)

    # Identify the indices of rows to drop (where week number is less than min_week)
    saved_data = saved_data[
        saved_data["Week"] >= datetime.datetime.now().isocalendar().week
    ]

    # Format 'Datum' back to string format
    saved_data["Datum"] = saved_data["Datum"].dt.strftime("%d-%m-%Y")

    # Group by week (year currently not used)
    weeks = saved_data.groupby(["Year", "Week"])

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

    for (_, week), group in weeks:
        # Display a subheader for each week
        if week != datetime.datetime.now().isocalendar()[1]:
            st.subheader(f"Week {week}")

        # Count occurrences of 'Apeldoorn' per day of the week for all relevant columns
        occurrences_per_day = {}

        # Get all columns except 'Dag' and 'Datum'
        relevant_columns = group.columns.difference(["Dag", "Datum"])

        for index, row in group.iterrows():
            day = row["Dag"]  # Assuming 'Dag' column contains the day of the week
            if day not in occurrences_per_day:
                occurrences_per_day[day] = 0  # Initialize count for the day

            # Check each relevant column for occurrences of 'Apeldoorn'
            for col in relevant_columns:
                if "Apeldoorn" in str(row[col]):
                    occurrences_per_day[day] += 1  # Increment count if found

        # Prepare the output string to display counts in a single line
        occurrences_str = " | ".join(
            f"**{day_abbreviations.get(day, day)} :{'red' if count == 0 else 'green'}[{count}]**"
            for day, count in occurrences_per_day.items()
        )

        # Display the counts in a single line
        st.write(f":round_pushpin: **Apeldoorn**: | {occurrences_str} |")

        # Track each week separately in session state
        week_key = f"week_{week}"

        if week_key not in st.session_state:
            st.session_state[week_key] = group.copy()

        # Create a toggle for view mode
        view_key = f"view_{week}"
        if view_key not in st.session_state:
            st.session_state[view_key] = False  # Default is editable mode

        # Toggle button to switch between views
        if st.button(
            (f"View mode" if not st.session_state[view_key] else f"Edit mode"),
            key=f"toggle_{week}",
        ):
            st.session_state[view_key] = not st.session_state[view_key]
            st.session_state[week_key] = group.copy()
            st.rerun()  # Toggle the state

        # Display based on the current view mode
        if st.session_state[view_key]:
            # View mode: Display with color styling for 'Apeldoorn'
            styled_data = group.copy().astype(
                str
            )  # Ensure all data is string for replacement
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
                hide_index=True,  # This will remove the index numbers from the first column
                key=f"data_editor_dev_{week}",  # Unique key for each editor
            )

            data_editor2 = data_editor2.fillna("-")

            # If data is changed, update the CSV file
            if not data_editor2.equals(st.session_state[week_key]):

                # Call update_csv to save the changes for the specific week using the unique name
                update_csv(data_editor2, saved_data, week, data_url)
