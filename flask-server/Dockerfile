FROM python

RUN mkdir /pwp

COPY requirements.txt /pwp

WORKDIR /pwp

RUN pip3 install -r requirements.txt

COPY . /pwp

ENV FLASK_APP=tapi

EXPOSE 5000

CMD [ "sh", "start.sh" ]


