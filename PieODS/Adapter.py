"""Adapter Service of the ODS
==========================

The adapter service fetches data from external data sources and provides
them via a HTTP API in JSON format. The data coming from the external
sources can be fetched over various protocols and can have various
formats.

Concepts
--------

-  **Datasource**: Description of a datasource. This description can be
   transformed into an *adapter* to import data from a data source and
   forward it to downstream services.
-  **Adapter**: Configuration to import data from a datasource; can be
   derived from a *datasource* config, or is provided by a user to
   generate a *preview*.
-  **Preview**: Stateless preview that allows executing a datasource
   config once and synchronously returning the result of the import and
   interpretation; does not send the result to downstream services
   (difference to creating and triggering a datasource).
-  **Data import**: One execution of the import of a *datasource*. The
   result and metadata get stored in the database and can be accessed
   for each *datasource*.

Current Features
----------------

-  Currently the adapter service is only a prototype and can handle
   JSON, XML and CSV files that can be fetched over HTTP. ## Planned
   Features The handling of new protocols and formats is going to be
   implemented.

Planned protocols: \* ftp

Planned formats:

Getting Started
---------------

-  Build with ``./gradlew build``
-  Run unit tests with ``./gradlew test``
-  Run integration test with ``./gradlew integrationTest`` (note that a
   instance of the adapterService needs to be up).
-  Start with ``./gradlew bootRun`` - not recommended
-  Use Docker-Compose:
   ``docker-compose -f ../docker-compose.yml --env-file ../.env up adapter``
   builds Docker images and starts them up. Note that you need to delete
   existing docker images from your local docker daemon to have recent
   changes integrated.
-  For integration testing run
   ``docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env up adapter-it``
-  To analyze the logs of the service under test we recommend using
   lazydocker. Alternatively, you can attach manually to the adapter
   container using the docker cli.
-  After running integration tests dependant services (e.g. rabbit-mq)
   keep running. In order to stop all services and return to a clean,
   initial state run
   ``docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml down``.

Architecture
------------

Each adapter consists of a importer that is responsible for the handling
of the data source protocol and a interpreter that reformats the given
data to json format. The implemented importers and interpreters are
stored in a map in the AdapterManager. For each request to the
AdapterEndpoint, the AdapterManager chooses a appropriate Interpreter
and Importer and creates an Adapter to handle the request. Information
about data format, protocal and location of the external data source to
include are stored in a AdapterConfig file which is included in the
request. The basic architecture of the ODS is depicted below. Support
for new protocols or data formats can easily be achieved by adding
classes implementing the importer/interpreter interface and registering
those classes in the AdapterManager. |basic architecture of the adapter
service|

API Docs
--------

Adapter API (data import)
-------------------------

+---------------------------+----------+------------------+---------------------------------------------------------------------------+
| Endpoint                  | Method   | Request Body     | Response Body                                                             |
+===========================+==========+==================+===========================================================================+
| *base\_url*/version       | GET      | -                | String containing the application version                                 |
+---------------------------+----------+------------------+---------------------------------------------------------------------------+
| *base\_url*/formats       | GET      | -                | JsonArray of data formats available for parsing and possible parameters   |
+---------------------------+----------+------------------+---------------------------------------------------------------------------+
| *base\_url*/protocols     | GET      | -                | JsonArray of protocols available for importing and possible parameters    |
+---------------------------+----------+------------------+---------------------------------------------------------------------------+
| *base\_url*/preview       | POST     | AdapterConfig    | PreviewResponse                                                           |
+---------------------------+----------+------------------+---------------------------------------------------------------------------+
| *base\_url*/preview/raw   | POST     | ProtocolConfig   | PreviewResponse                                                           |
+---------------------------+----------+------------------+---------------------------------------------------------------------------+

When started via docker-compose *base\_url* is
``http://localhost:9000/api/adapter``

Adapter Config
~~~~~~~~~~~~~~

::

    {
      "protocol": ProtocolConfig, 
      "format": {
        "type": "JSON" | "XML" | "CSV",
        "parameters": { } | CSVParameters
      }
    }

Protocol Config
~~~~~~~~~~~~~~~

::

    {
      "type": "HTTP",
      "parameters": {
       "location": String,
       "encoding": String
      }
    }

CSV Parameters
~~~~~~~~~~~~~~

::

    {
      "columnSeparator": char,
      "lineSeparator": char,
      "skipFirstDataRow": boolean,
      "firstRowAsHeader": boolean
    }

PreviewResponse
~~~~~~~~~~~~~~~

::

    {
        "data": <<Stringified JSON or RAW representation of payload>>
    }

Datasource API (configs)
------------------------

+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| Endpoint                                               | Method   | Request Body        | Response Body                                                        |
+========================================================+==========+=====================+======================================================================+
| *base\_url*/datasources                                | GET      | -                   | All DatasourceConfigs                                                |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}                           | GET      | -                   | DatasourceConfig wih {id}                                            |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources                                | POST     | Datasource Config   | Created datasource, id generated by server                           |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}                           | PUT      | Datasource Config   | Updated datasource with {id}                                         |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources                                | DELETE   | -                   | Delete all datasources                                               |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}                           | DELETE   | -                   | Delete datasource with {id}                                          |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/trigger                   | POST     | Parameters          | DataImport                                                           |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/imports                   | GET      | -                   | All DataImports for datasource with {id}                             |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/imports/{importId}        | GET      | -                   | DataImports with {importId} for datasource with {id}                 |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/imports/latest            | GET      | -                   | Latest DataImport for datasource with {id}                           |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/imports/{importId}/data   | GET      | -                   | Actual data of DataImport with {importId} for datasource with {id}   |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+
| *base\_url*/datasources/{id}/imports/latest/data       | GET      | -                   | Actual data for latest DataImport for datasource with {id}           |
+--------------------------------------------------------+----------+---------------------+----------------------------------------------------------------------+

When started via docker-compose *base\_url* is
``http://localhost:9000/api/adapter``

Datasource Config
~~~~~~~~~~~~~~~~~

::

    {
      "id": Number,
      "protocol": ProtocolConfig,
      "format": FormatConfig,
      "trigger": TriggerConfig,
      "metadata": Metadata
    }

Protocol Config
~~~~~~~~~~~~~~~

::

    {
        "type": "HTTP",
        "parameters": {
          "location": String,
          "encoding": String
        }
    }

Format Config
~~~~~~~~~~~~~

::

    {
      "format": {
        "type": "JSON" | "XML" | "CSV",
        "parameters": { } | CSVParameters
      }
    }

CSV Parameters
~~~~~~~~~~~~~~

::

    {
      "columnSeparator": char,
      "lineSeparator": char,
      "skipFirstDataRow": boolean,
      "firstRowAsHeader": boolean
    }

TriggerConfig
~~~~~~~~~~~~~

::

    {
      "firstExecution": Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX),
      "interval": Number,
      "periodic:" Boolean
    }

Metadata
~~~~~~~~

::

    {
      "author": String,
      "displayName": String,
      "license": String,
      "description": String,
      "creationTimestamp: Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX),
    }

Datasource Config Event (AMQP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    {
      "datasource": DatasourceConfig
    }

Parameters
~~~~~~~~~~

::

    {
      "parameters": <<Map of type <String, String> for open parameter to replace with the value>>
    }

DataImport
~~~~~~~~~~

::

    {
      "id": Number,
      "timestamp": Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX)
      "location": String (relative URI)
    }

"""
# from helpers import _url
from typing import Type
import requests
import json
#from .helpers import *
def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r

# class Config():
#   def __init__(self) -> None:
#       self.dict = 

class Unsupported_by_ODS(Exception):
  def __init__(self, *args: object) -> None:
      super().__init__(*args)
  

class ProtocolConfig():
  def __init__(self, type, location, encoding) -> None:
      self.type = type
      self.parameters = {"location":location, "encoding":encoding}

  @property
  def type(self):
    return self._type
  @type.setter
  def type(self, new_type):
    if type(new_type)==str:
      if new_type == "HTTP": #should be extended to fetch (AdapterAPI.get_supported_protocols()) the supported protocols and loop over them
        self._type = new_type
      else:
        raise Unsupported_by_ODS("The protocol '{}' is not yet supported!".format(new_type))
    else:
      raise TypeError("Invalid value for protocol type!\nType must be passed as string!")

  @property
  def parameters(self):
    return self._parameters
  @parameters.setter
  def parameters(self, new_parameters):
    if type(new_parameters)==dict:
      self._parameters = new_parameters
    else:
      raise TypeError("Invalid type for protocol parameters!\nParameters must be passed as dict!")
  
  def get_dict(self):
    return {"type":self.type, "parameters":self.parameters}
  def get_json(self):
    return json.dumps(self.get_dict())
  def __str__(self):
    return str(self.get_json())

class CSVparameters():
  def __init__(self, col_separtor=None, line_separator=None, skip_first_data_row=None, first_row_as_header=None) -> None:
      self.column_separator = col_separtor
      self.line_separator = line_separator
      self.skip_first_data_row = skip_first_data_row
      self.first_row_as_header = first_row_as_header
  def get_dict(self):
    return  {
      "columnSeparator": self.column_separator,
      "lineSeparator": self.line_separator,
      "skipFirstDataRow": self.skip_first_data_row,
      "firstRowAsHeader": self.first_row_as_header
    }
  def get_json(self):
    return json.dumps(self.get_dict())
  def __str__(self):
    return str(self.get_json())

class FormatConfig():
  def __init__(self, type=None, parameters =None) -> None:
      self.format_type = type
      self.format_parameters = parameters

  @property
  def format_type(self):
    return self._format_type
  @format_type.setter
  def format_type(self, new_format_type):
    if type(new_format_type)==str:
      new_format_type= new_format_type.upper()
      if new_format_type=="JSON" or new_format_type=="XML" or new_format_type=="CSV":
        self._format_type = new_format_type
      else:
        raise Unsupported_by_ODS("This format type is not supported!")
    else:
      raise TypeError("Invalid value for format type!\nFormat type must be passed as string!")

  @property
  def format_parameters(self):
    return self._format_parameters
  @format_parameters.setter
  def format_parameters(self, new_parameters):
    if new_parameters=={} or new_parameters==None:
      self._format_parameters = new_parameters
    elif type(new_parameters)==CSVparameters:
      self._format_parameters = new_parameters.get_dict()
    else:
      raise TypeError("Invalid type for format config parameters!\nParameters must be either an empty dict or a CSVparameters object!") 
  
  def get_dict(self):
    return {
            "format":{
              "type":self.format_type,
              "parameters":self.format_parameters
            }
          }
  def get_json(self):
    return json.dumps(self.get_dict())
  def __str__(self):
    return str(self.get_json())


class TriggerConfig():
  def __init__(self, first_ex=None, ) -> None:
      self.






a = ProtocolConfig("HTTP","There" ,"UTF-8" )
print(a  )   

# class AdapterConfig(ProtocolConfig, formatConfig):
#   def __init__(self) -> None:
#       self.protocol = Protocol  

#Adapter API (data import)
class AdapterAPI():
    def __init__(self) -> None:
        self.BASE_URL = "http://localhost:9000/api/adapter"

        self.relative_paths = {
            "version":"version",
            "formats":"formats",
            "protocols":"protocols",
            "preview":"preview",
            }
        

    def get_application_version(self):
        return requests.get(_url(self.BASE_URL, self.relative_paths["version"]))

    def get_supported_data_formats(self):
        return requests.get(_url(self.BASE_URL, self.relative_paths["formats"]))

    def get_supported_protocols(self):
        """Get all supported protocols

        :return: [description]
        :rtype: [type]
        """    
        return requests.get(_url(self.BASE_URL, self.relative_paths["protocols"]))

    def execute_configured_preview(self, AdapterConfig):
        #Note: AdapterConfig consists of both the protcol of data transfer and the format that it should be delivered in.
        #while the raw_preview needs only the protocol of data transfer
        return requests.post(_url(self.BASE_URL, self.relative_paths["preview"]), json=AdapterConfig)

    def execute_raw_preview(self, ProtocolConfig):
        return requests.post(_url(self.BASE_URL, self.relative_paths["preview"]), json=ProtocolConfig)

ada = AdapterAPI()
print(ada.get_supported_protocols().text)
# print(ada.get_supported_data_formats().text)
#Datasource API
#As it has the same self.BASE_URL, I put it in the  same file.
class DatasourceAPI():
  def __init__(self) -> None:
      self.BASE_URL = "http://localhost:9000/api/adapter"


      self.relative_paths = { 
          "datasources":"datasources",
          # "trigger":"datasources/{}/trigger", #datasource id goes in here
          # "imports":"datasources/{}/imports", #datasource id goes in here
          # "latest_DataImport":"datasources/{}/imports/latest", #datasource id goes in here
          # "lataest_DataImport":"datasources/{}/imports/{}/data", #datasource id then Dataimport id
          # "lataest_DataImport":"datasources/{}/imports/latest", #datasource id goes in here
          
          }
  def get_all_DatasourceConfigs(self):
    """Gets all DatasourceConfigs.
    Examples of a DatasourceConfig is:
      {
      "id": Number,
      "protocol": ProtocolConfig,
      "format": FormatConfig,
      "trigger": TriggerConfig,
      "metadata": Metadata
      }

    :return: DatasourceConfigs
    :rtype: json
    """
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"]))
       
  def get_DatasourceConfig(self, DatasourceID):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID))

  def create_Datasource(self, DatasourceConfig):
    return requests.post(_url(self.BASE_URL, self.relative_paths["datasources"]), json=DatasourceConfig)

  def update_Datasource(self, DatasourceID, DatasourceConfig):
    return requests.put(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID), json=DatasourceConfig)

  def delete_all_Datasources(self):
    return requests.delete(_url(self.BASE_URL, self.relative_paths["datasources"]))
  
  def delete_Datasource(self, DatasourceID):
    return requests.delete(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID))

  def trigger_DataImport(self, DatasourceID, Parameters):
    return requests.post(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "trigger"), json=Parameters)

  def trigger_DataImport(self, DatasourceID, Parameters):
    return requests.post(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "trigger"), json=Parameters)

  def get_All_Dataimports_of_Datasource(self, DatasourceID):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "imports"))

  def get_Dataimport_of_Datasource(self, DatasourceID, importId):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "imports", importId))

  def get_latest_Dataimport_of_Datasource(self, DatasourceID):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "imports", "latest"))

  def get_Data_of_Dataimport_of_Datasource(self, DatasourceID, importId):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "imports", importId, "data"))

  def get_Data_of_latest_Dataimport_of_Datasource(self, DatasourceID):
    return requests.get(_url(self.BASE_URL, self.relative_paths["datasources"], DatasourceID, "imports", "latest", "data"))


#x = DatasourceAPI()