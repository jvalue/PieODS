from datetime import date
import json

from helpers import Unsupported_by_ODS
from typing import Literal, Union

class Config():
  def get_json(self):
    return json.dumps(self.get_dict(), default=str, ensure_ascii=False).encode()
  def __str__(self):
    return str(self.get_json().decode())



###########################################
###### Adapter Service Data Structs #######
###########################################

class ProtocolConfig(Config):
  def __init__(self, type:str, location:str, encoding:str) -> None:
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


class CSVparameters(Config):

  def __init__(self, col_separtor: str=None , line_separator: str=None, skip_first_data_row: bool=None, first_row_as_header: bool=None) -> None:
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


class FormatConfig(Config):

  def __init__(self, type:str=None, parameters:Union[dict , CSVparameters] =None) -> None:
      self.format_type = type
      self.format_parameters = parameters

  @property
  def format_type(self):
    return self._format_type
  @format_type.setter
  def format_type(self, new_format_type:str):
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
  def format_parameters(self, new_parameters:Union[dict , CSVparameters]):
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

class DatasourceTriggerConfig(Config):

  def __init__(self, first_ex:str=None, interval:int=None, periodic:bool = None) -> None:
      self.first_execution = first_ex #Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX)
      self.interval = int(interval)
      self.periodic = periodic
  def get_dict(self):
    return {
            "format":self.first_execution,
            "interval":self.interval,
            "periodic":self.periodic,
          }

class Metadata(Config):
  def __init__(self, author=None, display_name=None, license=None, description=None, timestamp=None) -> None:
    self.author = author
    self.display_name = display_name
    self.license = license
    self.description = description
    self.creation_timestamp = timestamp #Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX)
  def get_dict(self):#create dict of non-empty only
    to_be_returned= {
      "author": self.author,
      "displayName": self.display_name,
      "license": self.license,
      "description": self.description,
      "creationTimestamp": self.creation_timestamp,
      }
    return {k: v for k, v in to_be_returned.items() if v is not None}

class DataImport(Config):
  def __init__(self, id:int, timestamp, location) -> None:
      self.id = int(id)
      self.timestamp = timestamp #Date (format: yyyy-MM-dd'T'HH:mm:ss.SSSXXX)
      self.location = location #String (relative URI)
  def get_dict(self):
    return {
      "id": self.id,
      "timestamp": self.timestamp,
      "location": self.location
    }

class AdapterConfig(Config):
  def __init__(self, protocol_config:ProtocolConfig, format_config:FormatConfig) -> None:
      self.protocol_config = protocol_config
      self.format_config = format_config
  def get_dict(self):
    return {
      "protocol": self.protocol.get_dict(), 
      "format": self.format.get_dict()
    }

class DatasourceConfig(Config):
  def __init__(self, id:int,
                protocol_config:ProtocolConfig,
                format_config:FormatConfig,
                trigger_config:DatasourceTriggerConfig,
                meta:Metadata):
    self.id = int(id)
    self.protocol_config = protocol_config
    self.format_config = format_config
    self.trigger_config = trigger_config
    self.meta_data = meta
  def get_dict(self):
    return {
      "id": self.id,
      "protocol": self.protocol_config.get_dict(),
      "format": self.format_config.get_dict(),
      "trigger": self.trigger_config.get_dict(),
      "metadata": self.meta_data.get_dict()
    }

class KVpairs(Config):
    """
    Example:
    +++++++++

    ::

    {
        "station": "BONN",
        "secret": 1
    }
    """
    def __init__(self, *pairs) -> None:
        self.kv_pairs = {}
        for p in pairs: #pairs is an iterable containing single-KV dicts
            for k in p:
                self.kv_pairs[k] = p[k]
    def get_dict(self):
        return self.kv_pairs

class Parameters(KVpairs):
    """
    {
  "parameters": <<Map of type <String, String> for open parameter to replace with the value>>
    }

    Example:
    +++++++++

    ::

        {
        "parameters": {
            "station": "BONN"
            }
        }
    """
    #   def __init__(self, *pairs) -> None:
    #     self.kv_pairs = {}
    #     for p in pairs:
    #       for k in p:
    #         self.kv_pairs[k] = p[k]
    def get_dict(self):
        return {
        "parameters":self.kv_pairs
        }



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




#################################################
######## Storage Service Data Structs ###########
#################################################
class PipeLineID(Config):
    def __init__(self, id:int) -> None:
        self.pipelineID = int(id)
    def get_dict(self):
        return {
            "pipelineid": self.pipelineID
        }

class DataForStorage(Config):
    def __init__(self, data:json, timestamp:str, origin:str, license:str, pipelineid:int) -> None:
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




#################################################
###### Notification Service Data Structs ########
#################################################

class WebhookNotificationParameter(Config):
    def __init__(self, url:str) -> None:
        self.url = url
    def get_dict(self):
        return {
            "parameter":{
                "url":self.url
            }
        }

class SlackNotificationParameter(Config):
    def __init__(self, workspaceId:str, channelId:str, secret:str) -> None:
        self.workspace_ID = workspaceId
        self.channel_ID = channelId
        self.secret = secret
    def get_dict(self):
        return {
            "parameter":{
                "workspaceId":self.workspace_ID,
                "channelId":self.channel_ID,
                "secret":self.secret
            }
        }

class FirebaseNotificationParameter(Config):
    def __init__(self, projectId:str, clientEmail:str, privateKey:str, topic:str) -> None:
        self.project_ID = projectId
        self.client_email = clientEmail
        self.private_key = privateKey
        self.topic = topic
    def get_dict(self):
        return {
            "parameter":{
                "projectId":self.project_ID,
                "clientEmail":self.client_email,
                "privateKey":self.private_key,
                "topic":self.topic
            }
        }

class NotificationWriteModel(Config):
    def __init__(self, pipelineId:int, condition:str,
                type:Literal["WEBHOOK", "SLACK" , "FCM"],
                parameter:Union[SlackNotificationParameter, FirebaseNotificationParameter, WebhookNotificationParameter] ) -> None:
        self.pipeline_ID = int(pipelineId)
        self.condition = condition
        self.type = type
        self.parameter = parameter
    def get_dict(self):
        return {
            "pipelineId": self.pipeline_ID,
            "condition": self.condition,
            "type": self.type,
            "parameter": self.parameter.get_dict()
            }

class NotificationTriggerConfig(Config):
    def __init__(self, pipelineId:int, pipelineName:str, data:KVpairs):
        self.pipeline_ID = int(pipelineId)
        self.pipeline_name = pipelineName
        self.data = data
    def get_dict(self):
        return {
            "pipelineId": self.pipeline_ID,
            "pipelineName": self.pipeline_name,
            "data": self.data.get_dict()
            }

#TO-DO#
#class JobResult #may need to implement that to expand postprocessing functionality
