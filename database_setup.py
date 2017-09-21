import os
import sys
from sqlalchemy import Column, ForeighKey, Integer, String
from sqlalchemy.ext.declarative import declerative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declerative_base()




engine= create_engine('sqlite:///restaurantmenu.db')
Base.metadata.creat_all(engine)
