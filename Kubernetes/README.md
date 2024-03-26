# Kubernetes - demo app

The idea behind this project was to strengthen knowledge of Kubernetes. For this purpose, a [docker image](https://hub.docker.com/repository/docker/nanajanashia/k8s-demo-app) of a simple web application developed in HTML and Node.js was used and was deployed in a kubernetes cluster, a MongoDB database was also deployed. The application was connected to the database using external configuration data from the ConfigMap and Secret files, in addition to that the web app is also accessible from the browser using `MinikubeIP:NodePort`.
