import os
import sys
from sqlalchemy import Column, ForeighKey, Integer, String
from sqlalchemy.ext.declarative import declerative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declerative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    
class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    


engine= create_engine('sqlite:///restaurantmenu.db')
Base.metadata.creat_all(engine)
