import streamlit as st


def save_csv(data_df, name):
    # Save the updated DataFrame to a CSV file
    try:
        data_df.to_csv(f"src/data/data_{name}.csv", index=False)
        print(f"Data saved {name}.")
    except Exception as e:
        st.warning(f"Error saving data {name}: {e}")


def save_data(data_df, person, index, name):
    """Save the updated data to a CSV file"""
    # Get the current value from the DataFrame for the specified person and day (index)
    current_value = data_df.loc[index, person]

    # Toggle between 0 and 1
    if current_value == 1:
        data_df.loc[index, person] = 0
    else:
        data_df.loc[index, person] = 1

    save_csv(data_df, name)


def select_all(data_df, person, name):
    """Select all days for the specified person"""
    for i in range(5):
        data_df.loc[i, person] = 1

    save_csv(data_df, name)


def show_planning(data_df_standup, data_df_planning):
    # Define workweek days
    workweek_days = ["Ma", "Di", "Woe", "Do", "Vrij"]

    for person in data_df_standup.columns:
        # Section to select the days of attendance
        st.subheader(f":blue[{person}]")
        col1, col2, col3 = st.columns([2, 2, 6])

        with col1:
            st.write("**Aanwezig**")

            st.button(
                "Select all",
                key=f"planning_{person}_all",
                on_click=select_all,
                args=[data_df_planning, person, "planning"],
            )

            for i, day in enumerate(workweek_days):
                # Get the current value for the day (1 or 0) from the DataFrame
                current_value = data_df_planning.loc[i, person]

                # Create a checkbox for each day, dynamically passing the key and value
                st.checkbox(
                    day,
                    value=bool(current_value),
                    key=f"planning_{person}_{day}",
                    on_change=save_data,
                    args=[data_df_planning, person, i, "planning"],
                )

        with col2:
            st.write("**Standup 9:30**")
            current_value = data_df_standup.loc[0, person]

            st.button(
                "Select all",
                key=f"standup_{person}_all",
                on_click=select_all,
                args=[data_df_standup, person, "standup"],
            )

            for i, day in enumerate(workweek_days):
                # Get the current value for the day (1 or 0) from the DataFrame
                current_value = data_df_standup.loc[i, person]
                # Create a checkbox for each day, dynamically passing the key and value
                st.checkbox(
                    day,
                    value=bool(current_value),
                    key=f"standup_{person}_{day}",
                    on_change=save_data,
                    args=[data_df_standup, person, i, "standup"],
                )
        st.text("")
