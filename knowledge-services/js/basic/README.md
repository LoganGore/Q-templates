# Basic Maana Service Template
This service template can be used to create a Maana logic service in Node-js.  This template is minimal -- it contains no authentication, no subscription service, etc.   It is intended as a starting point for the construction of logic services.   For more sophisticated projects, users are directed to start from the "advanced template"

## Creating a new Maana service
After you have forked this repository, you will need to customize three files:

* .env - Change the "Identity" environment variables to accurately describe your service.
* schema.gql - Extend the schema to include your custom types, queries and mutations.
* resolvers.js - Add the custom resolvers for your custom types, queries and mutations.

### Building your service
You can build your service by running the following command.

```
npm i
```

### Running your service locally
You can stand up your service running locally using the following command:
```
npm start
```

The service will be hosted on localhost at the port specified in the .env file.   You can test your service by navigating to localhost:<YOURPORT>/graphql in your web browser.   It should display a graphQL playground page where you can evaluate graphql operations against your schema.    For more information about graphql plaground, check out this web page:

https://www.apollographql.com/docs/apollo-server/features/graphql-playground.html

### Containerize your service
You can containerize your service for cloud deployment by running the following command:
```
npm run dockerize
```

This will build the service inside a docker container and tag the image with your service's name.

### Running your service in a docker container
You can stand up your service's docker container using the following command:
```
source .env; docker run -p $PORT:$SERVICE_PORT -ti $SERVICE_ID:latest
```

The service will be hosted on localhost at the port specified in the .env file.   You can test your service by navigating to localhost:<YOURPORT>/graphql in your web browser.   It should display a graphQL playground page where you can evaluate graphql operations against your schema.    For more information about graphql plaground, check out this web page:

https://www.apollographql.com/docs/apollo-server/features/graphql-playground.html


