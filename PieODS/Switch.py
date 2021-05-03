import os
from .helpers import extract_repo_zip_2, get_repo_zip
import subprocess
import threading
from . import Pipeline
from time import sleep

class ODSclient():
    def __init__(self, clone_parent_path=None, initialized=False) -> None: #path to where the ODS repo should be cloned
        self.initialized =  initialized
        self.github_repo_name = "open-data-service"
        self.github_repo_owner = "jvalue"
        self.github_branch = "main"
        self.repo_clone_parent_dirpath = os.path.dirname(os.path.realpath(__file__)) if clone_parent_path==None else clone_parent_path
        self.repo_clone_path = None
        self.running = False

    def __run_this(self, comms:list, wd):
        subprocess.run(comms, cwd=wd, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def start(self): #starts the ODS, initializes it if it is hasn't been 
        if not self.initialized:
            try:
                repo_response = get_repo_zip(repo_name=self.github_repo_name, repo_owner=self.github_repo_owner, branch=self.github_branch)
                if repo_response.status_code < 400:
                    self.repo_clone_path = extract_repo_zip_2(repo_response, self.repo_clone_parent_dirpath)
            except:
                print("Problem retrieving the ODS original repository!")
            if self.repo_clone_path!=None:
                #subprocess.run(["docker-compose", "up"], cwd=self.repo_clone_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                th = threading.Thread(target=self.__run_this, args=[["docker-compose", "up"], self.repo_clone_path], daemon=True)
                th.start()
                self.initialized=True
                # while th.is_alive():
                #     self.running = True
                self.running = True
                #self.initialized=True
                print("This")
        else:
            #subprocess.run(["docker-compose", "up --no-recreate"], cwd=self.repo_clone_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            th = threading.Thread(target=self.__run_this, args=[["docker-compose", "up --no-recreate"], self.repo_clone_path], daemon=True)
            th.start()
            # while th.is_alive():
            #     self.running = True
            self.running = True
            print("that")
    def stop(self): #stops the services but does not remove the containers -and session data-
        if self.repo_clone_path==None and os.path.isdir(os.path.join(self.repo_clone_parent_dirpath, "open-data-service-main")):
            pl = Pipeline.PipelineAPI()
            while "alive" not in pl.get_health_status().text:
                sleep(1)
            sleep(10)
            subprocess.run(["docker-compose", "stop"], cwd=os.path.join(self.repo_clone_parent_dirpath, "open-data-service-main"))
            self.running = False
        else:
            pl = Pipeline.PipelineAPI()
            while "alive" not in pl.get_health_status().text:
                sleep(1)
            sleep(10)
            subprocess.run(["docker-compose", "stop"], cwd=self.repo_clone_path)
            self.running = False
    def demolish(self): #stops and removes the containers -and session data-
        pl = Pipeline.PipelineAPI()
        while "alive" not in pl.get_health_status().text:
            sleep(1)
        sleep(10)
        subprocess.run(["docker-compose", "down -v"], cwd=self.repo_clone_path)
        self.running=False


    
# d = ODSclient(path="C:\Work\ODS")      
# d.start()  
# #print(os.path.realpath(__file__))
# # print(os.path.dirname(os.path.realpath(__file__)))

# def run_ODS_instance():
#     subprocess.run(["docker-compose", "up"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

# def stop_ODS_instance():
#     subprocess.run(["docker-compose", "stop"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

# def shut_down_ODS_instance():
#     subprocess.run(["docker-compose", "down"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))

# def rerun_ODS_instance():
#     #subprocess.run(["docker-compose", "up --no-recreate"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))
#     subprocess.run(["docker-compose", "start"], cwd=os.path.join(extract_repo_zip( write_repo_zip(get_repo_zip()), "C:\Work\ODS\Docker"), "open-data-service-main"))
 
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
# d = shut_down_ODS_instance()
# print("h")
