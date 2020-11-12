from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class ExistingCustomer(Base):
    """ Existing Customer """

    __tablename__ = "existing_customer"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)
    customer_id = Column(String(250), nullable=False)
    
    # Tire
    tire_sku = Column(String(250), nullable=False)
    tire_size = Column(String(250), nullable=False)

    timestamp = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, order_id, customer_id, tire_sku, tire_size, timestamp, quantity):
        """ Initializes an existing customer order """
        self.order_id = order_id
        self.customer_id = customer_id
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
        dict['customer_id'] = self.customer_id
        dict['tire'] = {}
        dict['tire']['tire_sku'] = self.tire_sku
        dict['tire']['tire_size'] = self.tire_size
        dict['timestamp'] = self.timestamp
        dict['quantity'] = self.quantity
        dict['date_created'] = self.date_created

        return dict
