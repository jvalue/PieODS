"""
Open Data Service - Pipeline-Service
====================================

Build
-----

``npm install``

``npm run tsc``

Run
---

``npm start``

Running in watch mode
---------------------

Use ``npm run watch`` to concurrently start the ``tsc`` compiler as well
as run the service. It automatically reloads after file changes.

Running unit tests
------------------

Use ``npm test`` to run the unit tests. There is also
``nrm run watch-test`` available to start ``jest`` in "watch mode".

Running end-to-end tests
------------------------

-  For integration testing run
   ``docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env up pipeline-it``.

-  To analyze the logs of the service under test we recommend using
   lazydocker. Alternatively, you can attach manually to the pipeline
   container using the docker cli.

-  After running integration tests dependant services (e.g. rabbit-mq)
   keep running. In order to stop all services and return to a clean,
   initial state run
   ``docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml down``.

API
---

+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| Endpoint                  | Method   | Request Body                   | Response Body      | Description                      |
+===========================+==========+================================+====================+==================================+
| *base\_url*/              | GET      | -                              | text               | Get health status                |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/version       | GET      | -                              | text               | Get service version              |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/job           | POST     | PipelineExecutionRequest       | JobResult          | Pipeline execution               |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/trigger       | POST     | PipelineConfigTriggerRequest   | text               | Pipeline trigger                 |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs       | GET      | -                              | PipelineConfig[]   | Get all pipeline configs         |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs/:id   | GET      | -                              | PipelineConfig     | Get pipeline config by id        |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs       | POST     | PipelineConfigDTO              | PipelineConfig     | Create a pipeline config         |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs/:id   | PUT      | PipelineConfigDTO              | text               | Update a pipeline config         |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs/:id   | DELETE   | -                              | text               | Delete a pipeline config by id   |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+
| *base\_url*/configs       | DELETE   | -                              | text               | Delete all pipeline configs      |
+---------------------------+----------+--------------------------------+--------------------+----------------------------------+

PipelineExecutionRequest
~~~~~~~~~~~~~~~~~~~~~~~~

::

    {
      "data": object,
      "func": string [VALID JS CODE]
    }

JobResult
~~~~~~~~~

::

    {
      "data"?: object,
      "error"?: object,
      "stats": stats
    }

PipelineConfigTriggerRequest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    {
      "datasourceId": number,
      "data": object
    }

PipelineConfig
~~~~~~~~~~~~~~

::

    {
      "id": number,
      "datasourceId": number,
      "transformation": {
        "func": string [VALID JS CODE]
      },
      "metadata": {
        "author": string,
        "displayName": string,
        "license": string,
        "description": string,
        "creationTimestamp": Date
      }
    }

PipelineConfigDTO
~~~~~~~~~~~~~~~~~

::

    {
      "datasourceId": number,
      "transformation": {
        "func": string [VALID JS CODE]
      },
      "metadata": {
        "author": string,
        "displayName": string,
        "license": string,
        "description": string,
      }
    }

License
-------

Copyright 2018 Friedrich-Alexander Universität Erlangen-Nürnberg

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see http://www.gnu.org/licenses/.

"""

"""
PipelineExecutionRequest:
{
  "data": object,
  "func": string [VALID JS CODE]
}

JobResult:
{
  "data"?: object,
  "error"?: object,
  "stats": stats
}

PipelineConfigTriggerRequest:
{
  "datasourceId": number,
  "data": object
}

PipelineConfig:
{
  "id": number,
  "datasourceId": number,
  "transformation": {
    "func": string [VALID JS CODE]
  },
  "metadata": {
    "author": string,
    "displayName": string,
    "license": string,
    "description": string,
    "creationTimestamp": Date
  }
}

PipelineConfigDTO:
{
  "datasourceId": number,
  "transformation": {
    "func": string [VALID JS CODE]
  },
  "metadata": {
    "author": string,
    "displayName": string,
    "license": string,
    "description": string,
  }
}
"""
import requests
from .helpers import _url, Config, KVpairs, Metadata

#################################################
######## Pipeline Service Data Structs ##########
#################################################

class PipelineExecutionRequest(Config):
    def __init__(self, data:KVpairs, func:str) -> None:
        self.data = data 
        self.func = func 
    def get_dict(self):
        return {
            "data": self.data.get_dict(), #KVpairs, pass key:value pairs to the init method of class KVpairs
            "func": self.func #string [VALID JS CODE]
            }

class PipelineConfigTriggerRequest(Config):
    def __init__(self, datasourceid: int, data:KVpairs) -> None:
        self.data_source_ID = int(datasourceid)
        self.data = data #KVpairs
    def get_dict(self):
        return {
            "datasourceId": self.data_source_ID,
            "data":self.data.get_dict() #KVpairs
        }

class Transformation(Config):
    def __init__(self, func:str) -> None:
        self.func = str(func)
    def get_dict(self):
        return {"func":self.func}

class PipeLineConfig(Config):
    def __init__(self, id:int, datasourceid:int, transformation:Transformation, metadata:Metadata) -> None:
        self.id = int(id)
        self.data_source_ID = int(datasourceid)
        self.transformation = transformation
        self.meta_data = metadata
    def get_dict(self):
        return {
            "id":self.id,
            "datasourceId":self.data_source_ID,
            "transformation":self.transformation.get_dict(),
            "metadata":self.meta_data.get_dict()
        }

class PipeLineConfigDTO(Config):
    def __init__(self, datasourceid:int, transformation:Transformation, metadata:Metadata) -> None:
        self.data_source_ID = int(datasourceid)
        self.transformation = transformation
        self.meta_data = metadata #without creationTimestamp
    def get_dict(self):
        return {
            "datasourceId":self.data_source_ID,
            "transformation":self.transformation.get_dict(),
            "metadata":self.meta_data.get_dict()
        }


class PipelineAPI:
  def __init__(self) -> None:
    
    self.BASE_URL = "http://localhost:9000/api/pipelines"

    self.relative_paths = {
        "version":"version",
        "job":"job",
        "trigger":"trigger",
        "configs":"configs",
    }

  def get_health_status(self):
      return requests.get(self.BASE_URL) 

  def get_service_version(self):
      return requests.get(_url(self.BASE_URL, self.relative_paths["version"]))

  #assuming body is always json
  def execute_pipeline(self, PipelineExecutionRequest:PipelineExecutionRequest):
      """Executes the pipeline

      Parameters
      ----------
      PipelineExecutionRequest : json
          Format:
              {
              "data": object,
              "func": string (VALID JS CODE)
              }

      Returns
      -------
      Response object: 
      -------
          "JobResult" is the response body and has the format:
              {
              "data"?: object,
              "error"?: object,
              "stats": stats
              }
      """
      return requests.post(_url(self.BASE_URL, self.relative_paths["job"]), json=PipelineExecutionRequest.get_dict())

  def trigger_pipeline(self, PipelineConfigTriggerRequest:PipelineConfigTriggerRequest):
      """Triggers the pipeline

      Parameters
      ----------
      PipelineConfigTriggerRequest: json
      """
      return requests.post(_url(self.BASE_URL, self.relative_paths["trigger"]), json=PipelineConfigTriggerRequest.get_dict())

  def get_all_pipeline_configs(self):
      return requests.get(_url(self.BASE_URL, self.relative_paths["configs"]))

  def get_pipeline_config_by_ID(self, PipelineID):
      """
      Parameters
      ----------
      PipelineID: int
      """
      return requests.get(_url(self.BASE_URL, self.relative_paths["configs"], PipelineID))

  def create_pipeline_config(self, PipelineconfigDTO:PipeLineConfigDTO):
    """Create a pipeline config

    :param PipelineconfigDTO: identifier of a pipeline config
    :type PipelineconfigDTO: json
    :return: [description]
    :rtype: [type]
    """  ""
    return requests.post(_url(self.BASE_URL, self.relative_paths["configs"]), json=PipelineconfigDTO.get_dict())

  def update_pipeline_config(self, PipelineID:int, PipelineconfigDTO:PipeLineConfigDTO):
    """Update a pipeline config.

    :param PipelineconfigDTO: [description]
    :type PipelineconfigDTO: [type]
    :return: [description]
    :rtype: [type]
    """  ""
    return requests.put(_url(self.BASE_URL, self.relative_paths["configs"], PipelineID), json=PipelineconfigDTO.get_dict())

  def delete_all_pipeline_configs(self):
      return requests.delete(_url(self.BASE_URL, self.relative_paths["configs"]))

  def delete_pipeline_config_by_ID(self, PipelineID:int):
      """
      Parameters
      ----------
      PipelineID: int
      """
      return requests.delete(_url(self.BASE_URL, self.relative_paths["configs"], PipelineID))

"""
#########################################
########## Example Requests #############
#########################################

############# PipelineAPI ################

pl = PipelineAPI()
import json
### Get all pipelines
all_pipelines = pl.get_all_pipeline_configs()
print(all_pipelines.status_code)
print(json.loads(all_pipelines.content))


### Create a pipeline
#creating a datasource for the pipeline
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

pl_config_DTO = PipeLineConfigDTO(ds_id,
                                              Transformation("data.test = 'abc'; return data;"),
                                              Metadata(author="icke",
                                                                    license= "none",
                                                                    display_name= "exampleRequest",
                                                                    description="none"
                                                                    )
                                              )
created_pipeline = pl.create_pipeline_config(pl_config_DTO)
#print(pl_config_DTO.get_json())
pl_id = json.loads(created_pipeline.content)["id"]

all_pipelines = pl.get_all_pipeline_configs()
print(all_pipelines.status_code)
print(json.loads(all_pipelines.content))

### Get pipeline x
retreived_pl = pl.get_pipeline_config_by_ID(pl_id)

### Update a pipeline
updated_pl_config_DTO = pl_config_DTO
updated_pl_config_DTO.meta_data.display_name = "none"

updated_pipeline = pl.update_pipeline_config(pl_id,updated_pl_config_DTO)

all_pipelines = pl.get_all_pipeline_configs()
print(all_pipelines.status_code)
print(json.loads(all_pipelines.content))

###delete a pipeline
##delete_pl = pl.delete_pipeline_config_by_ID(pl_id)
# all_pipelines = pl.get_all_pipeline_configs()
# print(all_pipelines.status_code)
# print(json.loads(all_pipelines.content))
### Delete all pipelines
deleted_all = pl.delete_all_pipeline_configs()

all_pipelines = pl.get_all_pipeline_configs()
print(all_pipelines.status_code)
print(json.loads(all_pipelines.content))

##clean up
cleaned = dsa.delete_Datasource(ds_id)
# all_pipelines = pl.get_all_pipeline_configs()
# print(json.loads(all_pipelines.content))

print("Cleaned successfully" if cleaned.status_code<400 else "Failed to clean up. Do it manually!")
"""