class DataService(object):
    """Provides services related to saving and fetching data for entities"""
    
    def __init__(self, application_config):
       self.app_config = application_config

    def save(self, entity, datasource):
        datasource = self.app_config.datasources.get(datasource,None)
        entity.save(datasource)

    def fetch(self, entity, datasource):
        datasource = self.app_config.datasources.get(datasource,None)
        entity.load(datasource)
    


