import datetime
import json

def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r

def get_current_timestamp():
    return datetime.datetime.now(tz =  datetime.datetime.now().astimezone().tzinfo).isoformat(timespec='milliseconds')

class Unsupported_by_ODS(Exception):
    pass

class Config():
  def get_json(self):
    #return json.dumps(self.get_dict(), default=str, ensure_ascii=False).encode()
    return json.dumps(self.get_dict())#,  ensure_ascii=False , indent=2, separators=(',', ': '))#.replace('\\"',"\"")

  def __str__(self):
    #return str(self.get_json().decode())
    return str(self.get_json())

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
      "description": self.description if self.description!=None else "none", #Important: the API rejects Metadata structs with missing description.
      "creationTimestamp": self.creation_timestamp
      }
    return {k: v for k, v in to_be_returned.items() if v is not None}