from flask import Flask, request

ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def file_upload():
    file = request.files['file']
    filename = file.filename
    print(f"received file {filename} from client")
    response = {'msg': "successfully received uploaded file"}
    return response
