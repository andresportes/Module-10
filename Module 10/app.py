# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables

inspector = inspect(engine)


# Save references to each table

measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#1. '/'
#   - Start at the homepage.
#   - List all the available routes.

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

@app.route("/api/v1.0/precipitation")
def precipitation():
  
    last_date = session.query(func.max(measurement.date)).all()

    
    end_date = dt.date.fromisoformat(last_date[0][0])

   
    beginning_date = end_date - dt.timedelta(days=365)
    
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= begin_date).filter(measurement.date <= end_date).all()

    
    prcp_df = pd.DataFrame(data=precipitation, columns = ['Date', 'Precipitation'])

    prcp_df = prcp_df.sort_values(['Date'], ascending=True).reset_index(drop=True)

    prcp_df.set_index('Date', inplace=True)

  
    prcp_dict = jsonify(prcp_df.to_dict()['Precipitation'])
	return(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [station.station, station.name, station.latitude, station.longitude, station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    

    sel = [measurement.station, func.count(measurement.id)]
    active_stations = session.query(*sel).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()
    most_active_station = active_stations[0][0]
    # We can now find the specific measurements at said station
    station_tobs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.station == most_active_station).filter(measurement.date >= '2016-08-23').filter(measurement.date <= '2017-08-23').all()
    return(f"The lowest temperature over the last year of data was {station_tobs[0][0]} degrees. <br/>"
           f"The highest temperature over the last year of data was {station_tobs[0][1]} degrees. <br/>"
           f"The average temperature over the last year of data was {station_tobs[0][2]} degrees. <br/>")


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    

    overall_tobs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
   
    return(f"The minimum temperature from {start} was {overall_tobs[0][0]} degrees. <br/>"
           f"The maximum temperature from {start} was {overall_tobs[0][1]} degrees. <br/>"
           f"The average temperature from {start} was {overall_tobs[0][2]} degrees. <br/>")


@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    
    start_end_tobs = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    #And print out the results
    return(f"The minimum temperature between {start} and {end} was {start_end_tobs[0][0]} degrees. <br/>"
           f"The maximum temperature between {start} and {end} was {start_end_tobs[0][1]} degrees. <br/>"
           f"The average temperature between {start} and {end} was {start_end_tobs[0][2]} degrees. <br/>")







if __name__ == "__main__":
    app.run(debug=True)
