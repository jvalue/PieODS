from requests.models import Response
from . import Adapter, Pipeline, helpers, Storage#, Notification

from typing import Literal, Union
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
        self._st =Storage.StorageAPI()
        #return True

    def check_duplicate_datasource(self) -> Union[int, bool]:
        #duplicate = False
        fetched_datasources_response = self._ds.get_all_DatasourceConfigs()    
        if fetched_datasources_response.status_code<300:
            try:
                #datasources = fetched_datasources_response.content
                for datasource_config in json.loads(fetched_datasources_response.content): #need to check behavior when there are no prior datasources
                    own_meta_data =self.meta_data.get_dict()
                    if (datasource_config["metadata"]["author"]== own_meta_data["author"] and
                        datasource_config["metadata"]["displayName"]== own_meta_data["displayName"] ) :
                        #duplicate=True
                        return datasource_config["id"]
            except:
                return False
        else:
            return False

    def create(self)->int:
        check = self.check_duplicate_datasource()
        if not check:
            created_ds = self._ds.create_Datasource(Adapter.DatasourceConfig(protocol_config=self.protcol_config,
                                                                    format_config=self.format_config,
                                                                    trigger_config=self.trigger_config,
                                                                    meta=self.meta_data
                                                                )
                                        )
            if created_ds.status_code<300:                            
                id= json.loads(created_ds.content)["id"]
            else:
                return False
        else:
            id=check
        self.id = id
        return id

    def check_duplicate_pipeline(self, pl_config:Pipeline.PipeLineConfigDTO):
        fetched_pipelines_response = self._pl.get_all_pipeline_configs()  
        if fetched_pipelines_response.status_code<300:
            try:
                #pipelines = fetched_pipelines_response.content
                for pipeline_config in json.loads(fetched_pipelines_response.content): #need to check behavior when there are no prior datasources
                    #if pipeline_config["id"]==41:
                    # print(pl_config.data_source_ID)
                    # print(pipeline_config["datasourceId"])
                    # print(pipeline_config["transformation"]["func"])
                    # print(pl_config.transformation)
                    #own_meta_data = pl_config.meta_data.get_dict()
                    # if (pipeline_config["metadata"]["author"]== own_meta_data["author"] and
                    #     pipeline_config["metadata"]["displayName"]== own_meta_data["displayName"] and
                    #     pipeline_config["datasourceId"]==pl_config.data_source_ID and
                    #     pipeline_config["transformation"]["func"]==pl_config.transformation.getdict()["func"]) :
                    if (pipeline_config["datasourceId"]==pl_config.data_source_ID and
                        pipeline_config["transformation"]["func"]==pl_config.transformation.get_dict()["func"]) :
                        #print("found {}".format(pipeline_config["id"]))
                        return pipeline_config["id"]
            except:
                return False
        else:
            return False

    def create_pipeline(self, transformation:str=None, author:str=None, display_name:str=None, description:str=None, license:str=None)-> int:
        pl_config = Pipeline.PipeLineConfigDTO(self.id,
                                                Pipeline.Transformation("return data;" if transformation==None else transformation),
                                                helpers.Metadata(author = self.meta_data.author if author==None else author,
                                                                display_name = self.meta_data.display_name+str(len(self.pipeline_IDs)) if display_name==None else display_name,
                                                                license = self.meta_data.license if license==None else license,
                                                                description = self.meta_data.description if description==None else description
                                                                )
                                                )
        check = self.check_duplicate_pipeline(pl_config)
        # created_pl = self._pl.create_pipeline_config(pl_config)
        # if created_pl.status_code < 300:
        #     pl_id = json.loads(created_pl.content)["id"]
        #     self.pipeline_IDs.append(pl_id)
        #     return pl_id
        # else:
        #     return False

        if not check:
            created_pl = self._pl.create_pipeline_config(pl_config)
            if created_pl.status_code<300:                            
                pl_id = json.loads(created_pl.content)["id"]
                self.pipeline_IDs.append(pl_id)
                return pl_id
            else:
                return False
        else:
            pl_id=check
            if pl_id not in self.pipeline_IDs:
                self.pipeline_IDs.append(pl_id)
        return pl_id

    def delete_pipeline(self, pipeline_id):
        if self._pl.delete_pipeline_config_by_ID(pipeline_id).status_code < 400:
            return True
        else:
            return False

    def delete_all_attributed_pipelines(self):
        if all([self.delete_pipeline(i) for i in self.pipeline_IDs]):
            return True
        else:
            return False
    
    def import_outside_pipeline(self, *dynamic_params) -> int:
        if not self.dynamic:
            return  json.loads(self._ds.trigger_DataImport_without_params(self.id).content)["id"]
        else:
            if dynamic_params==() or dynamic_params==None:
                f = self._ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(*self.default_params.raw_pairs))
                return json.loads(f.content)["id"]              
            else:
                #return json.loads(self._ds.trigger_DataImport_with_params(self.id, Adapter.DataImportParameters(*dynamic_params)).content)["id"]
                return json.loads(self._ds.trigger_DataImport_with_params(self.id, self.validate_params(*dynamic_params)).content)["id"]

    def validate_params(self, *input_params) -> Adapter.DataImportParameters:
        validated = [*input_params]
        input_params_keys = [key for pair in input_params for key in pair]
        defaults = self.default_params.get_dict()
        for key in defaults:
            if key not in input_params_keys:
                validated.append({key:defaults[key]})
        return Adapter.DataImportParameters(*validated)
        
                
    def get_single_import_data(self, import_id) -> Response:
        return self._ds.get_Data_of_Dataimport_of_Datasource(self.id, import_id).content

    def get_all_imports_data(self)-> dict:
        data = {}
        for imp in json.loads(self._ds.get_All_Dataimports_of_Datasource(self.id).content):
            data[imp["id"]] = self.get_single_import_data(imp["id"])
        return data
    
    def get_data_of_latest_data_import(self):
        return self._ds.get_Data_of_latest_Dataimport_of_Datasource(self.id).content

    def get_single_pipeline_output(self, pl_id):
        try:
            return json.loads(self._st.get_pipeline_data(pl_id).content)
        except:
            return {}
    def get_latest_single_pipeline_output(self, pl_id):

        try:
            data =  json.loads(self._st.get_pipeline_data(pl_id).content)[-1]["data"]
            return data
        except:
            return {}

    def self_destroy(self):
        if self.id!=None:
            self._ds.delete_Datasource(self.id)
            return True
        else:
            return False

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
