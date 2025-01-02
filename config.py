import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = 'postgresql://ludvig:Legolas24@localhost:5432/fyyuur'
SQLALCHEMY_DATABASE_URI = 'postgresql://programm:Legolas24@localhost:5432/fyyuue'
SQLALCHEMY_TRACK_MODIFICATIONS = False