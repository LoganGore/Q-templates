const { GraphQLServer } = require('graphql-yoga')
const { Prisma } = require('prisma-binding')
const faker = require('faker')

const resolvers = {
  Query: {
    info() {
      return {
          name: "Demo wrapper"
          version: "0.0.1"
      }
    }    
  },
  Mutation: {
    info() {
      return {
        name: "Demo wrapper"
        version: "0.0.1"
      }
    }
  }
}

const server = new GraphQLServer({
  typeDefs: './src/schema.graphql',
  resolvers
})

server.start(() => console.log('Server is running on http://localhost:4000'))
