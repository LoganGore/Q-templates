FROM node:alpine

WORKDIR /app

COPY package.json /app

RUN npm install
run npm build

COPY . /app

CMD npm start

EXPOSE 8050