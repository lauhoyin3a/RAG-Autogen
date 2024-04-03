import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables from .env file
load_dotenv()


def call_serpapi(query):
    api_key = os.getenv("SERP_API_KEY")

    # Define the base URL for the SerpApi
    base_url = "https://serpapi.com/search"

    # Set the query parameters
    params = {
        'q': query,
        'engine': 'google',
        'api_key': api_key,
        'output': 'json'
    }

    try:
        # Send a GET request to the SerpApi
        response = requests.get(base_url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Retrieve and parse the JSON response
            json_data = response.json()

            # Save the JSON response to a file
            filename = "search_results.json"
            with open(filename, 'w') as file:
                json.dump(json_data, file, indent=4)

            print(f"Search results saved to {filename}")
        else:
            # Handle any errors
            print("Error: ", response.status_code)

    except requests.RequestException as e:
        # Handle connection errors
        print("Error: ", e)


# Example usage
query = "What's your overall recommendation related to global equity strategies"
call_serpapi(query)