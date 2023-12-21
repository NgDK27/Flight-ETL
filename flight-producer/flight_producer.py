import datetime
import configparser
import random
from urllib import response
import requests
import os
import time
from kafka import KafkaProducer
import json
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 200))

config = configparser.ConfigParser()
config.read('booking_service.cfg')
api_credential = config['booking_api_credential']
access_token = api_credential['access_token']

def get_flight_data(departure_date, fromId, toId):
    # The URL of the API endpoint
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/getMinPrice"

    # The headers for the API request, including the API key and host
    headers = {
        "X-RapidAPI-Key": access_token,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    # The parameters for the API request, including the departure date, origin airport, destination airport, and currency code
    querystring = {"fromId": fromId, "toId": toId, "departDate": departure_date, "currency_code": "USD"}

    # Make the API request and store the response
    response = requests.get(url, headers=headers, params=querystring)

    # Parse the JSON response
    data = response.json()

    # Extract the flight data from the response
    flights = data['data']

    # Return the flight data
    return flights


def run():
    # Initialize iterator and flight_id
    iterator = 0
    flight_id = 0

    # Print a message indicating the setup of the Kafka producer
    print("Setting up Flight producer at {}".format(KAFKA_BROKER_URL))

    # Create a Kafka producer instance
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    )
    
    # Set the departure date to 6 days from today
    departure_date = datetime.date.today() + datetime.timedelta(days=6)

    # Define the list of airport pairs for which to fetch flight data
    airports = [("JFK.AIRPORT", "HND.AIRPORT"), ("HND.AIRPORT", "JFK.AIRPORT"), ("LHR.AIRPORT", "HND.AIRPORT"), ("HND.AIRPORT", "LHR.AIRPORT"), ("LHR.AIRPORT", "JFK.AIRPORT"), ("JFK.AIRPORT", "LHR.AIRPORT")]

    # Start an infinite loop to continuously fetch and send flight data
    while True:
        print("Sending new faker data iteration - {}".format(iterator))

        # For each pair of airports
        while airports:
             # Randomly select a pair of airports and remove it from the list
            fromId, toId = random.choice(airports)
            airports.remove((fromId, toId))

            # Fetch flight data
            flight_data = get_flight_data(departure_date.strftime("%Y-%m-%d"), fromId, toId)
            
            # For each flight in the fetched data
            for flight in flight_data:
                # Increment flight_id
                flight_id += 1

                # Extract necessary information from the flight data
                departure_date_value = flight["departureDate"]
                is_cheapest = flight["isCheapest"]
                price_units= flight["price"]["units"]
                price_nanos= flight["price"]["nanos"]
                currency_code= flight["price"]["currencyCode"]
                
                if (fromId, toId) == ("JFK.AIRPORT", "HND.AIRPORT"):
                    fromId, toId = ("New York", "Tokyo")
                elif (fromId, toId) == ("HND.AIRPORT", "JFK.AIRPORT"):
                    fromId, toId = ("Tokyo", "New York")
                elif (fromId, toId) == ("LHR.AIRPORT", "HND.AIRPORT"):
                    fromId, toId = ("London", "Tokyo")
                elif (fromId, toId) == ("HND.AIRPORT", "LHR.AIRPORT"):
                    fromId, toId = ("Tokyo", "London")
                elif (fromId, toId) == ("LHR.AIRPORT", "JFK.AIRPORT"):
                    fromId, toId = ("London", "New York")
                elif (fromId, toId) == ("JFK.AIRPORT", "LHR.AIRPORT"):
                    fromId, toId = ("New York", "London")
                
                # Prepare the final flight data to be sent
                flight_data_final = {
                    'flight_id': flight_id, 
                    'departure_date': departure_date_value, 
                    "from_city": fromId,
                    "to_city": toId,
                    "is_cheapest": is_cheapest, 
                    'price_units': price_units, 
                    'price_nanos': price_nanos, 
                    'currency_code': currency_code 
                }

                # Print the final flight data
                print("New flight data sent")
                print(flight_data_final)

                # Send the final flight data to the Kafka topic
                producer.send(TOPIC_NAME, value=flight_data_final)

                # Print a message indicating the date for which flight data was sent
                print("Flight data sent for date: ", departure_date)

                # Sleep for 5 seconds before fetching the next flight data
                time.sleep(5)

        # Sleep for a specified amount of time before fetching flight data for the next date
        time.sleep(SLEEP_TIME)

        # Print a message indicating the end of the sleep period
        print("Waking up!")

        # Increment the iterator
        iterator += 1

        # Reset the list of airport pairs for the next iteration
        airports = [("JFK.AIRPORT", "HND.AIRPORT"), ("HND.AIRPORT", "JFK.AIRPORT"), ("LHR.AIRPORT", "HND.AIRPORT"), ("HND.AIRPORT", "LHR.AIRPORT"), ("LHR.AIRPORT", "JFK.AIRPORT"), ("JFK.AIRPORT", "LHR.AIRPORT")]
        # Increment the departure date by 11 days
        departure_date += datetime.timedelta(days=11)
if __name__ == "__main__":
    run()
