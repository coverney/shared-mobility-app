# Initiate via yarn start-api

from flask import Flask, request, send_file
from DataProcessor import DataProcessor
import pandas as pd
import time # to add time delay for testing

ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__)
processor = None

@app.route('/upload', methods=['POST'])
def file_upload():
    """ Accepts uploaded file from React,
    makes sure that the file is the correct type,
    send the data to the processing pipeline, and
    returns a response to the frontend
    """
    eventsFile = request.files['eventsFile']
    eventsFilename = eventsFile.filename
    locationsFile = request.files['locationsFile']
    locationsFilename = locationsFile.filename
    print(f"received events file, {eventsFilename}, and locations file, {locationsFilename}, from client")
    # check file extension
    if any(ext in eventsFilename for ext in ALLOWED_EXTENSIONS) and any(ext in locationsFilename for ext in ALLOWED_EXTENSIONS):
        # valid extension, return success response
        response = {'error': False, 'msg': "successfully received uploaded files"}
        # start processing data
        df_events = pd.read_csv(eventsFile)
        df_locations = pd.read_csv(locationsFile)
        processor = DataProcessor(df_events, df_locations)
        processor.process_data()
        # print("Shape of demand file", processor.get_demand().shape)

        # time.sleep(3) # sleep for 3 seconds for testing
    else:
        # return unsuccessful response
        response = {'error': True, 'msg': "invalid file extension, both files need to be CSV"}
    return response

@app.route('/return-demand-file', methods=['GET'])
def return_demand_file():
    file = '../../../data_files/20210210_demandLatLng.csv'
    # file = processor.get_demand_file()
    try:
        return send_file(file,
                        mimetype='text/csv',
                        attachment_filename='demand.csv',
                        as_attachment=True)
    except Exception as e:
        return str(e)
