from odmantic import Model
from pydantic import ConfigDict

class AreaModel(Model):
    keyword:str
    publisher:str
    name:str
    image:str
    is_favorite:bool=False
    model_config={"collection":"areas"}
