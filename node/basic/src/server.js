//
// External imports
//

// load .env into process.env.*
require('dotenv').config()

// HTTP client
import fetch from 'node-fetch'
// HTTP server
import { createServer } from 'http'
// routing engine
import express from 'express'
// middleware to assemble content from HTTP
import bodyParser from 'body-parser'
// middleware to allow cross-origin requests
import cors from 'cors'
// middleware to support GraphQL
import { ApolloServer } from 'apollo-server-express'
// GraphQL core operations
import { execute } from 'graphql'
// GraphQL schema compilation
import { makeExecutableSchema } from 'graphql-tools'
// GraphQL websocket pubsub transport
import { SubscriptionServer } from 'subscriptions-transport-ws'
// GraphQL client
import { ApolloClient } from 'apollo-client'
// GraphQL networking: HTTP
import { createHttpLink } from 'apollo-link-http'
// GraphQL query caching
import { InMemoryCache } from 'apollo-cache-inmemory'
// GraphQL link context for authorization
import { setContext } from 'apollo-link-context'
// Auth0 Authentication client
import { AuthenticationClient } from 'auth0'
// Keep GraphQL stuff nicely factored
import glue from 'schemaglue'
import path from 'path'
import http from 'http'

//
// Internal imports
//
import { log, print, initMetrics, counter } from 'io.maana.shared'

const options = {
  mode: 'js' // default
  // ignore: '**/somefileyoudonotwant.js'
}
const schemaPath = path.join(
  '.',
  `${__dirname}`.replace(process.cwd(), ''),
  'graphql/'
)
const glueRes = glue(schemaPath, options)

// Compile schema
export const schema = makeExecutableSchema({
  typeDefs: glueRes.schema,
  resolvers: glueRes.resolver
})

//
// Client setup
// - allow this service to be a client of a remote service
//
let client

const clientSetup = token => {
  const authLink = setContext((_, { headers }) => {
    // return the headers to the context so httpLink can read them
    return {
      headers: {
        ...headers,
        authorization: token ? `Bearer ${token}` : ''
      }
    }
  })

  const httpLink = createHttpLink({
    uri: REMOTE_KSVC_ENDPOINT_URL,
    fetch
  })

  // Now that subsriptions are managed through RabbitMQ, WebSocket transport is no longer needed
  // as it is not production-ready and causes both lost and duplicate events.
  const link = authLink.concat(httpLink)

  client = new ApolloClient({
    link,
    cache: new InMemoryCache()
  })
}

//
// Server setup
//
// Our service identity
const SELF = process.env.SERVICE_ID || 'io.maana.template'

// HTTP port
const PORT = process.env.PORT

// HOSTNAME for subscriptions etc.
const HOSTNAME = process.env.HOSTNAME || 'localhost'

// External DNS name for service
const PUBLICNAME = process.env.PUBLICNAME || 'localhost'

// Remote (peer) services we use
const REMOTE_KSVC_ENDPOINT_URL = process.env.REMOTE_KSVC_ENDPOINT_URL

// Remote (peer) subscription endpoint we use
const REMOTE_KSVC_SUBSCRIPTION_ENDPOINT_URL =
  process.env.REMOTE_KSVC_SUBSCRIPTION_ENDPOINT_URL

const app = express()

//
// CORS
//
const corsOptions = {
  origin: `http://${PUBLICNAME}:3000`,
  credentials: true // <-- REQUIRED backend setting
}

app.use(cors(corsOptions)) // enable all CORS requests
app.options('*', cors()) // enable pre-flight for all routes

app.get('/', (req, res) => {
  res.send(`${SELF}\n`)
})

const defaultSocketMiddleware = (connectionParams, webSocket) => {
  return new Promise(function(resolve, reject) {
    log(SELF).warn(
      'Socket Authentication is disabled. This should not run in production.'
    )
    resolve()
  })
}

initMetrics(SELF)
const graphqlRequestCounter = counter('graphqlRequests', 'it counts')

const initServer = options => {
  let { httpAuthMiddleware, socketAuthMiddleware } = options

  let socketMiddleware = socketAuthMiddleware
    ? socketAuthMiddleware
    : defaultSocketMiddleware

  const server = new ApolloServer({
    schema,
    subscriptions: {
      onConnect: socketMiddleware
    }
  })

  server.applyMiddleware({
    app
  })

  const httpServer = http.createServer(app)
  server.installSubscriptionHandlers(httpServer)

  httpServer.listen({ port: PORT }, () => {
    log(SELF).info(
      `listening on ${print.external(`http://${HOSTNAME}:${PORT}`)}`
    )

    let auth0 = new AuthenticationClient({
      domain: process.env.REACT_APP_PORTAL_AUTH_DOMAIN,
      clientId: process.env.REACT_APP_PORTAL_AUTH_CLIENT_ID,
      clientSecret: process.env.REACT_APP_PORTAL_AUTH_CLIENT_SECRET
    })

    auth0.clientCredentialsGrant(
      {
        audience: process.env.REACT_APP_PORTAL_AUTH_IDENTIFIER,
        scope: 'read:client_grants'
      },
      function(err, response) {
        if (err) {
          console.error('Client was unable to connect', err)
        }

        clientSetup(response.access_token)
      }
    )
  })
}

export default initServer
