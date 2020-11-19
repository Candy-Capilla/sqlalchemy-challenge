import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
measurement = Base.classes.measurement
station= Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>add start date in YYYY-MM-DD format<br/>"
        f"/api/v1.0/<start>/<end> add start date and end date in YYYY-MM-DD format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all passenger names"""
    # Query all precipitation
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()

     # convert to dictionary  
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list"""
    # Query all stations
    results = session.query(station.name).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    last_year = dt.date(2017, 8, 23)- dt.timedelta(days =365)
    #query of last year of temps for most active station

    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= last_year).\
        filter(measurement.station == 'USC00519281').all()
    
    session.close()

    #convert to dictionary  
    all_tobs = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        all_tobs.append(temp_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #query start to current tmin, tavg, and tmax
    from_start = session.query(measurement.date,\
        func.min(measurement.tobs),\
        func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        group_by(measurement.date).all()

    session.close()
    
    #create dict
    start_temp = []
    for date, t_min, t_avg, t_max in from_start:
        start_temp_dict = {}
        start_temp_dict["date"] = date
        start_temp_dict["min"] = t_min
        start_temp_dict["avg"] = t_avg
        start_temp_dict["max"] = t_max
        start_temp.append(start_temp_dict)
    
    #jsonify
    return jsonify(start_temp)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #query start date to end date tmin, tavg, and tmax
    between_dates = session.query(measurement.date,\
        func.min(measurement.tobs),\
        func.avg(measurement.tobs),\
        func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).\
        group_by(measurement.date).all()
    
    session.close()

    #create dict
    start_end_temp = []
    for date, t_min, t_avg, t_max in between_dates:
        start_end_temp_dict = {}
        start_end_temp_dict["date"] = date
        start_end_temp_dict["min"] = t_min
        start_end_temp_dict["avg"] = t_avg
        start_end_temp_dict["max"] = t_max
        start_end_temp.append(start_end_temp_dict)
    
    #jsonify
    return jsonify(start_end_temp)

if __name__ == '__main__':
    app.run(debug=True)