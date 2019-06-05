# Q-ready NodeJS microservice template with support for MongoDB (incl. Azure CosmosDB)

This is a Maana Q-compatible project template supporting "modern JavaScript (ES2019)" and community best practices, including ESLint, Prettier, Docker, GraphQL, and Mongoose.

## Getting started

A _bare bones_ sample, **Foo**, has been provided that acts as a guide for where you should fill in your own schema, models, and resolvers.

- update `package.json` to reflect your information
- update `docker-compose-prod.yml` to reflect your docker image name
- modify the sample as appropriate

## Building and Running it:

- `yarn install` to get dependencies
- Use `docker-compose up` to start mongodb.
- Use `yarn dev` to start the server in Developer mode (hot reload).
- Use `yarn serve` to run the server in Production mode.

## Dependencies:

- Apollo Server
- Express
- Mongoose
- Nodemon
- Docker
- Docker-Compose
- ESLint
- Prettier

## Mongoose Schema

Under `src/db`, create one model file per file, then ensure they are included in the `index.js`.  A small sample has been provided for you to modify.

## Mongoose Helpers

A number of utility functions have been provided to simplify common access paterns.

```
// --- Helper functions

const getOrCreateInstance = async (model, origInput) => {
  // Work with a copy of the input
  const input = { ...origInput };

  // Autogen id, if not provided
  if (!input.id) {
    input.id = uniqueId(input);
  }

  // Perhaps it already exists
  let inst = await model.findOne({ id: input.id });
  if (!inst) {
    inst = new model(input);
    await inst.save();
  }
  return inst.toObject();
};

const distinct = async ({ model, selection, filter }) =>
  model.distinct(selection, filter);

// Build a list of sets based on the selection
const union = async args => {
  const { model, selection, filter } = args;
  const promises = selection.map(p =>
    distinct({ model, selection: p, filter })
  );
  const sets = await Promise.all(promises);

  // Flatten into a single list (with dupes)
  const flattened = [];
  sets.forEach(set => flattened.push(...set));

  // Unique-ify
  const unique = new Set(flattened);

  return [...unique]; // standard array
};

const find = async args => {
  const { model, filter, projection, remap } = args;
  if (!model) throw new Error(`find: missing model`);
  if (!filter) throw new Error(`find: missing filter`);

  const insts = await model.find(filter, projection);
  // console.log('>>>> ', filter, insts);
  if (!insts) return null;
  return insts.map(inst => rename(inst.toObject(), remap));
};

const findOne = async args => {
  const { model, filter, projection, remap } = args;
  let inst = await model.findOne(filter);
  if (!inst) return null;

  inst = inst.toObject();
  inst = projection ? project(inst, projection) : inst;
  inst = remap ? rename(inst, remap) : inst;
  return inst;
};

const exists = async args => {
  const res = await findOne(args);
  return !!res;
};
```

## Schema Glue

Add your factored GraphQL schema and resolvers within sub-folders of `src/graphql`.  They will be merged together for ApolloServer.

## Resolver Context

Your resolvers will receive, as part of the standard GraphQL `Context`, the following additional data:

- your Mongoose models
- the database object
- all of your other resolvers (allowing resolvers to call each other internally)

## Deployment

@@TODO

## TODO

- Authentication with CKG