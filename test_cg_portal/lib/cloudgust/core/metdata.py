
class ClassMetadata(object):
    """description of class"""

    def __init__(self, classname):
        self.classname= classname
        self.relations=None
        self.belongs_to_relations={}

    def belongs_to(self, target_classname, target_id_field, self_foreign_id_field, self_foreign_field, is_required):
        self.belongs_to_relations[self_foreign_field] = Relation(self.classname, self_foreign_id_field, self_foreign_field, target_classname, target_id_field, is_required)
    

class Relation(object):
    def __init__(self, source_classname, source_id_field, source_field, target_classname, target_id_field, is_required):
        self.source_classname= source_classname
        self.source_id_field=source_id_field
        self.source_field = source_field
        self.target_classname=target_classname 
        self.target_id_field=target_id_field
        self.is_required = is_required

class DataSourceRegistry(object):
    def __init__(self):
        self.datasources = {}

    def add(self, name, datasource_type):
        self.datasources[name]=datasource_type
    
    def get(self, name, configuration):
        if(not self.datasources.has_key(name)):
            raise "data source does not exist"

        datasource = self.datasources[name]
        return datasource.create(configuration)


class AppConfiguration(object):
    """Keeps metadata for an app"""

    def __init__(self, app_id):
        self.class_metadata = {}
        self.datasources=DataSourceRegistry()
        self.datasource_configs = {}

    def add_class(self, class_metadata):
        if(self.class_metadata.has_key(class_metadata.classname)):
            raise ValueError(class_metadata.classname)

        self.class_metadata[class_metadata.classname]=class_metadata

    def get_classes(self):
        return self.class_metadata.values()

    def get_class(self,name):
        return self.class_metadata.get(name,None)
        
    def add_datasource(self,name, type):
        self.datasources.add(name, type)

    def get_datasource(self, name):
        return self.datasources.get(name)

    def add_datasource_config(self, datasource_name, config):
        if(self.datasource_configs.has_key(datasource_name)):
            raise ValueError(datasource_name)

        self.datasource_configs[datasource_name]=config

class AppDefinition(object):
    def __init__(self, name):
        self.name =name
        self.id = name