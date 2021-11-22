# mycomfort
Windhager myComfort custom component for Home Assistant

This a first experimental implementation of Windhager myComfort integration within Home Assistant.

This code should be copied to `custom_components/mycomfort`.

You should also copy the project [mycomfortclient](https://github.com/sarabanjina/mycomfortclient) to the folder `custom_components/mycomfort/mycomfortclient`.

You can then configure the integration in `configuration.yaml` : 
```
mycomfort:
  host: "192.168.1.10"
  port: "80"
  username: "USER"
  password: "yoursecurepassword"
  scan_interval: 60
```
