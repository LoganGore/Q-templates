//
// External imports
//

// load .env into process.env.*
require("dotenv").config()

// File system access
import fs from "nano-fs"

// HTTP server
import { createServer } from "http"

// routing engine
import * as express from "express"

// middleware to assemble content from HTTP
import * as bodyParser from "body-parser"

// middleware to allow cross-origin requests
import * as cors from "cors"

// middleware to support GraphQL
import { graphiqlExpress, graphqlExpress } from "apollo-server-express"

// GraphQL core operations
import { execute, subscribe } from "graphql"

// GraphQL schema compilation
import { makeExecutableSchema } from "graphql-tools"

// GraphQL websocket pubsub transport
import { SubscriptionServer } from "subscriptions-transport-ws"

// Auth0 Authentication client
import { AuthenticationClient } from "auth0"

//
// Internal imports
//
import { counter, initMetrics, log, print, BuildGraphqlClient } from "io.maana.shared"

// GraphQL resolvers (implementation)
import resolvers from "./resolvers"

// GraphQL schema (model)
const typeDefs = fs.readFileSync("src/schema.gql", { encoding: "utf-8" })

// Compile schema
export const schema = makeExecutableSchema({
  typeDefs,
  resolvers,
})

//
// Client setup
// - allow this service to be a client of a remote service
//
let client
const clientSetup = (token) => {
  if (!client) {
    // construct graphql client using endpoint and context
    client = BuildGraphqlClient(REMOTE_KSVC_ENDPOINT_URL, (_, { headers }) => {
      // return the headers to the context so httpLink can read them
      return {
        headers: {
          ...headers,
          authorization: token ? `Bearer ${token}` : ''
        }
      }
    })
  }
}


//
// Server setup
//
// Our service identity
const SELF = process.env.SERVICE_ID || "io.maana.template"

// HTTP port
const PORT = process.env.PORT

// HOSTNAME for subscriptions etc.
const HOSTNAME = process.env.HOSTNAME || "localhost"

// External DNS name for service
const PUBLICNAME = process.env.PUBLICNAME || "localhost"

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
  credentials: true, // <-- REQUIRED backend setting
}

app.use(cors(corsOptions)) // enable all CORS requests
app.options("*", cors()) // enable pre-flight for all routes

app.get("/", (req, res) => {
  res.send(`${SELF}\n`)
})

const defaultHttpMiddleware = [
  graphqlExpress({
    schema,
  }),
]

const defaultSocketMiddleware = (connectionParams, webSocket) => {
  return new Promise(function(resolve, reject) {
    log(SELF).warn(
      "Socket Authentication is disabled. This should not run in production.",
    )
    resolve()
  })
}

initMetrics(SELF.replace('-','.'))
const graphqlRequestCounter = counter("graphqlRequests", "it counts")

const initServer = (options) => {
  const { httpAuthMiddleware, socketAuthMiddleware } = options
  const httpMiddleware = httpAuthMiddleware
    ? [httpAuthMiddleware, ...defaultHttpMiddleware]
    : defaultHttpMiddleware
  const socketMiddleware = socketAuthMiddleware
    ? socketAuthMiddleware
    : defaultSocketMiddleware

  app.use(
    "/graphql",
    (req, res, next) => {
      graphqlRequestCounter.inc()
      next()
    },
    bodyParser.json(),
    httpMiddleware,
  )

  app.use(
    "/graphiql",
    graphiqlExpress({
      endpointURL: "/graphql",
      subscriptionsEndpoint: `ws://${HOSTNAME}:${PORT}/subscriptions`,
    }),
  )

  const server = createServer(app)

  server.listen(PORT, () => {
    log(SELF).info(
      `listening on ${print.external(`http://${HOSTNAME}:${PORT}`)}`,
    )

    const auth0 = new AuthenticationClient({
      domain: process.env.REACT_APP_PORTAL_AUTH_DOMAIN,
      clientId: process.env.REACT_APP_PORTAL_AUTH_CLIENT_ID,
      clientSecret: process.env.REACT_APP_PORTAL_AUTH_CLIENT_SECRET,
    })

    auth0.clientCredentialsGrant(
      {
        audience: process.env.REACT_APP_PORTAL_AUTH_IDENTIFIER,
        scope: "read:client_grants",
      },
      function(err, response) {
        if (err) {
          console.error("Client was unable to connect", err)
        }

        clientSetup(response.access_token)
      },
    )
  })

  const subscriptionServer = new SubscriptionServer(
    {
      execute,
      subscribe,
      schema,
      onConnect: socketMiddleware,
      keepAlive: 3000,
    },
    {
      server,
      path: "/subscriptions",
    },
  )
}

export default initServer
