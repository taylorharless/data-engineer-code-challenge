from pathlib import Path

import pandas as pd
from pandaserd import ERD

# Load datasets into DataFrames
attendances_df = pd.read_csv(Path("data/attendances.csv"))
timeslots_df = pd.read_csv(Path("data/timeslots.csv"))
people_df = pd.read_csv(Path("data/people.csv"))
events_df = pd.read_csv(Path("data/events.csv"))

# Assign DataFrames to tables in ERD
erd = ERD()
attendances_table = erd.add_table(attendances_df, "attendances", bg_color="pink")
timeslots_table = erd.add_table(timeslots_df, "timeslots", bg_color="skyblue")
people_table = erd.add_table(people_df, "people", bg_color="skyblue")
events_table = erd.add_table(events_df, "events", bg_color="skyblue")

# Define the relationships between fields in the tables
erd.create_rel("attendances", "timeslots", on="timeslot_id", right_cardinality="*")
erd.create_rel("attendances", "people", on="user_id", right_cardinality="*")
erd.create_rel("attendances", "events", on="event_id", right_cardinality="*")

# Export the schema
erd.write_to_file(Path("docs/schema_output.txt"))
