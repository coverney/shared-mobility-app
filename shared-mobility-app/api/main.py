# Initiate via yarn start-api

import redis
import pyarrow as pa
from os import environ
from flask import Flask, request, send_file, session
from flask_session import Session
from DataProcessor import DataProcessor
import pandas as pd
import flask_excel as excel
from collections import OrderedDict
import time # to add time delay for testing
from datetime import datetime
import pytz
import utils

ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__, static_folder="build", static_url_path="/")
app.secret_key = environ.get('SECRET_KEY')
# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = environ.get('SESSION_TYPE')
app.config['SESSION_PERMANENT'] = environ.get('SESSION_PERMANENT')
app.config['SESSION_USE_SIGNER'] = environ.get('SESSION_USE_SIGNER')
app.config['SESSION_REDIS'] = redis.from_url(environ.get('SESSION_REDIS'))

# Create and initialize the Flask-Session object AFTER `app` has been configured
server_session = Session(app)
excel.init_excel(app)

@app.route("/")
def index():
    # TODO: delete unneeded code
    # if 'processorData' not in session:
    #     # session['processor'] = DataProcessor()
    #     session['processorData'] = None
    #     session['processorDistance'] = None
    # delete processorData and processorDistance so we can make a new one
    processor_data = session.pop('processorData', None)
    processor_distance = session.pop('processorDistance', None)
    return app.send_static_file("index.html")

@app.route('/upload-test', methods=['POST'])
def large_file_upload():
    print("hi")
    return 'OK'

@app.route('/upload', methods=['POST'])
def file_upload():
    """ Accepts uploaded file from React,
    makes sure that the file is the correct type,
    send the data to the processing pipeline, and
    returns a response to the frontend
    """
    # delete processorData and processorDistance so we can make a new one
    processor_data = session.pop('processorData', None)
    processor_distance = session.pop('processorDistance', None)
    if 'demandFile' in request.files:
        # received demand file and can skip data processing step
        demandFile = request.files['demandFile']
        demandFilename = demandFile.filename
        print(f"received demand file, {demandFilename}, from client")
        # check file extension
        if any(ext in demandFilename for ext in ALLOWED_EXTENSIONS):
            # valid extension, return success response
            response = {'error': False, 'msg': "successfully received uploaded file"}
            # set df_demand var in processor
            df_demand = pd.read_csv(demandFile)
            if utils.is_valid_df_demand(df_demand):
                # serialize df_demand
                df_demand_compressed = pa.serialize(df_demand).to_buffer().to_pybytes()
                session['processorData'] = df_demand_compressed
                # find processorDistance from df_demand
                session['processorDistance'] = utils.get_distance(df_demand)
            else:
                # return unsuccessful response
                response = {'error': True, 'msg': "demand file missing required cols"}
        else:
            # return unsuccessful response
            response = {'error': True, 'msg': "invalid file extension, files needs to be CSV"}
    else:
        # received events and location files and will process accordingly
        eventsFile = request.files['eventsFile']
        eventsFilename = eventsFile.filename
        locationsFile = request.files['locationsFile']
        locationsFilename = locationsFile.filename
        prob = float(request.form.get('probValue'))/100.0
        distance = int(request.form.get('distanceValue'))
        startTime = request.form.get('startTime')
        endTime = request.form.get('endTime')
        print(f"prob {prob}, distance {distance}, startTime {startTime}, and endTime {endTime}")
        print(f"received events file, {eventsFilename}, and locations file, {locationsFilename}, from client")
        # check file extension
        if any(ext in eventsFilename for ext in ALLOWED_EXTENSIONS) and any(ext in locationsFilename for ext in ALLOWED_EXTENSIONS):
            # valid extension, return success response
            response = {'error': False, 'msg': "successfully received uploaded files"}
            # start processing data
            df_events = pd.read_csv(eventsFile)
            df_locations = pd.read_csv(locationsFile)
            processor = DataProcessor()
            processor.set_events(df_events)
            processor.set_locations(df_locations)
            processor.set_p0(prob)
            processor.set_distance(distance)
            # TODO: when we get more data from other locations, we would need to change the timezone
            eastern = pytz.timezone('US/Eastern')
            if startTime:
                startTime = datetime.strptime(startTime, "%m/%d/%Y").replace(hour=0, minute=0, second=0)
                startTime = eastern.localize(startTime).isoformat()
                processor.set_start(startTime)
            if endTime:
                endTime = datetime.strptime(endTime, "%m/%d/%Y").replace(hour=0, minute=0, second=0)
                endTime = eastern.localize(endTime).isoformat()
                processor.set_end(endTime)
            processor.process_data()
            if processor.get_demand() is not None:
                # serialize df_demand
                df_demand_compressed = pa.serialize(processor.get_demand()).to_buffer().to_pybytes()
                session['processorData'] = df_demand_compressed
                session['processorDistance'] = distance
            else:
                print("processing didn't generate df_demand")
                response = {'error': True, 'msg': "processing didn't generate a data file"}
        else:
            # return unsuccessful response
            response = {'error': True, 'msg': "invalid file extension, both files need to be CSV"}
    return response

@app.route('/return-demand-file', methods=['GET'])
def return_demand_file():
    processor_data = session.get('processorData', None)
    # deserialize processor_data
    if processor_data is not None:
        df_demand = pa.deserialize(processor_data)
        demand_list = utils.get_relevant_demand_cols(df_demand).to_dict('records', into=OrderedDict)
        return excel.make_response_from_records(demand_list, file_type='csv')
    else:
        print("demand df is none")
        return {}

@app.route('/return-rectangles', methods=['POST', 'GET'])
def return_rectangles():
    # rectangles = [
    #   {
    #     'name': "Rectangle 1",
    #     'color': 'black',
    #     'bounds': [[41.835, -71.415],[41.825, -71.405]]
    #   },
    #   {
    #     'name': "Rectangle 2",
    #     'color': 'red',
    #     'bounds': [[41.825, -71.415],[41.815, -71.405]]
    #   }
    # ]
    # test_processor = DataProcessor()
    # rectangles = test_processor.build_shape_data()
    processor_distance = session.get('processorDistance', None)
    processor_data = session.get('processorData', None)
    # deserialize processor_data
    if processor_data is not None and processor_distance is not None:
        df_demand = pa.deserialize(processor_data)
    else:
        print("demand df is none")
        return {'data': []}
    # create Processor object
    processor = DataProcessor()
    if utils.is_valid_df_demand(df_demand):
        processor.set_demand(df_demand)
        processor.set_distance(processor_distance)
        if request.method == 'POST':
            start = str(request.form.get('start'))
            end = str(request.form.get('end'))
            # start and end need to be formated as YYYY-MM-DD
            start = datetime.strptime(start, "%m/%d/%Y").strftime('%Y-%m-%d')
            end = datetime.strptime(end, "%m/%d/%Y").strftime('%Y-%m-%d')
            rectangles, start, end = processor.build_shape_data(start, end)
        else:
            rectangles, start, end = processor.build_shape_data()
        # start and end need to be formated as MM/DD/YYYY
        start = datetime.strptime(start, '%Y-%m-%d').strftime("%m/%d/%Y")
        end = datetime.strptime(end, '%Y-%m-%d').strftime("%m/%d/%Y")
        return {'data': rectangles, 'start': start, 'end': end}
    else:
        print("demand file missing required cols")
        return {'data': []}
