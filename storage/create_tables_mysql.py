import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host=app_config["datastore"]["hostname"], user=app_config["datastore"]["user"],
password=app_config["datastore"]["password"], database=app_config["datastore"]["db"])

db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE existing_customer
          (id INT NOT NULL AUTO_INCREMENT, 
           order_id VARCHAR(250) NOT NULL,
           customer_id VARCHAR(250) NOT NULL,
           tire_sku VARCHAR(250) NOT NULL,
           tire_size VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           quantity INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT existing_customer_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE dropship
          (id INT NOT NULL AUTO_INCREMENT, 
           order_id VARCHAR(250) NOT NULL,
           name VARCHAR(250) NOT NULL,
           address VARCHAR(250) NOT NULL,
           unit_no VARCHAR(250) NULL,
           city VARCHAR(250) NOT NULL,
           state_province VARCHAR(250) NOT NULL,
           country VARCHAR(250) NOT NULL,
           postal_zipcode VARCHAR(250) NOT NULL,
           tire_sku VARCHAR(250) NOT NULL,
           tire_size VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           quantity INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT dropship_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
