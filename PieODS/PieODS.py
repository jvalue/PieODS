from requests.models import Response
from . import Adapter, Pipeline, helpers#, Notification, Storage, 

from typing import Literal#, Union
import json

#should be embedded inside local scopes
# _ad = Adapter.AdapterAPI()
# _ds = Adapter.DatasourceAPI()
# _pl = Pipeline.PipelineAPI()
#_nt = Notification.NotificationAPI()
#_st = Storage.StorageAPI()


class DataSource():
    def __init__(self, protocol_type:str="HTTP",
                location:str=None,
                encoding:str="UTF-8", 
                default_parameters:helpers.KVpairs=None,
                format_type:Literal["JSON","XML","CSV"]="JSON",
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
        self.default_params = default_parameters
        self.meta_data = helpers.Metadata(author, display_name, license, description)

        self.id = None

        self.pipeline_IDs = []
        self._ds = Adapter.DatasourceAPI()
        self._pl = Pipeline.PipelineAPI()

    def check_duplicate(self):
        duplicate = False
        datasources = self._ds.get_all_DatasourceConfigs().content
        for datasource_config in json.loads(datasources):
            own_meta_data =self.meta_data.get_dict()
            if (datasource_config["metadata"]["author"]== own_meta_data["author"] and
                datasource_config["metadata"]["displayName"]== own_meta_data["displayName"] ) :
                duplicate=True
                return datasource_config["id"]
        return False

    def create(self):
        check = self.check_duplicate()
        if not check:
            created_ds = self._ds.create_Datasource(Adapter.DatasourceConfig(protocol_config=self.protcol_config,
                                                                    format_config=self.format_config,
                                                                    trigger_config=self.trigger_config,
                                                                    meta=self.meta_data
                                                                )
                                        )
            id= json.loads(created_ds.content)["id"]
        else:
            id=check
        self.id = id
        return id

    def create_pipeline(self, transformation:str=None, display_name:str=None, description:str=None):
        created_pl = self._pl.create_pipeline_config(Pipeline.PipeLineConfigDTO(self.id,
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
            return  json.loads(self._ds.trigger_DataImport_without_params(self.id).content)["id"]
        else:
            if dynamic_params==() or dynamic_params==None:
                f = self._ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(*self.default_params.raw_pairs))
                return json.loads(f.content)["id"]              
            else:
                #return json.loads(self._ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(*dynamic_params)).content)["id"]
                return json.loads(self._ds.trigger_DataImport_with_params(self.id, self.validate_params(*dynamic_params)).content)["id"]

    def validate_params(self, *input_params):
        validated = [*input_params]
        input_params_keys = [key for pair in input_params for key in pair]
        defaults = self.default_params.get_dict()
        for key in defaults:
            if key not in input_params_keys:
                validated.append({key:defaults[key]})
        return Adapter.DataImportParameters(*validated)
        
                
    def get_single_import_data(self, import_id) -> Response:
        return self._ds.get_Data_of_Dataimport_of_Datasource(self.id, import_id).content

    def get_all_imports_data(self):
        data = {}
        for imp in json.loads(self._ds.get_All_Dataimports_of_Datasource(self.id).content):
            data[imp["id"]] = self.get_single_import_data(imp["id"])
        return data

#########Examples##############
# d = DataSource(location="https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/{station}/W/measurements.json?start=P1D",
#               default_parameters={"station": "BAMBERG"},
#               author="test",
#               display_name="Tessst",
#               )
# a = d.import_outside_pipeline()
# b = d.import_outside_pipeline({"station": "BONN"})
# c = d.import_outside_pipeline({"station": "BAMBERG"})
# e = d.get_single_import_data(a)
# f = d.get_single_import_data(b)
# g = d.get_single_import_data(c)
# h = d.get_all_imports_data()
# print("here")

    
# d = DataSource(location="https://api.covid19api.com/live/country/{country}/status/confirmed/date/{date}",
#               default_parameters=helpers.KVpairs({"country": "germany"}, {"date":"2021-03-21T13:13:30Z"}),
#               author="test",
#               display_name="Tessst",
#               )

# a = d.import_outside_pipeline()
# #k = d.create_pipeline(transformation="")
# b = d.import_outside_pipeline({"country": "united-states"}, {"date":"2020-03-21T13:13:30Z"})
# #c = d.import_outside_pipeline({"station": "BAMBERG"})
# e = d.get_single_import_data(a)
# f = d.get_single_import_data(b)
# #g = d.get_single_import_data(c)
# h = d.get_all_imports_data()
