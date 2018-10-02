import * as jwt from "express-jwt"
import * as jwksRsa from "jwks-rsa"
import { initServer } from "./server.js"

//
// Express Authentication Middleware
//
const jwtVerificationDefinition = {
  // Dynamically provide a signing key
  // based on the kid in the header and
  // the signing keys provided by the JWKS endpoint.
  secret: jwksRsa.expressJwtSecret({
    cache: true,
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri: `https://${
      process.env.REACT_APP_PORTAL_AUTH_DOMAIN
    }/.well-known/jwks.json`,
  }),

  // Validate the audience and the issuer.
  audience: process.env.REACT_APP_PORTAL_AUTH_IDENTIFIER,
  issuer: `https://${process.env.REACT_APP_PORTAL_AUTH_DOMAIN}/`,
  algorithms: ["RS256"],
}
// Middleware for validating JWT token against Auth0
const checkJwt = jwt(jwtVerificationDefinition)

//
// WebSocket Authentication Middleware
//
// This function manually adds the token to the express-jwt function,
// such that it could retrieve directly and not from a request
const jwtWithLocalToken = (token) => {
  const expandedDefinition = Object.assign({}, jwtVerificationDefinition, {
    getToken: () => {
      return token
    },
  })
  return jwt(expandedDefinition)
}

// This function uses our custom form of express-jwt to ensure the token passed to the socket is valid
const validateSocketToken = (checkTokenFunc) => {
  return new Promise((resolve, reject) => {
    // checkTokenFunc is a result of the express-jwt middleware
    // since we're not using it in the express context, req and res don't have to be passed
    checkTokenFunc({}, {}, (error) => {
      if (typeof error !== "undefined") {
        reject(`Cannot verify access token: ${error}`)
      } else {
        resolve()
      }
    })
  })
}

const socketAuthMiddleware = (connectionParams, webSocket) => {
  if (connectionParams.authToken && connectionParams.consumerName) {
    const checkTokenFunc = jwtWithLocalToken(connectionParams.authToken)
    return validateSocketToken(checkTokenFunc).then(
      () => {
        console.log(`Consumer ${connectionParams.consumerName} is connected`)
        return
      },
      (err) => {
        throw new Error(`Socket connection could not be established - ${err}`)
      },
    )
  } else {
    throw new Error(
      "Socket connection could not be established - Missing auth token!",
    )
  }
}

initServer({
  httpAuthMiddleware: checkJwt,
  socketAuthMiddleware,
})
