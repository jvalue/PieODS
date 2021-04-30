#import requests
import os
from .helpers import extract_repo_zip, write_repo_zip, get_repo_zip
#import zipfile
import subprocess

#class ODS():



def run_ODS_instance():
    subprocess.run(["docker-compose", "up"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

def stop_ODS_instance():
    subprocess.run(["docker-compose", "stop"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

def shut_down_ODS_instance():
    subprocess.run(["docker-compose", "down"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

def rerun_ODS_instance():
    #subprocess.run(["docker-compose", "up --no-recreate"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))
    subprocess.run(["docker-compose", "start"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))
 
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
# required_files = ["docker-compose.yml", ".env"]

# for file in required_files:
#     write_file_from_repo(get_file_from_repo(file), file, "C:\Work\ODS\Docker")
#print(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"))
    
