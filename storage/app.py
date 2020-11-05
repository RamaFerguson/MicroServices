import connexion
from connexion import NoContent

import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base

from dropship import DropShip
from existing_customer import ExistingCustomer

import json
import os.path
import datetime
from os import path

import mysql.connector
import pymysql

import yaml
import logging
import logging.config

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(app_config["datastore"]["user"], app_config["datastore"]["password"], app_config["datastore"]["hostname"], app_config["datastore"]["port"], app_config["datastore"]["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

MAX_EVENTS = 10
EVENTS_FILENAME = "events.json"

# def order_new_location(body):   
#     logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
#     session = DB_SESSION()

#     ds = DropShip(body['order_id'],
#                         body['address']['name'],
#                         body['address']['address'],
#                         body['address']['unit_no'],
#                         body['address']['city'],
#                         body['address']['state/province'],
#                         body['address']['country'],
#                         body['address']['postal/zipcode'],
#                         body['tire']['tire_sku'],
#                         body['tire']['tire_size'],
#                         body['timestamp'],
#                         body['quantity']
#                         )

#     session.add(ds)

#     session.commit()
#     session.close()
    
#     logger.debug('Stored event order_new_location request with a unique id of %s', body["order_id"])
    
#     return NoContent, 201

# def order_existing_customer(body):
#     logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
#     session = DB_SESSION()

#     ec = ExistingCustomer(body['order_id'],
#                         body['customer_id'],
#                         body['tire']['tire_sku'],
#                         body['tire']['tire_size'],
#                         body['timestamp'],
#                         body['quantity']
#                         )

#     session.add(ec)

#     session.commit()
#     session.close()

#     logger.debug('Stored event order_existing_customer request with a unique id of %s', body["order_id"])

#     return NoContent, 201

def get_existing_customer_orders(timestamp):
    """ Gets new existing customer orders after the timestamp """
    logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(
        timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)
    readings = session.query(ExistingCustomer).filter(ExistingCustomer.date_created >=
                                                timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Existing Customer orders after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200

def get_dropship_orders(timestamp):
    """ Gets new dropship orders after the timestamp """
    logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
    session = DB_SESSION()    
    timestamp_datetime = datetime.datetime.strptime(
        timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)
    readings = session.query(DropShip).filter(DropShip.date_created >=
                                                timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Dropship orders after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200

def update_events_log(body):
    events_log_json = []
    if not(path.exists(EVENTS_FILENAME)):
        events_log = open(EVENTS_FILENAME, "a")
        events_log.write("[]")
        events_log.close()

    with open(EVENTS_FILENAME, "r+") as events_log_file:
        events_log_contents = events_log_file.read()
        if (len(events_log_contents) == 0):
            events_log_file.write("[]")
            events_log_json = []
        else:
            events_log_json = json.loads(events_log_contents)

    if (len(events_log_json) == MAX_EVENTS):
        events_log_json.pop(0)        
    events_log_json.append(body)

    with open(EVENTS_FILENAME, 'w') as outfile:
        json.dump(events_log_json, outfile, indent=4)

def process_messages():
    """ Process event messages """
    logger = logging.getLogger('basicLogger')
    logger.info('Processing messages')
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group='storage',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "existing_customer":
            logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
            session = DB_SESSION()

            ec = ExistingCustomer(payload['order_id'],
                                payload['customer_id'],
                                payload['tire']['tire_sku'],
                                payload['tire']['tire_size'],
                                payload['timestamp'],
                                payload['quantity']
                                )

            session.add(ec)

            session.commit()
            session.close()

            logger.debug('Stored event order_existing_customer request with a unique id of %s', payload["order_id"])

        elif msg["type"] == "dropship":
            logger.info('Connecting to DB. Hostname: %s, Port:%i', app_config["datastore"]["hostname"], app_config["datastore"]["port"])
            session = DB_SESSION()

            ds = DropShip(payload['order_id'],
                                payload['address']['name'],
                                payload['address']['address'],
                                payload['address']['unit_no'],
                                payload['address']['city'],
                                payload['address']['state/province'],
                                payload['address']['country'],
                                payload['address']['postal/zipcode'],
                                payload['tire']['tire_sku'],
                                payload['tire']['tire_size'],
                                payload['timestamp'],
                                payload['quantity']
                                )

            session.add(ds)

            session.commit()
            session.close()
            
            logger.debug('Stored event order_new_location request with a unique id of %s', payload["order_id"])
            
        # Commit the new message as being read
        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
