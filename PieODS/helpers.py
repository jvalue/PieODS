from datetime import datetime, timedelta, date
from io import BytesIO
import json
import requests
import zipfile
import os

from requests.models import Response

def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r


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
        self.raw_pairs = pairs
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

def get_repo_zip(repo_owner="jvalue", repo_name="open-data-service", branch="main"): #semi-hard coded
    return requests.get('https://github.com/{}/{}/archive/{}.zip'.format(repo_owner, repo_name, branch)) #depends on Github resources API design

def write_repo_zip(repo_zip, repo_name="open-data-service", destination_dir=None):
    #final_path = os.path.join(os.getcwd(), 'repo.zip')
    if destination_dir==None:
        destination_dir=os.getcwd()

    final_path = os.path.join(destination_dir, '{}.zip'.format(repo_name))

    with open(final_path, 'wb') as f:
        f.write(repo_zip.content)
    return final_path


def extract_repo_zip(path_to_zip_file=None, directory_to_extract_to=None):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    return directory_to_extract_to

def extract_repo_zip_2(zip_response:Response, directory_to_extract_to=None):
    with zipfile.ZipFile(BytesIO(zip_response.content), 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
        return os.path.join(directory_to_extract_to, zip_ref.namelist()[0]) #assuming gihub sends only the folder inside the zip
    #return directory_to_extract_to

#both work equally well!
def get_file_from_repo(file_name, repo_owner="jvalue", repo_name="open-data-service", branch="main", folder_name=None):
    return requests.get(_url('https://raw.githubusercontent.com',
                            repo_owner, repo_name, branch,
                            _url(folder_name, file_name) if folder_name!=None else file_name)
                        )

def get_file_from_repo_2(file_name, repo_owner="jvalue", repo_name="open-data-service", branch="main", folder_name=None):
    #Ex: https://github.com/thepanacealab/covid19_twitter/raw/master/dailies/2020-11-23/2020-11-23_clean-dataset.tsv.gz
    return requests.get(_url("https://github.com",
                            repo_owner, repo_name, "raw", branch,
                            _url(folder_name, file_name) if folder_name!=None else file_name)
                        )

def write_file_from_repo(repo_file, file_name, destination_dir=None):
    if destination_dir==None:
        destination_dir=os.getcwd()

    final_path = os.path.join(destination_dir, file_name)

    with open(final_path, 'wb') as f:
        f.write(repo_file.content)
    return final_path

def yield_days_between(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_current_timestamp():
    return datetime.now(tz =  datetime.now().astimezone().tzinfo).isoformat(timespec='milliseconds')
    
def list_days_between(start_date:date=date(2021, 1, 1), end_date:date=date(2021, 5, 5)):
    # for single_date in yield_days_between(start_date, end_date):
    #     print(single_date.strftime("%Y-%m-%d"))
    return [d for d in yield_days_between(start_date, end_date)]