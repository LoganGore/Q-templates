const { find } = require('../db');

// --- GraphQL resolvers

const resolver = {
  Query: {
    allFoos: async (_, args, { models }) => {},
    foo: async (_, { name }, { models }) => {}
  },
  Mutation: {
    createFoo: async (_, { name }, { models }) => {},
    deleteFoo: async (_, { name }, { models }) => {}
  }
};

exports.resolver = resolver;
