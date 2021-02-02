# Initiate via yarn start-api

from flask import Flask, request
import processData
import pandas as pd

ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__)

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
        # df_events = pd.read_csv(eventsFile)
        # df_locations = pd.read_csv(locationsFile)
        # processData.process_data(df_events, df_locations)
    else:
        # return unsuccessful response
        response = {'error': True, 'msg': "invalid file extension, both files need to be CSV"}
    return response
