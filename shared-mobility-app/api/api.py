# Initiate via yarn start-api

from flask import Flask, request, send_file
from DataProcessor import DataProcessor
import pandas as pd
import flask_excel as excel
from collections import OrderedDict
import time # to add time delay for testing
from datetime import datetime

ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__)
excel.init_excel(app)
processor = DataProcessor()

@app.route('/upload', methods=['POST'])
def file_upload():
    """ Accepts uploaded file from React,
    makes sure that the file is the correct type,
    send the data to the processing pipeline, and
    returns a response to the frontend
    """
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
            if processor.is_valid_df_demand(df_demand):
                processor.set_demand(df_demand)
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
        print(f"prob {prob} and distance {distance}")
        print(f"received events file, {eventsFilename}, and locations file, {locationsFilename}, from client")
        # check file extension
        if any(ext in eventsFilename for ext in ALLOWED_EXTENSIONS) and any(ext in locationsFilename for ext in ALLOWED_EXTENSIONS):
            # valid extension, return success response
            response = {'error': False, 'msg': "successfully received uploaded files"}
            # start processing data
            df_events = pd.read_csv(eventsFile)
            df_locations = pd.read_csv(locationsFile)
            processor.set_events(df_events)
            processor.set_locations(df_locations)
            processor.set_p0(prob)
            processor.set_distance(distance)
            processor.process_data()
            # print("Shape of demand file", processor.get_demand().shape)
            # time.sleep(3) # sleep for 3 seconds for testing
        else:
            # return unsuccessful response
            response = {'error': True, 'msg': "invalid file extension, both files need to be CSV"}
    return response

@app.route('/return-demand-file', methods=['GET'])
def return_demand_file():
    demand_list = processor.get_relevant_demand_cols().to_dict('records', into=OrderedDict)
    return excel.make_response_from_records(demand_list, file_type='csv')

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
    if processor.get_demand() is not None:
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
        print("demand df is none")
        return {'data': []}
