import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

################################################
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
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


""""Convert the query results to a dictionary using date as the key and prcp as the value."""
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route('/api/v1.0/precipitation')
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    List = []
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    for x in prcp_results:
        data = {}
        data["date"] = Measurement.date
        data["prcp"] = Measurement.prcp
        List.append(data)
    return jsonify(List)

@app.route('/api/v1.0/stations')
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    station_results = session.query(Station.station).all()
    session.close()
    station_names = list(np.ravel(station_results))
    return jsonify(station_names)

@app.route('/api/v1.0/tobs')
def temp():
     # Create our session (link) from Python to the DB
    session = Session(engine)
    stations_max_count = session.query(Measurement.station,func.count(Measurement.station).label('station_count')).group_by(Measurement.station).order_by(desc("station_count")).first()[0]
    temp_data = session.query(Measurement.tobs).filter(Measurement.date >= query_date).filter(Measurement.station == stations_max_count[0]).all()
    session.close()
    Temp_list = list(np.ravel(temp_data))
    return jsonify(Temp_list)

@app.route('/api/v1.0/<start>')

def temp_details(start):
     # Create our session (link) from Python to the DB
    session = Session(engine)
    Temp_summary = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    Temp_summary_List = list(np.ravel(Temp_summary))
    return jsonify(Temp_summary_List)

@app.route('/api/v1.0/<start>/<end>')

def calc_temps(start, end):
    session = Session(engine)
    
    temp_results =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    Temp_results_List = list(np.ravel(temp_results))
    return jsonify(Temp_results_List)

if __name__ == '__main__':
    app.run(debug=True)




