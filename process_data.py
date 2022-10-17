import json
from pathlib import Path

import pandas as pd


def create_child_dataframe(
    child_columns: list,
    dataset_prefix: str,
    columns_to_rename: dict,
    final_field_order: list,
    unique_column: str,
    parent_df: pd.DataFrame = parent_df,
) -> pd.DataFrame:
    """
    Create a child copy of the parent DataFrame, transform it, and return the child DataFrame.
    """

    # Copy parent DataFrame
    child_df = parent_df.copy()

    # Select a subset of necessary fields
    child_df = child_df[[*child_columns]]

    # Remove the dataset's prefix from all field names
    child_df.columns = child_df.columns.str.replace(dataset_prefix, "", regex=False)

    # Any remaining columns that have a period in their name belong in a separate table
    # that is not required in this activity, so filter them out
    child_df = child_df[[col for col in child_df.columns if "." not in col]]

    # Rename some columns for clarity
    child_df = child_df.rename(columns=columns_to_rename)

    # Drop all unneeded columns, and recorder the remaining ones
    child_df = child_df[final_field_order]

    # Drop all duplicates in the 'unique_column' column
    child_df = child_df.drop_duplicates(unique_column, ignore_index=True)

    return child_df


#############################
#  CREATE PARENT DATAFRAME  #
#############################

# Import the Attendances JSON file as a Python dictionary
with open(Path("data/attendances.json")) as f:
    attendances_json = json.loads(f.read())

# Load the Attendances data into a Pandas DataFrame and flatten all nested fields
parent_df = pd.json_normalize(attendances_json)

# Drop all rows that contain a null value in any of the 'id','timeslot.id','event.id', or 'person.user_id' columns
parent_df = parent_df.dropna(
    axis=0, how="any", subset=["id", "timeslot.id", "event.id", "person.user_id"]
)

# Convert fields to integers that Pandas incorrectly cast as floats
parent_df = parent_df.astype(
    dtype={"id": "int64", "timeslot.id": "int64", "event.id": "int64"}
)

##################################
#  CREATE ATTENDANCES DATAFRAME  #
##################################

# Copy parent DataFrame
attendances_df = parent_df.copy()

# Select a subset of necessary fields
attendances_df = attendances_df[
    [
        *[col for col in parent_df.columns if "." not in col],
        "person.user_id",
        "event.id",
        "timeslot.id",
    ]
]

# Rename some columns for clarity
attendances_df = attendances_df.rename(
    columns={"id": "attendance.id", "person.user_id": "user_id"}
)

# Change all periods to underscores in all column names
attendances_df.columns = attendances_df.columns.str.replace(".", "_", regex=False)

# Drop all unneeded columns, and recorder the remaining ones
attendances_df = attendances_df[
    [
        "attendance_id",
        "event_id",
        "timeslot_id",
        "user_id",
        "created_date",
        "modified_date",
        "rating",
        "custom_signup_field_values",
        "feedback",
        "status",
        "attended",
    ]
]


##################################
#  CREATE OTHER CHILD DATAFRAMES #
##################################

timeslots_df_params = dict(
    child_columns=[col for col in parent_df.columns if "timeslot." in col],
    dataset_prefix="timeslot.",
    columns_to_rename={"id": "timeslot_id"},
    final_field_order=[
        "timeslot_id",
        "end_date",
        "start_date",
        "is_full",
        "instructions",
    ],
    unique_column="timeslot_id",
)

people_df_params = dict(
    child_columns=[col for col in parent_df.columns if "person." in col],
    dataset_prefix="person.",
    columns_to_rename={},
    final_field_order=[
        "user_id",
        "given_name",
        "family_name",
        "sms_opt_in_status",
        "created_date",
        "modified_date",
        "blocked_date",
    ],
    unique_column="user_id",
)

events_df_params = dict(
    child_columns=[col for col in parent_df.columns if "event." in col],
    dataset_prefix="event.",
    columns_to_rename={"id": "event_id"},
    final_field_order=[
        "event_id",
        "accessibility_notes",
        "approval_status",
        "created_by_volunteer_host",
        "modified_date",
        "event_campaign",
        "instructions",
        "timezone",
        "virtual_action_url",
        "featured_image_url",
        "browser_url",
        "tags",
        "title",
        "event_type",
        "summary",
        "address_visibility",
        "high_priority",
        "created_date",
        "accessibility_status",
        "visibility",
        "timeslots",
        "is_virtual",
        "description",
    ],
    unique_column="event_id",
)

timeslots_df = create_child_dataframe(**timeslots_df_params, parent_df=parent_df)
people_df = create_child_dataframe(**people_df_params, parent_df=parent_df)
events_df = create_child_dataframe(**events_df_params, parent_df=parent_df)


##############################
#  EXPORT DATAFRAMES TO CSV  #
##############################

# These functions use Path objects as the export destination to support cross-platform compatibility

attendances_df.to_csv(Path("data/attendances.csv"), index=False)
timeslots_df.to_csv(Path("data/timeslots.csv"), index=False)
people_df.to_csv(Path("data/people.csv"), index=False)
events_df.to_csv(Path("data/events.csv"), index=False)
