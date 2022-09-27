FROM python:3.10.7 as builder

WORKDIR /pwp

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip3 install virtualenv

RUN virtualenv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .

RUN pip3 install -r requirements-prod.txt

FROM python:3.10.7-alpine

COPY --from=builder /opt/venv /opt/venv

COPY tapi /pwp/tapi

COPY start.sh /pwp

WORKDIR /pwp

ENV PATH="/opt/venv/bin:$PATH"

ENV FLASK_APP=tapi

EXPOSE 5000

CMD [ "sh", "start.sh" ]


