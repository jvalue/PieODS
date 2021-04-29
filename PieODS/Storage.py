"""
# Storage Service of the ODS

The storage service is responsible for storing data and making it available via a query API.

## Current Implementation
The current implementation consists of the following parts:
* PostgreSQL database in the background
* Liquibase as >>source control<< for the database
* PostgREST as wrapping microservice with REST API

## Getting Started

* Build all containers with `docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env build storage-db-liquibase storage storage-mq`
* Run all containers with `docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env up storage-db storage-db-liquibase storage-db-ui storage storage-swagger storage-mq` (includes Adminer on port 8081 as UI for db, Swagger-UI as UI on port 8080 for REST API, Integration Tests)
Note that you need to delete existing docker images from your local docker daemon to have recent changes integrated: `docker system prune -f && docker volume prune -f`
* For integration testing run `docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env up storage-it`.
* To analyze the logs of the service under test we recommend using lazydocker. Alternatively, you can attach manually to the storage or storage-mq containers using the docker cli. 
* After running integration tests dependant services (e.g. rabbit-mq) keep running. In order to stop all services and return to a clean, initial state run `docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml down`. 


## API
| Endpoint  | Method  | Request Body  | Response Body |
|---|---|---|---|
| *base_url*/rpc/createStructureForDatasource  | POST  | `{pipelineid: "the-pipeline-id"}` | - |
| *base_url*/rpc/deleteStructureForDatasource  | POST  | `{pipelineid: "the-pipeline-id"}` | - |
| *base_url*/{the-pipeline-id}  | POST  | `{data: {<<json object>>}, timestamp: "<<timestamp>>", origin: "<<origin>>", license: "<<license>>", pipelineId: "<<pipelineId>>}` | - |
| *base_url*/{the-pipeline-id} | GET  | - | `{data: {<<json object>>, timestamp: "<<timestamp>>", origin: "<<origin>>", license: "<<license>>", pipelineId: "<<pipelineId>>}` |

When nothing is changed *base_url* is `http://localhost/3000`

"""
import requests
from helpers import _url, Config #this works


#################################################
######## Storage Service Data Structs ###########
#################################################
class PipeLineIDforStorage(Config):
    def __init__(self, id:int) -> None:
        self.pipelineID = str(id)
    def get_dict(self):
        return {
            "pipelineid": self.pipelineID
        }

class DataForStorage(Config):
    def __init__(self, data:str, timestamp:str, origin:str, license:str, pipelineid:int) -> None:
        self.data = data #<json object>
        self.timestamp = timestamp
        self.origin = origin
        self.license = license
        self.pipe_line_ID = int(pipelineid)
    def get_dict(self):
        return {
            "data":self.data,
            "timestamp":self.timestamp,
            "origin":self.origin, 
            "license":self.license,
            "pipelineId":self.pipe_line_ID
        }


class StorageAPI():
    def __init__(self) -> None:
        self.BASE_URL = "http://localhost:9000/api/storage"
        self.relative_paths = {
            "create_structure":"rpc/createstructurefordatasource",
            "delete_structure":"rpc/deletestructurefordatasource",
        }

    def create_structure_for_Datasource_Pipeline(self, request_body:PipeLineIDforStorage):
        return requests.post(_url(self.BASE_URL, self.relative_paths["create_structure"]), json=request_body.get_dict())
    
    def delete_structure_for_Datasource_Pipeline(self, request_body:PipeLineIDforStorage):
        return requests.post(_url(self.BASE_URL, self.relative_paths["delete_structure"]), json=request_body.get_dict())

    def add_pipeline_data(self, PipelineID:int,  request_body:DataForStorage):
        return requests.post(_url(self.BASE_URL, PipelineID), json=request_body.get_dict())

    def get_pipeline_data(self, PipelineID:int):
        return requests.get(_url(self.BASE_URL, PipelineID))

# health = requests.get("http://localhost:9000/api/storage")
# print("jjd")

"""
#########################################
########## Example Requests #############
#########################################

############# StorageAPI ################
import json
### Perform Storage Structure Creation

#creating a datasource
import Adapter
dsa = Adapter.DatasourceAPI()
protocol_config_params_json = ProtocolConfigParameters(location="https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json",
                                                                    encoding= "UTF-8")
protocol_config_json = ProtocolConfig("HTTP", protocol_config_params_json)
format_config_json = FormatConfig(type="JSON",
                                              parameters={})
ds_trigger_config = DatasourceTriggerConfig(first_ex="2018-10-07T01:32:00.123Z",
                                                          interval=60000,
                                                          periodic=True)
ds_metadata = Metadata(author="icke",
                                    display_name="pegelOnline",
                                    license="none")
ds_config = DatasourceConfig(None, protocol_config_json, format_config_json, ds_trigger_config, ds_metadata) 
create_datasource = dsa.create_Datasource(ds_config)
ds_id = json.loads(create_datasource.content)["id"]

#creating a pipeline
import Pipeline
pl = Pipeline.PipelineAPI()
pl_config_DTO = PipeLineConfigDTO(ds_id,
                                              Transformation("data.test = 'abc'; return data;"),
                                              Metadata(author="icke",
                                                                    license= "none",
                                                                    display_name= "exampleRequest",
                                                                    description="none"
                                                                    )
                                              )
created_pipeline = pl.create_pipeline_config(pl_config_DTO)
pl_id = json.loads(created_pipeline.content)["id"]

#creating the storage structure creation
st = StorageAPI()
created_storage_structure = st.create_structure_for_Datasource_Pipeline(PipeLineIDforStorage(pl_id))

### Get Stored Data
stored_data = st.get_pipeline_data(pl_id)

#cleaning the created data structure
deleted_st = st.delete_structure_for_Datasource_Pipeline(PipeLineIDforStorage(pl_id))

#cleaning the pipeline
deleted_pl = pl.delete_pipeline_config_by_ID(pl_id)
#deleted_all_pls = pl.delete_all_pipeline_configs()
#cleaning the datasource
deleted_ds = dsa.delete_Datasource(ds_id)
#deleted_all_ds = dsa.delete_all_Datasources()
print("End")
"""