FROM node

COPY . /react-client

WORKDIR /react-client

RUN npm install

RUN npm run-script build

RUN npm install -g serve

EXPOSE 3000

CMD serve -s build -l 3000

