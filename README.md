# PWP SPRING 2021
# PROJECT NAME: Calorie tracker
# Group information
* Student 1. Oana Stoicescu oana.stoicescu@oulu.fi
* Student 2. jjuutine20@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Release notes

1.0.6 - Updated dependencies: Python, Flask, SqlAlchemy, Node, Material-ui

1.0.5 - Updated Node dependencies and optimized docker images

1.0.4 - Fixed dependency issues by updating Python and server dependencies to latest stable versions, and by fixing Node version.

1.0.3 - Added docker-compose configuration

1.0.2 - Added PUT Meal functionality to the React Client

1.0.1 - Added delete Portion functionaly to the React Client

1.0 - First version of the PWP

## How to run the Unit Tests in Docker:

### Linux

prerequisite: Docker environment available

1. Go to the flask-server directory

```cd flask-server```

2. Build the pwp-tests Docker image 

```docker build . -f Dockerfile-tests --tag pwp-tests:1.0```

3. Execute the tests

```docker run --rm pwp-tests:1.0```

(Optional)

4. Clean up the image from consuming storage space

```docker image rm pwp-tests:1.0```


## How to run the app with docker-compose

prerequisite: **docker-compose installed** (tested on: Ubuntu 24.04 LTS)

1. Build and start the service

```docker-compose up```

2. Try the application

http://localhost:3000

3. Stop the service

```Ctrl+C```

4. Clean up

```docker-compose down --rmi all```


## How to prepare the Python environment and execute the unit tests:

### Linux


prerequisite: **python3 installed** (tested on: Ubuntu 24.04 LTS)

1. Go to the flask-server directory

```cd flask-server```

2. Create a new virtual environment for installation

```python3 -m venv pwp-environment```

3. Switch to the newly create environment

```source pwp-environment/bin/activate```

4. Install dependencies

```pip install -r requirements.txt```

5. Execute unit tests

```pytest```


### Windows 10


prerequisite: **python3 installed** (tested on: Windows 10 Home)

1. Go to the flask-server directory

```cd flask-server```

2. Create a new virtual environment for installation

```python -m venv pwp-environment```

3. Switch to the newly create environment

```pwp-environment\Scripts\activate.bat```

4. Install dependencies

```pip install -r requirements.txt```

5. Execute unit tests

```pytest```



## How to run the App in Docker:

### Linux

prerequisite: Docker environment available

1. Go to the flask-server directory

```cd flask-server```

2. Build the pwp Docker image 

```docker build . --tag pwp:1.0```

3. Start the container

```docker run -d --name pwp --rm -p 5000:5000 -p 3000:3000 pwp:1.0```

4. Navigate your favourite browser to http://localhost:3000/

5. Stop the container

```docker stop pwp```

6. Clean up the image from consuming storage space

```docker image rm pwp:1.0```
