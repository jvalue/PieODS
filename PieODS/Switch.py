import requests
import os
from .helpers import _url

def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r

def get_repo_zip(repo_owner="jvalue", repo_name="open-data-service", branch="main"):
    return requests.get('https://github.com/{}/{}/archive/{}.zip'.format(repo_owner, repo_name, branch))

def write_repo_zip(repo_zip, repo_name="open-data-service", destination_dir=None):

    #final_path = os.path.join(os.getcwd(), 'repo.zip')
    if destination_dir==None:
        destination_dir=os.getcwd()

    final_path = os.path.join(destination_dir, '{}.zip'.format(repo_name))

    with open(final_path, 'wb') as f:
        f.write(repo_zip.content)
    return final_path

import zipfile

def extract_repo_zip(path_to_zip_file, directory_to_extract_to):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    return directory_to_extract_to

def get_file_from_repo(file_name, repo_owner="jvalue", repo_name="open-data-service", branch="main", folder_name=None):
    return requests.get(_url('https://raw.githubusercontent.com',
                            repo_owner, repo_name, branch,
                            _url(folder_name, file_name) if folder_name!=None else file_name)
                        )


def write_file_from_repo(repo_file, file_name, destination_dir=None):
    if destination_dir==None:
        destination_dir=os.getcwd()

    final_path = os.path.join(destination_dir, file_name)

    with open(final_path, 'wb') as f:
        f.write(repo_file.content)
    return final_path

# required_files = ["docker-compose.yml", ".env"]

# for file in required_files:
#     write_file_from_repo(get_file_from_repo(file), file, "C:\Work\ODS\Docker")
#print(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"))
import subprocess
subprocess.run(["docker-compose", "up"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))
#subprocess.run(["docker-compose", "up"], cwd="C:\Work\ODS\Docker")


# # if subprocess.run(["docker-compose", "up"], cwd="C:\Work\ODS\Docker", capture_output=True, check=True)!=0:
# #     subprocess.run(["docker-compose", "down"], cwd="C:\Work\ODS\Docker", capture_output=True, check=True)
#client = docker.from_env()

# print(client.containers.list())
# # for cl in client.containers.list():
# #     cl.stop()
# # print(client.containers.list())
# print(client.images.list())
# creds = {"username":"shad00", "password":"Saher1988"}
#ims = client.images.pull("jvalue/open-data-service", all_tags=True , auth_config=creds)

# for im in ims:
#     client.containers.run(im)

#def first_start():
    
