# PWP SPRING 2021
# PROJECT NAME: Calorie tracker
# Group information
* Student 1. Oana Stoicescu oana.stoicescu@oulu.fi
* Student 2. jjuutine20@student.oulu.fi
* Student 3. Name and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## How to run the Unit Tests in Docker:

### Linux

prerequisite: Docker environment available

1. Build the docker pwp-tests package

```docker build . -f Dockerfile-tests --tag pwp-tests:1.0```

2. Execute the tests

```docker run --rm pwp-tests:1.0```

(Optional)

3. Clean up the image from consuming storage space

```docker image rm pwp-tests:1.0```



## How to prepare the Python environment and execute the unit tests:

### Linux


prerequisite: **python3 installed** (tested on: Ubuntu 20.04)



1. Create a new virtual environment for installation

```python3 -m venv pwp-environment```

2. Switch to the newly create environment

```source pwp-environment/bin/activate```

3. Install dependencies

```pip install -r requirements.txt```

4. Execute unit tests

```pytest```


### Windows 10


prerequisite: **python3 installed** (tested on: Windows 10 Home)

1. Create a new virtual environment for installation

```python -m venv pwp-environment```

2. Switch to the newly create environment

```pwp-environment\Scripts\activate.bat```

3. Install dependencies

```pip install -r requirements.txt```

4. Execute unit tests

```pytest```



## How to run the App in Docker:

### Linux

prerequisite: Docker environment available

1. Build the docker pwp package

```docker build . --tag pwp:1.0```

2. Start the container

```docker run -d --name pwp --rm -p 5000:5000 -p 3000:3000 pwp:1.0```

3. Navigate your favourite browser to http://localhost:5000/

4. Stop the container

```docker stop pwp```

5. Clean up the image from consuming storage space

```docker image rm pwp:1.0```
