#from typing import Literal
# from PieODS.data_structs import KVpairs
# import .Adapter
# import .Pipeline
# import .Notification
# import .Storage
from . import Adapter, Pipeline, Notification, Storage, helpers

from typing import Union, Literal
import json

#should be embedded inside local scopes
#will remove them later
#_ad = Adapter.AdapterAPI()
_ds = Adapter.DatasourceAPI()
_pl = Pipeline.PipelineAPI()
#_nt = Notification.NotificationAPI()
#_st = Storage.StorageAPI()

class DataSource():
    def __init__(self, protocol_type:str="HTTP",
                location:str=None,
                encoding:str="UTF-8", 
                default_parameters:helpers.KVpairs=None,
                format_type:Literal["JSON","XML","CSV"]=None,
                CSV_col_separtor: str=";" ,
                CSV_line_separator: str="\n",
                CSV_skip_first_data_row: bool=False,
                CSV_first_row_as_header: bool=True,
                first_execution:str="2018-10-07T01:32:00.123Z",
                interval:int = 60000,
                periodic:bool  = False,
                author:str=None,
                display_name: str =None,
                license : str = None,
                description:str = None, 
                ) -> None:
        self.protcol_config = Adapter.ProtocolConfig(Adapter.ProtocolConfigParameters(location, encoding, default_parameters), type=protocol_type)

        self.format_type = format_type
        self.format_config = None if self.format_type==None else Adapter.FormatConfig(format_type,
                            {} if format_type!="CSV" else Adapter.CSVparameters(CSV_col_separtor, CSV_line_separator, CSV_skip_first_data_row, CSV_first_row_as_header))

        self.trigger_config = Adapter.DatasourceTriggerConfig(first_execution, interval, periodic)

        self.dynamic = True if default_parameters!=None else False

        self.meta_data = helpers.Metadata(author, display_name, license, description)

        self.id = self.__create()

        self.pipeline_IDs = []

    def __create(self):
        created_ds = _ds.create_Datasource(Adapter.DatasourceConfig(protocol_config=self.protcol_config,
                                                                format_config=self.format_config,
                                                                trigger_config=self.trigger_config,
                                                                meta=self.meta_data
                                                               )
                                      ).content
        return json.loads(created_ds.content)["id"]

    def create_pipeline(self, transformation:str=None, display_name:str=None, description:str=None):
        created_pl = _pl.create_pipeline_config(Pipeline.PipeLineConfigDTO(self.id,
                                                                        Pipeline.Transformation("return data;" if transformation==None else transformation),
                                                                        helpers.Metadata(self.meta_data.author,
                                                                                        self.meta_data.display_name+str(len(self.pipeline_IDs)) if display_name==None else display_name,
                                                                                        self.meta_data.license,
                                                                                        description
                                                                                        )
                                                                        )
                                              )
        pl_id = json.loads(created_pl.content)["id"]
        self.pipeline_IDs.append(pl_id)
        return pl_id
    
    def import_outside_pipeline(self, *dynamic_params):
        if not self.dynamic:
            return  json.loads(_ds.trigger_DataImport_without_params(self.id).content)["id"]
        else:
            if dynamic_params==[] or dynamic_params==None:
                return json.loads(_ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(self.protcol_config.parameters.default_parameters)).content)["id"]              
            else:
                return json.loads(_ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(dynamic_params)).content)["id"]

    def get_single_import_data(self, import_id):
        return json.loads(_ds.get_Data_of_Dataimport_of_Datasource(self.id, import_id).content)

    def get_all_imports_data(self):
        data = {}
        for imp in json.loads(_ds.get_All_Dataimports_of_Datasource(self.id).content):
            data[imp["id"]] = self.get_single_import_data(imp["id"])
        return data

d = DataSource(location="https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/{station}/W/measurements.json?start=P1D",
              default_parameters={"station": "BAMBERG"},
              author="test",
              display_name="Tessst",
              )
d.import_outside_pipeline()
    
            