# Docker - demo app

The idea behind this project was to strengthen knowledge in Docker. For this purpose, a simple application developed in html and Node.js was used, and MongoDB was employed for data storage. All documents are Docker-based. It is possible to use the app by resorting to Docker or using Docker Compose, by creating a YAML document for this purpose. Finally, a Docker image was also generated based on the Dockerfile document.

# With Docker Compose

Step 1: Initiate mongodb and mongo-express
``` 
docker-compose -f docker-compose.yaml up 
```
Mongo-express UI can be accessed from the web browser under localhost:8080.

Step 2: Create a new database "my-db" in mongo-express UI.

Step 3: Following that create a new collection "users" in the database "my-db".

Step 4: Initiate the Node server.
```
cd app
npm install
node server.js
```
The nodejs app can be accessed from the web browser under http://localhost:3000.

# With Docker


