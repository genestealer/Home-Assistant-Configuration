# ==============================================================================
# check_stock.py
# ==============================================================================
# This script checks for medication stock availability at nearby pharmacies.
# It uses the Pyscript service in Home Assistant, and gets the current location
# from a given entity (e.g., `person.richard`). It calculates the distance from
# the current location and queries an API for stock availability at pharmacies
# within a specified radius (default 30 miles).
#
# Requirements:
# - Home Assistant with Pyscript installed
# - Medication stock checker API
#
# The script performs the following tasks:
# - Get the current location (latitude and longitude) of the user
# - Query pharmacies within a specified radius for medication availability
# - Update a Home Assistant sensor based on the stock availability
#
# Author: Richard Huish
# Last updated: 2024 11 21
# ==============================================================================

import aiohttp
from math import radians, sin, cos, sqrt, atan2

# ==============================================================================
# Haversine formula to calculate the great-circle distance between two points
# on the Earth, specified by their latitude and longitude. This is used to 
# calculate the distance between the user's location and nearby pharmacies.
# ==============================================================================
def calculate_distance(lat1, lon1, lat2, lon2):

    # Calculate the great-circle distance in miles between two points on the Earth.

    # Parameters:
    #     lat1, lon1 (float): Coordinates of the first point (user's location).
    #     lat2, lon2 (float): Coordinates of the second point (pharmacy location).

    # Returns:
    #     float: Distance in miles between the two points.

    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ==============================================================================
# Pyscript service: check_stock
# This function checks for stock availability at pharmacies within a specified
# distance from the user's current location. The stock check is performed by
# calling an external API, and the results are stored in a Home Assistant sensor.
# ==============================================================================
@service
async def check_stock(base_lat=0.0, base_lon=0.0, distance=30):

    # Check medication stock and create a sensor in Home Assistant.

    # This function uses aiohttp to perform non-blocking HTTP requests, as blocking requests are
    # not supported in Pyscript due to its execution in Home Assistant's event loop.
    
    # Parameters:
    #   - base_lat (float): Latitude of the location to calculate distance from (required).
    #   - base_lon (float): Longitude of the location to calculate distance from (required).
    #   - distance (float): Radius in miles for filtering stores (defaults to 30 miles if not provided).

    # If you call the service without passing `distance`, it will default to 30 miles.

    log.info(f"Starting stock check with distance: {distance} miles from location: ({base_lat}, {base_lon})")

    # =======================================================================
    # API request setup: The payload includes medication details, and the headers
    # define the request format to the stock checker API.
    # =======================================================================
    api_url = "https://pharmacystockchecker.com/getStock"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    payload = {
        "Medications": [{"name": "Concerta XL", "strengths": [{"id": "11", "strength": "36mg"}]}],
        "StockLevel": "G",  # "G" for good stock level
    }

    log.debug(f"Payload for API call: {payload}")

    try:
        # =======================================================================
        # Make an asynchronous HTTP POST request to the stock checker API.
        # The response is expected to contain stock data in JSON format.
        # =======================================================================
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"API call failed with status: {response.status}")
                # Directly parse the JSON response (not needing 'await' as it’s synchronous in this context)
                stock_data = response.json()
                log.debug(f"Received stock data: {stock_data}")

        # =======================================================================
        # Filter pharmacies within the specified distance from the user's location.
        # This checks the distance from the user's current coordinates to each pharmacy.
        # =======================================================================
        nearby_stores = [
            {
                **store,  # Add store information
                "distance": calculate_distance(base_lat, base_lon, store["lat"], store["long"]),  # Calculate distance
            }
            for store in stock_data
            if calculate_distance(base_lat, base_lon, store["lat"], store["long"]) <= distance  # Check if within radius
        ]
        log.info(f"Found {len(nearby_stores)} stores within {distance} miles")

        # =======================================================================
        # Update the Home Assistant sensor with the result (on if stock is found, off otherwise).
        # The stores and their details are included in the sensor attributes.
        # =======================================================================
        has_stock = bool(nearby_stores)  # True if there are any stores with stock
        state.set(
            "sensor.medication_stock",  # The sensor entity to update
            "on" if has_stock else "off",  # Set the sensor state
            {
                "stores": nearby_stores,  # List of stores with stock
                "location": {"lat": base_lat, "lon": base_lon},  # User's location
                "distance": distance,  # Search radius
                "has_stock": has_stock,  # Stock availability status
            },
        )
        # Set binary sensor indicating no error
        state.set("binary_sensor.medication_check_error", "off")
        log.debug(f"Sensor updated: {'on' if has_stock else 'off'}")
    
    except Exception as e:
        # =======================================================================
        # Handle errors: If the API request fails or any other error occurs, 
        # log the error and update the sensor to indicate a failure.
        # =======================================================================
        log.error(f"Error checking stock: {e}")
        state.set(
            "sensor.medication_stock",  # The sensor entity to update
            "error",  # State indicating an error
            {
                "error": str(e),  # Log the error message
                "location": {"lat": base_lat, "lon": base_lon},  # User's location
                "distance": distance,  # Search radius
            },
        )

        # Set binary sensor indicating an error
        state.set("binary_sensor.medication_check_error", "on")
