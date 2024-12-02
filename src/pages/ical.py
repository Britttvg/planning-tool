import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import io


# Function to create an iCal file from the DataFrame
def create_ical(data_url):
    data_planning = pd.read_csv(data_url)
    cal = Calendar()

    for _, row in data_planning.iterrows():
        date = datetime.strptime(row["Datum"], "%Y-%m-%d")

        # Add events for each person
        for person in data_planning.columns:
            if (
                row[person] != "-"
                and row[person] is not None
                and person not in ["Datum", "Dag", "Week", "Jaar"]
            ):
                event = Event()
                event.add("summary", f"{row[person]} ({person})")
                event.add("dtstart", date)
                event.add("dtend", date + timedelta(days=1))  # End of the day
                event.add("description", f"{person}: {row[person]}")
                cal.add_component(event)

    # Write the iCal data to a bytes buffer
    ical_bytes = io.BytesIO()
    ical_bytes.write(cal.to_ical())
    ical_bytes.seek(0)
    return ical_bytes
