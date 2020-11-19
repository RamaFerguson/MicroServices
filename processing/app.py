import connexion
from connexion import NoContent

import requests

import json
import os.path
import datetime
from os import path

import yaml
import logging
import logging.config

import datetime

from flask_cors import CORS, cross_origin

from apscheduler.schedulers.background import BackgroundScheduler

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

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def get_stats():   
    logger.info("Start get_stats")
    if os.path.isfile(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"], 'r') as f:
            data = json.load(f)
            logger.debug(data)
            logger.info("get_stats request completed")
            return data, 200
    else:
        return "Statistics do not exist", 404

def populate_stats():
    logger.info("Start Periodic Processing")
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "num_orders": 0,
        "num_existing_customer_orders": 0,
        "num_dropship_orders": 0,
        "max_existing_customer_quantity": 0,
        "max_dropship_quantity": 0,
        'timestamp': current_datetime
    }
    if os.path.isfile(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"], 'r') as f:
            data = json.load(f)
    # logger.debug(data)
    dropship_response = requests.get(app_config["eventstore"]["url"]+"/orders/dropship", params={ "timestamp": data["timestamp"]} )
    if (dropship_response.status_code != 200):
        logger.error("%i code received", dropship_response.status_code)
    else:
        dropship_json = dropship_response.json()
        logger.info("%i new events from Dropship", len(dropship_json))
        data["num_dropship_orders"] += len(dropship_json)

        # quantity
        # logger.debug(len(dropship_json))
        if len(dropship_json) > 0 :
            # logger.debug(dropship_json)
            max_quant = data["max_dropship_quantity"]
            for item in dropship_json:
                if (item["quantity"] > max_quant):
                    max_quant = item["quantity"]

            data["max_dropship_quantity"] = max_quant
    
    existing_customer_response = requests.get(app_config["eventstore"]["url"]+"/orders/existing_customer", params={ "timestamp": data["timestamp"]} )
    if (existing_customer_response.status_code != 200):
        logger.error("%i code received", existing_customer_response.status_code)
    else:
        exist_cust_json = existing_customer_response.json()
        logger.info("%i new events from Existing_Customer", len(exist_cust_json))
        data["num_existing_customer_orders"] += len(exist_cust_json)

        # quantity
        # logger.debug(len(exist_cust_json))
        if len(exist_cust_json) > 0 :
            # logger.debug(exist_cust_json)
            max_quant = data["max_existing_customer_quantity"]
            for item in exist_cust_json:
                if (item["quantity"] > max_quant):
                    max_quant = item["quantity"]

            data["max_existing_customer_quantity"] = max_quant
    
    
    data["num_orders"] =  data["num_existing_customer_orders"] + data["num_dropship_orders"]
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    data_str = json.dumps(data)

    with open(app_config["datastore"]["filename"], 'w') as f:
            f.write(data_str)

    logger.debug(data_str)
    logger.info("End Periodic Processing")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                'interval',
                seconds=app_config['scheduler']['period_sec'])
    sched.start()    

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS']='Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)