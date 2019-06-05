const mongoose = require('mongoose');

const schema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    index: true
  }
});

module.exports = mongoose.model('Foo', schema);
