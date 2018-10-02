require('dotenv').config()
const apollo = require('apollo-fetch')
import { AuthenticationClient } from 'auth0'

import pubsub from './pubsub'

import { KindDBSvc, log, print, convertGQLtoKinds } from 'io.maana.shared'

const SELF = process.env.SERVICE_ID || 'io.maana.template'

export default {
  Query: {
    info: async () => {
      return {
        id: 'e5614056-8aeb-4008-b0dc-4f958a9b753a',
        name: 'io.maana.template',
        description: 'Maana Q Knowledge Service template'
      }
    }
  },
  Subscription: {
    personAdded: {
      subscribe: (parent, args, ctx, info) =>
        pubsub.asyncIterator('personAdded')
    }
  }
}
