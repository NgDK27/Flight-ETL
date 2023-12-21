
import asyncio
import configparser
import os
import time
from collections import namedtuple
from kafka import KafkaProducer
from faker import Faker
import json
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 10))
fake = Faker()

def get_registered_user():
    flight_cities = ["Tokyo", "New York", "London"]
    airports = {"Tokyo": "Haneda", "New York": "JFK", "London": "Heathrow"}
    flight_origin = fake.random_element(elements=flight_cities)
    airport = airports[flight_origin]
    flight_cities.remove(flight_origin)
    flight_destination = fake.random_element(elements=flight_cities)

    # Random from list of 30 jobs for easier data analysis purposes
    jobs = ["Engineer", "Doctor", "Teacher", "Nurse", "Accountant", "Lawyer", "Chef", "Police Officer", "Firefighter", "Software Developer",
            "Architect", "Dentist", "Pharmacist", "Physician", "Veterinarian", "Psychologist", "Librarian", "Journalist", "Pilot", "Photographer",
            "Real Estate Agent", "Graphic Designer", "Web Developer", "Animator", "Interior Designer", "Fashion Designer", "Social Worker", "Translator", "Counselor", "Electrician"]


    return {
        "name": fake.name(),
        "address": fake.address(),
        "year": fake.year(),
        "job": fake.random_element(elements=jobs),
        "email": fake.email(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
        "country": fake.country(),
        "city": fake.city(),
        "gender": fake.random_element(elements=('M', 'F')),
        "language_name": fake.language_name(),
        "flight_destination": flight_destination,
        "flight_origin": flight_origin,
        "airport": airport,
    }
def run():
    iterator = 0
    print("Setting up Faker producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER_URL],
    # Encode all values as JSON
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    )
    while True:
        sendit = get_registered_user()
        # adding prints for debugging in logs
        print("Sending new faker data iteration - {}".format(iterator))
        producer.send(TOPIC_NAME, value=sendit)
        print("New faker data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1
        
if __name__ == "__main__":
    run()
