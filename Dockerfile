from ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update; apt-get -y upgrade; apt-get -y autoremove

RUN apt-get install -y npm python3-pip python3

RUN mkdir /pwp

WORKDIR /pwp

COPY ./requirements.txt /pwp/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /pwp

WORKDIR /pwp/react-client

RUN npm install

RUN npm run-script build

RUN npm install -g serve

WORKDIR /pwp

ENV FLASK_APP=tapi

EXPOSE 5000
EXPOSE 3000

CMD [ "sh", "start.sh" ]


