import connexion
from connexion import NoContent
import requests
import json
import os.path
import yaml
import logging
import logging.config
import datetime
from pykafka import KafkaClient
from os import path

MAX_EVENTS = 10
EVENTS_FILENAME = "events.json"

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
kafka_server = "{}:{}".format(app_config["events"]["hostname"],app_config["events"]["port"])


# logger.info("App Conf File: %s" % app_conf_file)
# logger.info("Log Conf File: %s" % log_conf_file)


def order_existing_customer(body):
    logger.info('Received event order_existing_customer request with a unique id of %s', body["order_id"])
    # logger.info("{}:{}".format(app_config["events"]["hostname"],app_config["events"]["port"]))
    client = KafkaClient(hosts=kafka_server)
    topic = client.topics[app_config["events"]["topic"]]
    producer = topic.get_sync_producer()
    msg = { "type": "existing_customer",
            "datetime" : datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned event order_existing_customer request with a unique id of %s with status code %i',
                body["order_id"], 200)
    return NoContent, 200


def order_new_location(body):
    logger.info('Received event order_new_location request with a unique id of %s', body["order_id"])
    # logger.info("{}:{}".format(app_config["events"]["hostname"],app_config["events"]["port"]))
    client = KafkaClient(hosts=kafka_server)
    topic = client.topics[app_config["events"]["topic"]]
    producer = topic.get_sync_producer()
    msg = { "type": "dropship",
            "datetime" : datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Returned event order_new_location request with a unique id of %s with status code %i',
                body["order_id"], 200)
    return NoContent, 200

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


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True,
validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)
