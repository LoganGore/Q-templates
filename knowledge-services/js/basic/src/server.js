/*===============================================================================
 copyright 2018 Maana Incorporated
 Released under the MIT License.

 Permission is hereby granted, free of charge, to any person obtaining a copy of 
 this software and associated documentation files (the "Software"), to deal in 
 the Software without restriction, including without limitation the rights to use, 
 copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
 Software, and to permit persons to whom the Software is furnished to do so, 
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all 
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
 SOFTWARE.
=============================================================================*/
require('dotenv').config()                      // load .env into process.env.*
let fs = require('fs')                          // File system access
let express = require('express')                // routing engine
let bodyParser = require('body-parser')         // middleware to assemble content from HTTP
let { ApolloServer } = require('apollo-server-express') // middleware to support GraphQL
resolvers = require('./resolvers')              // GraphQL resolvers (implementation)
const { log } = require('io.maana.shared')      // Logging for maana services

// Initialize a minimal graphql server with the provided schema and resolvers.
// The server will listen to the port specified in the .env file.  
const initServer = () => {
  // read the schema in from the specified file and create the server
  const typeDefs = fs.readFileSync('./schema.gql', { encoding: 'utf-8' })
  const server = new ApolloServer({typeDefs, resolvers})  
  const app = express()

  // display the service name if someone open's the root path of the server
  app.get('/', (req, res) => { res.send(`${process.env.SERVICE_ID}\n`) })

  // parse the body of requests as JSON
  app.use( bodyParser.json() )

  // Attach the graphql express configuration to this server
  server.applyMiddleware({app})

  // start the listener and then display the information about the host.
  app.listen({port : process.env.PORT}, () => {
      log(process.env.SERVICE_ID).info(
        `Server ready at http://localhost:${process.env.PORT}${server.graphqlPath}`)
    })
}

module.exports.initServer = initServer