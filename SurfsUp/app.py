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
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# SECTION 1: Start at the homepage. List all the available routes.
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

# SECTION 2: Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. 
# Return the JSON representation of your dictionary.
#################################################
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

# SECTION 3: Return a JSON list of stations from the dataset.
#################################################

@app.route("/api/v1.0/stations")
def stations():
 # Create our session (link) from Python to the DB
    session = Session(engine)

# List of stations in the table
    results = session.query(Station.station, Station.name).all()
       
    session.close()

# Convert the query results to a list of dictionaries
    stations_data = []
    for station, name in results:
        station_data = {
            "station": station,
            "name": name
        }
        stations_data.append(station_data)

    # Return a JSON response
    return jsonify(stations_data)

# SECTION 4 Query the dates and temperature observations of the most-active station for the previous year of data. 
# Return a JSON list of temperature observations for the previous year.
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
 # Create our session (link) from Python to the DB
    session = Session(engine)

# Stations
    results = session.query(Station.station, Station.name).all()
       
    session.close()


if __name__ == '__main__':
    app.run(debug=True)