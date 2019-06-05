const mongoose = require('mongoose');
const util = require('util');

// ---
const { uniqueId, project, rename } = require('../util');

// --- Schema

const Foo = require('./Foo');

const models = {
  Foo
};

// --- Mongoose client

// Setup Mongoose Promises.
mongoose.Promise = global.Promise;

const startDB = args => {
  const { user, pwd, url, db } = args;
  mongoose.connect(
    `mongodb://${user}:${pwd}@${url}/${db}`,
    {
      useNewUrlParser: true
    },
    error => {
      if (error) {
        console.log('MongoDB error', error);
        setTimeout(() => startDB(args), 3000);
      }
    }
  );
};

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

module.exports = {
  distinct,
  exists,
  find,
  findOne,
  getOrCreateInstance,
  models,
  startDB,
  union
};
