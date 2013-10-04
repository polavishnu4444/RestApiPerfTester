
import logging
from log4mongo.handlers import MongoHandler

handler = MongoHandler(host='localhost:27017', database_name="PerfLogs", collection="MeasureData")

class CGLogger:
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def get_logger(self, name):
        logger = logging.getLogger(name)
        # logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return logger
    
    def merge_dict(self, dict_list):
        dictionary = {}
        for item in dict_list:
            dictionary.update(item)
        return dictionary