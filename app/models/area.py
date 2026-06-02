from odmantic import Model
from pydantic import ConfigDict

class AreaModel(Model):
    keyword:str
    title:str
    link:str =""
    category:str=""
    description:str=""
    telephone:str=""
    address:str=""
    roadAddress:str=""
    mapx:str=""
    mapy:str=""
    is_favorite:bool=False
    model_config={"collection":"areas"}
