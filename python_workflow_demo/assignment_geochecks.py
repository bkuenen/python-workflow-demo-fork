# %%

import json
import random

import pandas as pd
import requests


def fetch_temperature_data():
    """
    Fetch the latest air and water temperatures for Vlissingen and Hoek van Holland
    using the Rijkswaterstaat OphalenLaatsteWaarnemingen service.

    Returns:
        dict: The fetched data as a dictionary, or None in case of an error.
    """
    url = "https://waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES_DBO/OphalenWaarnemingen"
    api_payload = {
        "Locatie": {"Code": "EIJSDPTN", "X": 690277.449553451, "Y": 5628778.46616937},
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Compartiment": {"Code": "OW"},
                "Grootheid": {"Code": "CONCTTE"},
                "Parameter": {"Code": "Cd"},
            }
        },
        "Periode": {
            "Begindatumtijd": "2000-01-01T00:00:00.000+01:00",
            "Einddatumtijd": "2030-01-01T00:00:00.000+01:00",
        },
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(api_payload), headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching data: {e}")
        return None


def extract_measurements(data):
    """
    Extract measurements from the fetched JSON data.

    Args:
        data (dict): The JSON response containing observations.

    Returns:
        list: A list of measurement dictionaries.
    """
    if not data or "WaarnemingenLijst" not in data:
        print("Invalid or empty data received.")
        return []

    measurements = []
    for row in data["WaarnemingenLijst"]:
        measurements.extend(row.get("MetingenLijst", []))
    return measurements


def process_measurements(measurements):
    """
    Process the extracted measurements into a pandas DataFrame.

    Args:
        measurements (list): A list of measurement dictionaries.

    Returns:
        pd.DataFrame: A DataFrame containing processed measurement data.
    """
    if not measurements:
        print("No measurements to process.")
        return pd.DataFrame()

    df = pd.DataFrame(measurements)
    if "Meetwaarde" in df.columns:
        df["waardes"] = df["Meetwaarde"].apply(lambda x: x.get("Waarde_Numeriek") if isinstance(x, dict) else None)
        df.drop(columns=["Meetwaarde", "WaarnemingMetadata"], inplace=True, errors="ignore")
    return df


def add_validation_errors(df):
    """
    Adds random validation errors to the Tijdstip and waardes columns in the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with Tijdstip and waardes columns.

    Returns:
        pd.DataFrame: DataFrame with introduced validation errors.
    """

    def introduce_error_tijdstip(tijdstip):
        # Randomly return invalid date formats
        errors = [
            "INVALID_DATE",  # Completely invalid
            "2080-10-100 28:28:28",  # Invalid format and impossible date
            "2025-05-12T25:61:00.000+01:00",  # Invalid time
        ]
        return random.choice(errors) if random.random() < 0.5 else tijdstip

    def introduce_error_waardes(waarde):
        # Randomly return invalid values
        errors = [
            "STRING_INSTEAD_OF_NUMBER",  # Invalid type
            random.uniform(1001, 5000),  # Weird large numbers
            None,  # Missing value
        ]
        return random.choice(errors) if random.random() < 0.5 else waarde

    # Apply errors to Tijdstip and waardes columns
    df["Tijdstip"] = df["Tijdstip"].apply(lambda x: introduce_error_tijdstip(x) if random.random() < 0.2 else x)
    df["waardes"] = df["waardes"].apply(lambda x: introduce_error_waardes(x) if random.random() < 0.2 else x)

    return df


def value_validation(df):
    """
    Check if values in dataframe are valid
    """

    for index, row in df.iterrows():
        valid_lst = []
        validity = True

        if row["waardes"] is None:
            validity = False
            print("Invalid data: None")
        elif isinstance(type(row["waardes"]), int):
            validity = False
            print(f"Invalid data type: {type(row['waardes'])}")
        elif int(row["waardes"]) > 1000:
            validity = False
            print("Invalid data: Larger than 1000")

        valid_lst.append(validity)
    df["valid_data"] = valid_lst
    return df


def main():
    """
    Main function to fetch, process, and display the temperature data.
    """
    data = fetch_temperature_data()
    measurements = extract_measurements(data)
    df = process_measurements(measurements)
    df = add_validation_errors(df)

    # Assignment 1
    # Create validation of dataformat, add as function and push to branch
    # Write test to check your function
    # df = dateformat_validation(df)

    # Assignment 2
    # Create validation of dataformat, add as function and push to branch
    # Write test to check your function
    df = value_validation(df)

    print(df.columns)
    print(df)


if __name__ == "__main__":
    main()


# %%
