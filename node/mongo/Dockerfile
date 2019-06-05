FROM node:alpine

WORKDIR /app

COPY package.json /app
COPY . /app

RUN yarn install
CMD yarn dev

EXPOSE 4000