import datetime
import gzip
import os
import re
import sys

import pandas as pd
from cassandra.cluster import BatchStatement, Cluster, ConsistencyLevel
from cassandra.query import dict_factory

tablename = os.getenv("weather.table", "weatherreport")
twittertable = os.getenv("twittertable.table", "twitterdata")
fakertable = os.getenv("fakertable.table", "fakerdata")
flighttable = os.getenv("flighttable.table", "flightdata")


CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else 'localhost'
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'

WEATHER_TABLE = os.environ.get("WEATHER_TABLE") if os.environ.get("WEATHER_TABLE") else 'weather'
TWITTER_TABLE = os.environ.get("TWITTER_TABLE") if os.environ.get("TWITTER_TABLE") else 'twitter'
FAKER_TABLE = os.environ.get("FAKER_TABLE") if os.environ.get("FAKER_TABLE") else 'faker'
FLIGHT_TABLE = os.environ.get("FLIGHT_TABLE") if os.environ.get("FLIGHT_TABLE") else 'flight'


def getWeatherDF():
    return getDF(WEATHER_TABLE)
def getTwitterDF():
    return getDF(TWITTER_TABLE)
def getFakerDF():
    return getDF(FAKER_TABLE)
def getFlightDF():
    return getDF(FLIGHT_TABLE)

def getDF(source_table):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    if source_table not in (WEATHER_TABLE, TWITTER_TABLE, FAKER_TABLE, FLIGHT_TABLE):
        return None

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    cqlquery = "SELECT * FROM " + source_table + ";"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    action = sys.argv[1]
    target = sys.argv[2]
    targetfile = sys.argv[3]
    if action == "get":
        getDF(target)


