import json
from helpers import Unsupported_by_ODS

class Config():
  def get_json(self):
    return json.dumps(self.get_dict())
  def __str__(self):
    return str(self.get_json())

class ProtocolConfig(Config):
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


class CSVparameters(Config):

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


class FormatConfig(Config):

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


class TriggerConfig(Config):

  def __init__(self, first_ex=None, interval=None, periodic = None) -> None:
      self.first_execution = first_ex
      self.interval = interval
      self.periodic = periodic
  def get_dict(self):
    return {
            "format":self.first_execution,
            "interval":self.interval,
            "periodic":self.periodic,
          }

class Metadata(Config):
  def __init__(self, author, display_name, license, description, timestamp) -> None:
    self.author = author
    self.display_name = display_name
    self.license = license
    self.description = description
    self.creation_timestamp = timestamp
  def get_dict(self):
    return {
      "author": self.author,
      "displayName": self.display_name,
      "license": self.license,
      "description": self.description,
      "creationTimestamp": self.creation_timestamp,
      }

class DataImport(Config):
  def __init__(self, id, timestamp, location) -> None:
      self.id = int(id)
      self.timestamp = timestamp
      self.location = location
  def get_dict(self):
    return {
      "id": self.id,
      "timestamp": self.timestamp,
      "location": self.location
    }

class AdapterConfig(Config):
  def __init__(self, protocol_config, format_config) -> None:
      self.protocol_config = protocol_config
      self.format_config = format_config
  def get_dict(self):
    return {
      "protocol": self.protocol.get_dict(), 
      "format": self.format.get_dict()
    }

class DatasourceConfig(Config):
  def __init__(self, id, protocol_config, format_config, trigger_config, meta):
    self.id = int(id)
    self.protocol_config = protocol_config
    self.format_config = format_config
    self.trigger_config = trigger_config
    self.meta_data = meta
  def get_dict(self):
    return {
      "id": self.id,
      "protocol": self.protocol_config,
      "format": self.format_config,
      "trigger": self.trigger_config,
      "metadata": self.meta_data
    }

class Parameters(Config):
  """
  Example:
  +++++++++

  ::

      {
      "parameters": {
        "station": "BONN"
        }
      }
  """
  def __init__(self, *pairs) -> None:
    self.kv_pairs = {}
    for p in pairs:
      for k in p:
        self.kv_pairs[k] = p[k]
    def get_dict(self):
      return {
        "parameters":self.kv_pairs
      }


