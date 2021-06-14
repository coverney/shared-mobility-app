from json import JSONEncoder
from DataProcessor import DataProcessor

class DataProcessorEncoder(JSONEncoder):
    """
    Serialize DataProcessor object. This class is no longer needed with
    Flask-Session and Redis
    """
    def default(self, obj) :
        if isinstance(obj, DataProcessor):
            return obj.to_json()
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)
