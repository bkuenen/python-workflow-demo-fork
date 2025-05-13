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


import pandas as pd


def dateformat_validation_and_repair(df):
    """
    Validate and repair the date format in the Tijdstip column of the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with Tijdstip column.

    Returns:
        pd.DataFrame: DataFrame with validation results and repaired values.
    """

    # Example validation: Check if the date format is correct
    def validate_and_repair_date_format(tijdstip):
        try:
            # Validate the strict format
            valid_date = pd.to_datetime(tijdstip, format="%Y-%m-%dT%H:%M:%S.%f%z")
            return {"valid": True, "repaired": valid_date.isoformat()}
        except ValueError:
            # Attempt to repair with flexible parsing
            try:
                repaired_date = pd.to_datetime(tijdstip, errors="coerce")
                if pd.notnull(repaired_date):
                    return {"valid": False, "repaired": repaired_date.isoformat()}
            except Exception:
                pass
            # Return as invalid with no repair if everything fails
            return {"valid": False, "repaired": None}

    # Apply the validation and repair function
    validation_results = df["Tijdstip"].apply(validate_and_repair_date_format)

    # Extract validation and repaired columns
    df["date_validation"] = validation_results.apply(lambda x: x["valid"])
    df["repaired_Tijdstip"] = validation_results.apply(lambda x: x["repaired"])

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
    df = dateformat_validation_and_repair(df)

    # Assignment 2
    # Create validation of dataformat, add as function and push to branch
    # Write test to check your function
    # df = value_validation(df)

    print(df.columns)
    print(df)


if __name__ == "__main__":
    main()

# %%
