# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
 # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns json with the date as the key and the value as the precipitation"""
# Last data point in the database
    last_date_str = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date_str, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

# Precipitation data for the last 12 months
    results = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= one_year_ago).all()

    session.close()

  # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/precipitation")
def stations():


if __name__ == '__main__':
    app.run(debug=True)