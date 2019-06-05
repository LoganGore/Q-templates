// --- External imports
const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const glue = require('schemaglue');

// --- Internal imports
const { startDB, models } = require('./db');

console.log('MONGODB_HOST', process.env.MONGODB_HOST);

// --- Database setup
const db = startDB({
  user: 'graphql',
  pwd: 'yoga123',
  db: 'graphqlYoga',
  url: process.env.MONGODB_HOST || 'localhost:27017'
});

// --- Schema setup

// Glue all the schemas and resolvers together
const options = {
  js: '**/*.js' // default
  // ignore: '**/somefileyoudonotwant.js'
};
const { schema: typeDefs, resolver: resolvers } = glue('src/graphql', options);

// --- Call context: every resolver receives this
const context = {
  models, // all of the persistence models
  db, // the database itself
  resolvers // all of the other resolvers
};

// --- HTTP server
const port = 4000;
const path = '/graphql';

const app = express();

// --- GraphQL Server
const server = new ApolloServer({ typeDefs, resolvers, context });
server.applyMiddleware({ path, app });

app.listen({ port }, () => {
  console.log(
    `🦄  maana-q-function-assist-helpers @ http://localhost:${port}${
      server.graphqlPath
    }`
  );
});
