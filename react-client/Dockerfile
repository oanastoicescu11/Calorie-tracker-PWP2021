FROM node:16.16.0 as builder

COPY . /react-client

WORKDIR /react-client

RUN npm install

RUN npm run-script build

FROM node:16.16.0-alpine

RUN npm install -g serve

RUN addgroup -S appgroup

RUN adduser -S appuser -G appgroup

COPY --from=builder /react-client/build /react-client

WORKDIR /react-client

USER appuser

EXPOSE 3000

CMD ["nohup", "serve", "-s", ".", "-l", "3000"]

#CMD serve -s build -l 3000

