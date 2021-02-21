# PWP SPRING 2021
# PROJECT NAME
# Group information
* Student 1. Oana Stoicescu oana.stoicescu@oulu.fi
* Student 2. jjuutine20@student.oulu.fi
* Student 3. Name and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## How to prepare the Python environment and execute the unit tests:

### Linux


prerequisite: **python3 installed** (tested on: Ubuntu 20.04)



1. Create a new virtual environment for installation

```python3 -m venv pwp-environment```

2. Switch to the newly create environment

```source pwp-environment/bin/activate```

3. Install dependencies

```pip install -r requirements```

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

