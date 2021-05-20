from nikolaik/python-nodejs:python3.9-nodejs16-alpine

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


