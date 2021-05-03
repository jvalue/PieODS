from typing import Literal
# from PieODS.data_structs import KVpairs
# import .Adapter
# import .Pipeline
# import .Notification
# import .Storage
from . import Adapter, Pipeline, Notification, Storage, helpers
from . import Pipeline
from . import Notification
from . import Storage
from typing import Union

ad = Adapter.AdapterAPI()
ds = Adapter.DatasourceAPI()
pl = Pipeline.PipelineAPI()
nt = Notification.NotificationAPI()
st = Storage.StorageAPI()

class DataSource():
    def __init__(self, protocol_type:str="HTTP",
                location:str=None,
                encoding:str="UTF-8", 
                default_parameters:helpers.KVpairs=None,
                format_type:Literal["JSON","XML","CSV"]=None,
                format_parameters:Union[dict , Adapter.CSVparameters] =None
                ) -> None:
        pass