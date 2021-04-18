"""
# Open Data Service - Notification-Service

## Build

`npm install`

`npm run transpile`

## Run

`npm start`

## Running unit tests

Use `npm test` to run the unit tests.

## Running end-to-end tests

* For integration testing run 
  
  ```docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml --env-file ../.env up notification-it```

* To analyze the logs of the service under test we recommend using lazydocker. Alternatively, you can attach manually to the notification container using the docker cli. 

* After running integration tests dependant services (e.g. rabbit-mq) keep running. In order to stop all services and return to a clean, initial state run 
  
  ```docker-compose -f ../docker-compose.yml -f ../docker-compose.it.yml down```. 


## API
| Endpoint  | Method  | Request Body  | Response Body | Description |
|---|---|---|---|---|
| *base_url*/ | GET | - | text | Get health status |
| *base_url*/version | GET | - | text | Get service version |
| *base_url*/configs | POST | NotificationWriteModel | - | Create a notification config |
| *base_url*/configs?pipelineId={pipelineId} | GET | - | NotificationReadModel[] | Get all notifications, filter by pipelineId if provided |
| *base_url*/configs/{id} | GET | - | NotificationReadModel | Get notification by id |
| *base_url*/configs/{id} | PUT | NotificationWriteModel | - | Update notification |
| *base_url*/configs/{id} | DELETE | - | - | Delete notification |
| *base_url*/trigger | POST | TriggerConfig | - | Trigger all notifications related to pipeline |


### NotificationWriteModel
Base model:
```
{
  "pipelineId": number,
  "condition": string,
  "type": "WEBHOOK" | "SLACK" | "FCM",
  "parameter": {
    ... see below
  }
}
```

Parameter for a webhook notification: 
```
"parameter": {
    "url": string
}
```


Parameter for a slack notification: 
```
"parameter": {
    "workspaceId": string
    "channelId": string
    "secret": string
}
```


Parameter for a firebase notification: 
```
"parameter": {
    "projectId": string
    "clientEmail": string
    "privateKey": string
    "topic": string
}
```

### NotificationReadModel
Equal to `NotificationWriteModel`, but has an additional `id: number` field.

### TriggerConfig
```
{
  "pipelineId": number,
  "pipelineName": string,
  "data": object
}
```


### Slack notification walkthrough
* Create a slack app for your slack channel and enable activations as discribed [here](https://api.slack.com/messaging/webhooks).
* Determine your apps' incoming webhook url at the slack [dashboard](https://api.slack.com/apps).
* POST a slackRequest under the endpoint ```/configs```. The workspaceId, channelId and secret fields can be taken from the parts of the incoming webhook url (separated by '/', in the given order).
* Go to your configured channel and be stunned by the magic. 

"""

#import requests
##from requests.models import requote_uri
#from helpers import _url
from .helpers import *

class NotificationAPI():
    def __init__(self) -> None:
        self.BASE_URL = "http://localhost:9000/api/notification"
        self.relative_paths = {
            "version":"version",
            "trigger":"trigger",
            "configs":"configs",
        }

    def get_health_status(self):
        return requests.get(_url(self.BASE_URL))

    def get_service_version(self):
        return requests.get(_url(self.BASE_URL, self.relative_paths["version"]))

    def create_notificationConfig(self, NotificationWriteModel):
        return requests.get(_url(self.BASE_URL, self.relative_paths["configs"]), json=NotificationWriteModel)

    def get_all_notificationConfigs(self):
        return requests.get(_url(self.BASE_URL, self.relative_paths["configs"]))

    def get_pipeline_notificationConfigs(self, PipelineID):
        return requests.get(_url(self.BASE_URL, "{}?pipelineId={}".format(self.relative_paths["configs"], PipelineID)))
    
    def get_notificationConfig(self, NotificationConfigID):
        return requests.get(_url(self.BASE_URL, self.relative_paths["configs"], NotificationConfigID))

    def get_notificationConfig(self, NotificationConfigID):
        return requests.get(_url(self.BASE_URL, self.relative_paths["configs"], NotificationConfigID))

    def update_notificationConfig(self, NotificationConfigID, NotificationWriteModel):
        return requests.put(_url(self.BASE_URL, self.relative_paths["configs"], NotificationConfigID), json=NotificationWriteModel)

    def delete_notificationConfig(self, NotificationConfigID):
        return requests.delete(_url(self.BASE_URL, self.relative_paths["configs"], NotificationConfigID))

    def trigger_all_notifications(self, TriggerConfig):
        return requests.put(_url(self.BASE_URL, self.relative_paths["trigger"]), json=TriggerConfig)
