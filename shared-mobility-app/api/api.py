# Initiate via yarn start-api

from flask import Flask, request

ALLOWED_EXTENSIONS = set(['.csv'])

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def file_upload():
    eventsFile = request.files['eventsFile']
    eventsFilename = eventsFile.filename
    locationsFile = request.files['locationsFile']
    locationsFilename = locationsFile.filename
    print(f"received events file, {eventsFilename}, and locations file, {locationsFilename}, from client")
    # check file extension
    if any(ext in eventsFilename for ext in ALLOWED_EXTENSIONS) and any(ext in locationsFilename for ext in ALLOWED_EXTENSIONS):
        # valid extension, return success response
        response = {'error': False, 'msg': "successfully received uploaded files"}
    else:
        # return unsuccessful response
        response = {'error': True, 'msg': "invalid file extension, both files need to be CSV"}
    return response
