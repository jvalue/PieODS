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
from helpers import _url

#thinking about doing OOP version, might be easier to distinguish concepts like adapter and datasource that are in the same file
#should be imported from a configs or main file
BASE_URL = "http://localhost:9000/api/pipelines"

relative_paths = {
    "version":"version",
    "job":"job",
    "trigger":"trigger",
    "configs":"configs",
}


# def _url(r, *path_components):
#     """
#     .. warning:: Don't do this, it will break your system!
#     """
#     for c in path_components:
#         r += "/{}".format(str(c)) 
#     return r
    
def get_health_status():
    return requests.get(BASE_URL) 

def get_service_version():
    return requests.get(_url(BASE_URL, relative_paths["version"]))

#assuming body is always json
def execute_pipeline(PipelineExecutionRequest):
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
    return requests.post(_url(BASE_URL, relative_paths["job"]), json=PipelineExecutionRequest)

def trigger_pipeline(PipelineConfigTriggerRequest):
    """Triggers the pipeline

    Parameters
    ----------
    PipelineConfigTriggerRequest: json
    """
    return requests.post(_url(BASE_URL, relative_paths["trigger"]), json=PipelineConfigTriggerRequest)

def get_all_pipeline_configs(PipelineConfigTriggerRequest):
    return requests.get(_url(BASE_URL, relative_paths["configs"]))

def get_pipeline_config_by_ID(PipelineID):
    """
    Parameters
    ----------
    PipelineID: int
    """
    return requests.get(_url(BASE_URL, relative_paths["configs"], PipelineID))

def create_pipeline_config(PipelineconfigDTO):
  """Create a pipeline config

  :param PipelineconfigDTO: identifier of a pipeline config
  :type PipelineconfigDTO: json
  :return: [description]
  :rtype: [type]
  """  ""
  return requests.post(_url(BASE_URL, relative_paths["configs"]), json=PipelineconfigDTO)

def update_pipeline_config(PipelineID, PipelineconfigDTO):
  """Update a pipeline config.

  :param PipelineconfigDTO: [description]
  :type PipelineconfigDTO: [type]
  :return: [description]
  :rtype: [type]
  """  ""
  return requests.put(_url(BASE_URL, relative_paths["configs"], PipelineID), json=PipelineconfigDTO)

def delete_all_pipeline_configs():
    return requests.delete(_url(BASE_URL, relative_paths["configs"]))

def get_pipeline_config_by_ID(PipelineID):
    """
    Parameters
    ----------
    PipelineID: int
    """
    return requests.delete(_url(BASE_URL, relative_paths["configs"], PipelineID))