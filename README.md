
## Demo video

https://rmiteduau.sharepoint.com/:v:/s/Adv547/EdDiCWWmjOFMoW_3fZpH2CgBSse71WuYjCp0GvrPkuHZXA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&e=tEPvf0

# Quickstart instructions

You need to register for some APIs to use with this. Sample API keys are given, but it can be blocked if too many users are running this and it will charge money for over-used of API calls.

OpenWeatherMap API: https://openweathermap.org/api 

Booking com API: https://rapidapi.com/DataCrawler/api/booking-com15

After obtaining the API keys, please update the files "owm-producer/openweathermap_service.cfg" and "flight-producer/booking_service.cfg" accordingly.

I will use booking api to query for the min price of 11 flights of different flight paths (from airport to airport, there are 3 airport used in the application) within a departure date param (5 days before and 5 days after the departure date and the departure date). The departure date used will be the current day running this project + 6 days in the future and after each iteration, the departure date will increased by 11 days


## Create docker networks

```bash
$ docker network create kafka-network                         # create a new docker network for kafka cluster (zookeeper, broker, kafka-manager services, and kafka connect sink services)
$ docker network create cassandra-network                     # create a new docker network for cassandra. (kafka connect will exist on this network as well in addition to kafka-network)
```
## Starting Cassandra

Cassandra is setup so it runs keyspace and schema creation scripts at first setup so it is ready to use.
```bash
$ docker-compose -f cassandra/docker-compose.yml up -d
```

## Starting Kafka on Docker
```bash
$ docker-compose -f kafka/docker-compose.yml up -d            # start single zookeeper, broker, kafka-manager and kafka-connect services
$ docker ps -a                                                # sanity check to make sure services are up: kafka_broker_1, kafka-manager, zookeeper, kafka-connect service
```

## Create the correct table in Cassandra

First login into Cassandra's container with the following command or open a new CLI from Docker Desktop if you use that.
```bash
$ docker exec -it cassandra bash
```
Once loged in, bring up cqlsh with this command.
```bash
$ cqlsh --cqlversion=3.4.4 127.0.0.1 #make sure you use the correct cqlversion
```

Run this script

```bash
# This script will create table for the data received from faker and booking api

USE kafkapipeline;
CREATE TABLE IF NOT EXISTS fakerdata (
    name text,
    address text,
    year text,
    job text,
    email text PRIMARY KEY,
    date_of_birth text,
    country text,
    city text,
    gender text,
    language_name text,
    flight_destination text,
    flight_origin text,
    airport text
);

CREATE TABLE IF NOT EXISTS flightdata (
    flight_id int PRIMARY KEY,
    departure_date text,
    from_city text,
    to_city text,
    is_cheapest boolean,
    price_units bigint,
    price_nanos bigint,
    currency_code text,
);
```



> **Note:** 
Kafka-Manager front end is available at http://localhost:9000

You can use it to create cluster to view the topics streaming in Kafka.


IMPORTANT: You have to manually go to CLI of the "kafka-connect" container and run the below comment to start the Cassandra sinks.
```
./start-and-wait.sh
```

## Starting Producers
```bash
$ docker-compose -f owm-producer/docker-compose.yml up -d     # start the producer that retrieves open weather map

$ docker-compose -f faker-producer/docker-compose.yml up -d # start the producer for faker

$ docker-compose -f flight-producer/docker-compose.yml up -d     # start the producer that retrieves flight data
```


## Starting the consumers

```bash
$ docker-compose -f consumers/docker-compose.yml up       # start the consumers
```

## Check that data is arriving to Cassandra

Go back to terminal in Cassandra and use the below commands
```bash
cqlsh:kafkapipeline> select * from weatherreport;

cqlsh:kafkapipeline> select * from fakerdata;

cqlsh:kafkapipeline> select * from flightdata;
```

And that's it! you should be seeing records coming in to Cassandra. Feel free to play around with it by bringing down containers and then up again to see the magic of fault tolerance!


## Visualization

Run the following command and go to http://localhost:8888 to run the visualization notebook accordingly

```bash
$ docker-compose -f data-vis/docker-compose.yml up -d
```
On http://localhost:8888 you can navigate to the jupyter notebook file to run the cells and analyze the charts, graphs provided

Chart 1: using faker and flight data

City of Origin vs Average Flight Price

![alt text](https://spkuounwjckbvmdirseo.supabase.co/storage/v1/object/public/avatars/chart1.png)

Chart 2: using faker and flight data

Distribution of Cheapest Flights by Jo

![alt text](https://spkuounwjckbvmdirseo.supabase.co/storage/v1/object/public/avatars/chart2.png)

Chart 3: using weather and faker data

Humidity Distribution at location by Job

![alt text](https://spkuounwjckbvmdirseo.supabase.co/storage/v1/object/public/avatars/chart3.png)

## Teardown

To stop all running kakfa cluster services

```bash
$ docker-compose -f data-vis/docker-compose.yml down           # stop visualization node

$ docker-compose -f consumers/docker-compose.yml down          # stop the consumers

$ docker-compose -f owm-producer/docker-compose.yml down       # stop open weather map producer

$ docker-compose -f faker-producer/docker-compose.yml down     # stop faker producer

$ docker-compose -f flight-producer/docker-compose.yml down    # stop flight producer

$ docker-compose -f kafka/docker-compose.yml down              # stop zookeeper, broker, kafka-manager and kafka-connect services

$ docker-compose -f cassandra/docker-compose.yml down          # stop Cassandra
```

!IMPORTANT!: These commands are for your reference, please don't do it if you don't want to spend time downloading resources again 

To remove the all the networks:

```bash
$ docker network rm kafka-network
$ docker network rm cassandra-network
```

To remove resources in Docker

```bash
$ docker container prune # remove stopped containers, done with the docker-compose down
$ docker volume prune # remove all dangling volumes (delete all data from your Kafka and Cassandra)
$ docker image prune -a # remove all images (help with rebuild images)
$ docker builder prune # remove all build cache (you have to pull data again in the next build)
$ docker system prune -a # basically remove everything
```


