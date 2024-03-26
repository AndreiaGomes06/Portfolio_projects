# Docker - demo app

The idea behind this project was to strengthen knowledge in Docker. For this purpose, a simple application developed in html and Node.js was used, and MongoDB was employed for data storage. All documents are Docker-based. It is possible to use the app by resorting to Docker or using Docker Compose, by creating a YAML document for this purpose. Finally, a Docker image was also generated based on the Dockerfile document.

## With Docker Compose

Step 1: Initiate mongodb and mongo-express
``` 
docker-compose -f docker-compose.yaml up 
```
Mongo-express UI can be accessed from the web browser under http://localhost:8080.

Step 2: Create a new database "my-db" in mongo-express UI.

Step 3: Following that create a new collection "users" in the database "my-db".

Step 4: Start the nodejs application locally - on the app directory of project.
```
cd app
npm install
node server.js
```
The nodejs app can be accessed from the web browser under http://localhost:3000.


## With Docker

Step 1: Create the docker network.
```
docker network create mongo-network 
```
Step 2: Initiate mongodb.
```
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password --name mongodb --net mongo-network mongo
```

Step 3: Initiate mongo-express.
```
docker run -d -p 8081:8081 -e ME_CONFIG_MONGODB_ADMINUSERNAME=admin -e ME_CONFIG_MONGODB_ADMINPASSWORD=password --net mongo-network --name mongo-express -e ME_CONFIG_MONGODB_SERVER=mongodb mongo-express   
```
Mongo-express UI can be accessed from the web browser under http://localhost:8081.

Step 4: Create `user-account` database and `users` collection in mongo-express.

Step 5: Start the nodejs application locally - on the app directory of project.
```
cd app
npm install
node server.js
```
The nodejs app can be accessed from the web browser under http://localhost:3000.

## Build a Docker image from the app using the Dockerfile

The '.' denotes the location of the Dockerfile.
```
docker build -t my-app:1.0 .
```
