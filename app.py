# import Flask
from flask import Flask
from flask import jsonify

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt
from datetime import date

#################################################
# Database Setup
#################################################
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement_base = Base.classes.measurement
station_base = Base.classes.station

# Create an app, being sure to pass __name__
app = Flask(__name__)


# Define what to do when a user hits the index route/home page. 
# put in a default start and end date instead of word start and end.
@app.route("/")
def home():
    """list all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(measurement_base.date, measurement_base.prcp).filter(measurement_base.date >= query_date).all()

    session.close()

    # Convert list of tuples into normal list
    all_dates = list(np.ravel(precipitation))

    all_dates = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_dates.append(precipitation_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the list of stations.
    stations = session.query(measurement_base.station).group_by(measurement_base.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    result = session.query(measurement_base.tobs).filter((measurement_base.station == 'USC00519281')\
                                            &(measurement_base.date >= query_date)).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_results = list(np.ravel(result))

    return jsonify(all_results)

# when we runthis function for start or start/end - pass in the variable for start date.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
#put in the last date as the default end date.
def start_dates(start, end='2017-08-23'):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results = session.query(func.avg(measurement_base.tobs), func.max(measurement_base.tobs), func.min(measurement_base.tobs)).filter((measurement_base.date >= start) & (measurement_base.date <= end)).all()


    for min, avg, max in results:
        start = {}
        start["avg"] = avg
        start["min"] = min
        start["max"] = max
        return_list.append(start)

    session.close()

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug=True)