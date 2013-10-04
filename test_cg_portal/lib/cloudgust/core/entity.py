import sys
import urllib2
import json
from base64 import b64encode
from copy import deepcopy
from data_service import DataService

class CGBaseObject(object):
    next_id=0
    def __init__(self):
        self.cid = CGBaseObject.create_id()

    @classmethod
    def create_id(cls):
        cls.next_id += 1
        return cls.next_id
        
class CGObject(CGBaseObject):    
    def __init__(self, classname, attributes={}, id_attribute="id"):   
        CGBaseObject.__init__(self)
            
        self.classname = classname
        self.attributes = deepcopy(attributes)
        self.isLoaded = True
        self.id_attribute = id_attribute

    def getid(self):        
        return self.attributes.get(self.id_attribute, None)

    def delete(self, dataprovider):
        self.attributes = dataprovider.delete(self.classname, self.getid())

    def load(self,dataprovider):
        self.attributes = dataprovider.get_by_id(self.classname, self.getid())        
        self.isLoaded = True

    def save(self, dataprovider):
        saved_vals =  dataprovider.save(self);
        self.attributes = saved_vals

    def set(self,key, value):
        self.attributes[key]=value

    def get(self, key):
        return self.attributes.get(key, None)

    def set(self, key, value):
        self.attributes[key]=value    

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, **kwargs)

    def to_dict(self, *args, **kwargs):
        values = deepcopy(self.attributes)

        #take care of value items
        for k,v in filter(lambda x: isinstance(x[1], CGBaseObject),values.iteritems()):
            values[k] = v.to_dict(*args, **kwargs)

        return values

    def clone(self, **options):
        attributes = deepcopy(self.attributes)
        if(options):
            if(options.has_key('copy_id') and options['copy_id'] == False):
                attributes.pop(self.id_attribute,None)

        return CGObject(self.classname, attributes) 
        
class CGCollection(CGBaseObject):
    def __init__(self, classname, classtype=CGObject, entities=None):  
        super(CGBaseObject,self).__init__()
              
        self.classname = classname
        self.collection = entities
        self.isLoaded = False
        self.classtype = classtype

    def get(self, id):
        vals = filter(lambda m: m.getid()==id, self.collection)
        if len(vals):
            if len(vals) == 1 : 
                return vals[0]
            else:
                raise ValueError("Collection is corrupt...multiple models with same id")
        return None
        
    def get_by_cid(self, cid):
        vals = filter(lambda m: m.cid==cid, self.collection)
        if len(vals):
            if len(vals) == 1 : 
                return vals[0]
            else:
                raise ValueError("Collection is corrupt...multiple models with same cid")
        return None    

    def load(self,dataprovider, query=None):
        self.collection = [self.classtype(self.classname,entity_val) for entity_val in dataprovider.get(self.classname,query)]
        self.isLoaded = True

    def save(self, dataprovider):
        return [entity.save(dataprovider) for entity in self.collection]

    def to_json(self,*args, **kwargs):
        val_dict = [entity.to_dict() for entity in self.collection]
        return json.dumps(val_dict, *args, **kwargs)
    
    def clone(self, options):
        new_obj = CGCollection(self.entity_creator, self.classname)
        new_obj.collection = [entity.clone(options) for entity in self.attributes]
        return new_obj

