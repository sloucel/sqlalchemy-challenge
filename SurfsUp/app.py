# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy import func, desc
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
        f"/api/v1.0/tobs/yyyy-mm-dd<br/>"
        f"/api/v1.0/tobs/yyyy-mm-dd/yyyy-mm-dd"
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

# SECTION 4: Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # STEP #1: Most active stations from climate_start.ipynb
    most_active_stations = session.query(Measurements.station, func.count(Measurements.station))\
                                  .group_by(Measurements.station)\
                                  .order_by(func.count(Measurements.station).desc())\
                                  .all()

    # Get the most active station ID
    most_active_station_id = most_active_stations[0][0] if most_active_stations else None

    # STEP #3: Most recent date for the most active station (mas) from climate_start.ipynb
    most_recent_date_for_mas = session.query(Measurements.date)\
                                      .filter(Measurements.station == most_active_station_id)\
                                      .order_by(desc(Measurements.date))\
                                      .first()
    most_recent_date = most_recent_date_for_mas[0] if most_recent_date_for_mas else None

    # STEP #4: 12-month date range for the most active station 
    twelve_months_ago_mas = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)

    # STEP #5: Query the last 12 months of temperature observation data for this station from climate_start.ipynb
    most_active_station_data = session.query(Measurements.date, Measurements.tobs)\
                                      .filter(Measurements.station == most_active_station_id, 
                                              Measurements.date >= twelve_months_ago_mas)\
                                      .order_by(Measurements.date)\
                                      .all()

    session.close()

    # Print
    print = {
        "most_active_station_id": most_active_station_id,
        "twelve_months_tobs": [
            {"date": date, "tobs": tobs} for date, tobs in most_active_station_data
        ]
    }

    return jsonify(print)

# SECTION 5a: Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#################################################
@app.route("/api/v1.0/tobs/<start>")
def temp_with_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Start date format
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Filter start date and get min, max, avg
    results = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start_date).all()

    session.close()

    # Check for results
    if not results or results[0][0] is None:
        return jsonify({"error": "No data found for the given start date."}), 404

    # Pull results
    lowest_temp, avg_temp, highest_temp = results[0]

    # Print
    print = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "lowest_temp": lowest_temp,
        "avg_temp": avg_temp,
        "highest_temp": highest_temp
    }

    return jsonify(print)


# SECTION 5b: Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
#################################################
@app.route("/api/v1.0/tobs/<start>/<end>")
def temp_with_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Start and end date formatting
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    # Convert datetime objects back to string for comparison
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Check if start date exists in the table
    start_date_exists = session.query(Measurements.date).filter(Measurements.date == start_date_str).first()
    if not start_date_exists:
        session.close()
        return jsonify({"error": "Start date not found in the dataset. Select date between 2010-01-01 and 2017-08-23"}), 404
    
    # Check if end date exists in the table
    end_date_exists = session.query(Measurements.date).filter(Measurements.date == end_date_str).first()
    if not end_date_exists:
        session.close()
        return jsonify({"error": "End date not found in the dataset. Select date between 2010-01-01 and 2017-08-23"}), 404

    # Define the query for temperature statistics from the start date to the end date
    results = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start_date_str, Measurements.date <= end_date_str).all()

    session.close()

    # Check results
    if not results or results[0][0] is None:
        return jsonify({"error": "No data found for the given date range. Select date between 2010-01-01 and 2017-08-23"}), 404

    # Pull results
    lowest_temp, avg_temp, highest_temp = results[0]

    # Prepare the response
    response = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "lowest_temp": lowest_temp,
        "avg_temp": avg_temp,
        "highest_temp": highest_temp
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)