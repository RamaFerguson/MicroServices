from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class DropShip(Base):
    """ DropShip """

    __tablename__ = "dropship"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)

    # Address
    name = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    unit_no = Column(String(250), nullable=True)
    city = Column(String(250), nullable=False)
    state_province = Column(String(250), nullable=False)
    country = Column(String(250), nullable=False)
    postal_zipcode = Column(String(250), nullable=False)

    # Tire
    tire_sku = Column(String(250), nullable=False)
    tire_size = Column(String(250), nullable=False)

    timestamp = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, order_id, name, address, unit_no, city, state_province, country, postal_zipcode, tire_sku, tire_size, timestamp, quantity ):
        """ Initializes a dropship order """
        self.order_id = order_id

        self.name = name
        self.address = address
        self.unit_no = unit_no
        self.city = city
        self.state_province = state_province
        self.country = country
        self.postal_zipcode = postal_zipcode

        self.tire_sku = tire_sku
        self.tire_size = tire_size
        
        self.timestamp = timestamp
        self.quantity = quantity
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of an existing customer order """
        dict = {}
        dict['id'] = self.id
        dict['order_id'] = self.order_id

        dict['address'] = {}
        dict['address']['name'] = self.name
        dict['address']['address'] = self.address
        dict['address']['unit_no'] = self.unit_no
        dict['address']['city'] = self.city
        dict['address']['state/province'] = self.state_province
        dict['address']['country'] = self.country
        dict['address']['postal/zipcode'] = self.postal_zipcode

        dict['tire'] = {}
        dict['tire']['tire_sku'] = self.tire_sku
        dict['tire']['tire_size'] = self.tire_size

        dict['timestamp'] = self.timestamp
        dict['quantity'] = self.quantity
        dict['date_created'] = self.date_created

        return dict
