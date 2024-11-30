from django.conf import settings
from django.core.cache import cache
import json


class RedisUtils:
    
    def __init__(self):
        self.cache = cache
        
        
    
    def save(self,key,value,ex=None):
        serialized_value = json.dumps(value)
        self.cache.set(key,serialized_value, ex)
        
        
        
    def get(self,key):
        
        value = self.cache.get(key)
        
        if value:
            return json.loads(value)
        return None
    
    
    def delete(self,key):
        self.cache.delete(key)
        
        
