# maerskdemo
this is private repo to demonstrate a deployment model which involves tools like docker, docker-compose, docker container lifecycle management tool like kubenetes using minikube, continuous integration and deployment using jenkins for a Python Flask app and a Redis database


Repo structure - 
.
|-- app
|   |-- app.py
|   |-- app_test.py
|   |-- docker-compose.yml
|   |-- Dockerfile
|   |-- __init__.py
|   |-- jenkinsfile
|   |-- logs
|   `-- requirements.txt
|-- k8s
|   |-- app-svc.yml
|   |-- frontend-service.yaml
|   |-- maerskDemo-deployment.yaml
|   |-- redis-master-deployment.yaml
|   |-- redis-master-service.yaml
|   |-- redis-slave-deployment.yaml
|   `-- redis-slave-service.yaml
|-- README.md
`-- Vagrantfile

Tools Stack - 
VirtualBox version - Version 6.0.15 r135660 (Qt5.6.3)
Docker version 1.13.1, build 4ef4b30/1.13.1
Compose file format - 3.1	     
Vagrant 2.2.5
Centos7 GNU/Linux
kernel version - 3.10.0-1062.9.1.el7.x86_64
minikube version: v1.2.0
kubectl v1.11.0"
Kubernetes v1.15.0
Python docker image - python:3
Redis docker image - redis:latest

As per expectations -  
* Dockerfiles for the app and a redis database. -> /app/Dockerfile
* Deployment definitions in the form of docker-compose or kubernetes manifests 
docker-compose -> /app/docker-compose.yml 
Kubernetes using minikube -> /k8s
* Build script, makefile and/or jenkinsfile, travis.yml or similar pipeline definition.
/app/jenkinsfile

This app is deployed in 2 ways here -

1) I have used vagrant here to spin up a centos7 linux machine where docker and docker-compose is installed. 
To manage and deploy multiple containers in our app, I have used docker-compose here. 
With docker-compose, we only have to write a docker-compose.yml file to configure both flask app and redis db services. 
Then, with a single command we created and started all the services from the configuration.

[vagrant@MaerskExercise app]$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                                     PORTS                    NAMES
2dd7e45cdee3        app_flask           "python app.py"          4 seconds ago       Up 2 second (health: starting)   0.0.0.0:8000->8000/tcp   app_flask_1
d7417b40e57b        redis:latest        "docker-entrypoint..."   5 seconds ago       Up 4 seconds                               0.0.0.0:6379->6379/tcp   redis

[vagrant@MaerskExercise app]$ docker-compose ps
   Name                  Command               State           Ports
-----------------------------------------------------------------------------
app_flask_1   python app.py                    Up(healthy)      0.0.0.0:8000->8000/tcp
redis         docker-entrypoint.sh redis ...   Up               0.0.0.0:6379->6379/tcp

[vagrant@MaerskExercise app]$ curl http://0.0.0.0:8000/get
{"time": "b'2020-02-02 12:47:10.403776'"}

[vagrant@MaerskExercise app]$ docker exec -it redis /bin/bash
root@6f5c6c2a0a3a:/data# redis-cli -h redis -p 6379

redis:6379> keys *
1) "time"

redis:6379> get time
"2020-02-02 12:47:10.403776"


The code resides and checked-in to a github repo into the master branch. 
with the help of jenkinsfile, CI pipeline is created on an instance setup on the same vagrant machine. 

In a professional setting for Flask or Python applications, we would want to also add a few things, which were not covered in this exercise.
Code commit to main or release branch: when tests pass, push an artifact, such as pip package or docker image, or an artifact repository
Submission of pull/merge request: run tests and provide feedback to git server, such as GitHub or GitLab, and block submission approval if tests fail.

2) uisng minikube to run this application stack on single-node Kubernetes cluster

Kubernetes is an open-source platform for managing containerized workloads and services, that facilitates both declarative configuration and automation.
Minikube is a tool that runs a single-node Kubernetes cluster in a virtual machine using virtualbox.

tasks accomplished here are -
Start up a Redis master
Start up Redis slaves
Start up the flask app api
Expose and test the api service.


ramaurya@ramaurya-mac maerskdemo (master)*$ kubectl get pod,svc,deployment -n maersk -o wide
NAME                               READY     STATUS    RESTARTS   AGE       IP           NODE       NOMINATED NODE   READINESS GATES
pod/flask-app-6d54cd9d4c-rbqkb     1/1       Running   0          2d6h      172.17.0.9   minikube   <none>           <none>
pod/redis-master-ccdbd9bff-wlclx   1/1       Running   0          2d9h      172.17.0.5   minikube   <none>           <none>
pod/redis-slave-6fc88d66b6-mctlw   1/1       Running   0          2d9h      172.17.0.6   minikube   <none>           <none>
pod/redis-slave-6fc88d66b6-vt9l6   1/1       Running   0          2d9h      172.17.0.7   minikube   <none>           <none>

NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE       SELECTOR
service/flask-app      NodePort    10.98.179.191   <none>        8000:30542/TCP   2d7h      app=flask-app,tier=frontend
service/redis-master   ClusterIP   10.96.198.139   <none>        6379/TCP         2d9h      app=redis,role=master,tier=backend
service/redis-slave    ClusterIP   10.109.98.87    <none>        6379/TCP         2d9h      app=redis,role=slave,tier=backend

NAME                                 READY     UP-TO-DATE   AVAILABLE   AGE       CONTAINERS   IMAGES                          SELECTOR
deployment.extensions/flask-app      1/1       1            1           2d7h      flask-app    docker.io/raviusit/maerskdemo   app=flask-app,tier=frontend
deployment.extensions/redis-master   1/1       1            1           2d9h      master       redis:latest                    app=redis,role=master,tier=backend
deployment.extensions/redis-slave    2/2       2            2           2d9h      slave        astro3/redisslave               app=redis,role=slave,tier=backend


Here, I have created a Redis Master Deployment (redis-master-deployment.yaml) which creates one pod (replicas: 1) fronteded with a service(redis-master-service.yaml).
The flask api applications needs to communicate to the Redis master to write its data. so we had to apply a Service to proxy the traffic to the Redis master Pod. This Service defines a policy to access the Pods.

Although the Redis master is a single pod, we can make it highly available to meet traffic demands by adding replica Redis slaves.
I have used redis-slave-deployment.yaml to deploy 2 pods of redis slaves and created a service redis-slave-service.yaml.

Finally, I have deployed the Flask api app with maerskDemo-deployment.yaml. The api has a web frontend serving the HTTP requests written in python using Flask web framework. It is configured to connect to the redis-master Service for write requests and the redis-slave service for Read requests.

Since we must configure this Api Service to be externally visible, so a client can request the Service from outside the container cluster. Minikube can only expose Services through NodePort. This is done using frontend-service.yaml.

Once everything is done, I tested the system - 

ramaurya@ramaurya-mac k8s (master)*$ curl http://192.168.99.100:30542/version
{"version": "1.1.1"}
ramaurya@ramaurya-mac k8s (master)*$ curl http://192.168.99.100:30542/get
{"time": "b'2020-02-03 09:37:43.456269'"}





