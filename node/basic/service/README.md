# Node-based Maana Knowledge Microservice Template

## Layout

@@TODO

## Customization

* Change the name and description of the module

In `package.json`, edit the metadata:

```json
{
  "name": "sample",
  "author": "Acme, Inc.",
  "license": "MIT",
  "version": "1.0.0",
  "description": "Awesome Bot",
  "main": "src/server.js",
  "repository": "https://github.com/acme-inc/awesome-bot.git",
```

* Edit the `.env` file to reflect proper `PORT`, `SERVICE_ID`, and other service-specific parameters.
* Define your public-facing schema in a single GraphQL file in the root, e.g., `sample.gql`, which contains the common patterns:

```graphql
scalar Date

scalar JSON

type Person {
  # Kind fields
  id: ID! # internal identifier (unique)
  name: String! # external identifier (non-unique)
  # Domain-specific fields
  givenName: String
  familyName: String
  dateOfBirth: Date
}

# Create a Person instance
input AddPersonInput {
  id: ID # if known, otherwise one will be generated
  # these are all optional, but the resolver(s) must produce a 'name' value, since it is required
  name: String
  givenName: String
  familyName: String
  dateOfBirth: Date
}

# Create a Person instance
input UpdatePersonInput {
  id: ID! # required
  # only what is changing
  name: String
  givenName: String
  familyName: String
  dateOfBirth: Date
}

# Standard queries (instance and batch)
type Query {
  info: Info
  # unique people
  person(id: ID!): Person
  persons(ids: [ID!]!): [Person] # order preserved
  # specialized queries
  personsByName(name: String!): [Person]
  personsByDateOfBirth(date: Date!): [Person]
}

# Standard mutations (instance and batch)
type Mutation {
  addPerson(input: AddPersonInput): ID
  addPersons(input: [AddPersonInput!]!): [ID]
  updatePerson(input: UpdatePersonInput): ID
  updatePersons(input: [UpdatePersonInput!]!): [ID]
  deletePerson(id: ID!): Person
  deletePersons(ids: [ID!]!): [Person]
}

# Standard events
type PersonAddedEvent {
  id: ID!
  name: String!
}

type PersonUpdatedEvent {
  id: ID!
  name: String!
  # only what changed
  givenName: String
  familyName: String
  dateOfBirth: Date
}

type PersonDeletedEvent {
  id: ID!
  name: String!
  # only what was known
  givenName: String
  familyName: String
  dateOfBirth: Date
}

type Subscription {
  personAdded: PersonAddedEvent!
  personUpdated: PersonUpdatedEvent!
  personDeleted: PersonDeletedEvent!
}
```

* Define an **internal** GraphQL schema, typically the result of a **merge** and place it in the source root as `/src/schema.gql`.
* ​

## Build setup

@@TODO

## Server setup

@@TODO

## Deployment

@@TODO

## Logging

In some attempt to provide coherent and standard logging, I developed at least a funnel through which we could eventually connect proper logging. (There are several good ones, but we need to coordinate our selection with the containerization and deployment models involved.)

But instead of adding 'console.log', it is suggested to use the `io.maana.shared` utility: `log` [(source code)](/repo/ksvcs/packages/maana-shared/src/log.js), which provides a simple wrapper providing:

* a uniform log output format
  * module identity: `id`
  * time?
  * level (`info`,`warn`,`error`)
  * formatted values and indicators
* semantic argument formatters
  * module identity: `id`
  * `external` data (e.g., names)
  * `internal` data (e.g., uuids)
  * `info` data (i.e., values)
  * `true` and `false` and `bool` values
  * `json` objects
* colorization using [chalk](https://github.com/chalk/chalk)

### Setup

At the top of your `.js` file:

```javascript
import { log, print } from 'io.maana.shared'

// Module identity (whoami)
const SELF = (process.env.SERVICE_ID || 'io.maana.portal') + '.pubsub'
```

This is boilerplate for all Maana knowledge Services.

### Examples

Instead of:

```javascript
console.log('Opening RedisPubSub Connection: %s %d', REDIS_ADDR, REDIS_PORT)
```

do:

```js
log(SELF).info(`Opening RedisPubSub Connection ${REDIS_ADDR} ${REDIS_PORT}`)
```

Or, if you wish to convey more meaning in your logging:

```javascript
log(SELF).info(
  `uploading ${print.external(req.uploadFileName)} to ${print.internal(
    req.uploadDir
  )}` + (partIndex ? ` part: ${print.info(partIndex)}` : '')
)
```

# Deploying the Service

## Prerequisits

You need to have Docker installed and running on your machine.

## Log into the Azure Container Registery

    docker login --username [USER_NAME] --password [PASSWORD] [ACR_NAME].azurecr.io

## Build and tag the Docker image

    docker build --tag=[ACR_NAME].azurecr.io/[SERVICE_NAME]:[VERSION]

Make sure you assign a _unique_ name and version to your image.

## Push your image into ACR

    docker push [ACR_NAME].azurecr.io/[SERVICE_NAME]:[VERSION]

## Run an instance of your application

1. In the ACR interface in the Azure Portal, click on `Reposetories`
2. Click on the name of your image. The version tag of your image will appear.
3. Click on the elipses (...) on the right side of the version tag.
4. Click on "Run Instance"
5. Provide the required information to spin up the instance. You'll be required to provide a name, resource group and port. The port should match the one used in your Dockerfile (8050)