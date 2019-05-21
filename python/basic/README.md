

# Maana Python 3.7 Template

This template is designed to make quick work of creating new [GraphQL](http://graphql.org) microservices for use inside [Maana Q](https://www.maana.io/knowledge-platform/). It was created by Alexander Elkholy, Almir Alemic, Ashish Juneja and Andrew Spode, members of Maana's Customer Solutions team. 

## Getting Started

To use this template, you will need [docker-compose](https://docs.docker.com/compose/install/) installed and **running**. You **do not** need Python or any of its package requirements installed. Everything is run inside the docker container - both during production and development.

Clone this repository to your machine and from a Linux/Mac terminal, navigate to the folder and run:

> ./build_and_deploy.sh

If you are using Windows, instead run:

> ./build_and_deploy.bat

Docker will then automatically download all requirements to build the container, eventually leaving you with the helloWorld service running on port 8001. It may take a while on the first build, but subsequent builds are faster and only services that change require rebuilding.

[GraphiQL](https://github.com/graphql/graphiql), a web based application for simple testing of your services, is built in to every service. Test your service is running by visiting [http://localhost:8001/graphiql](http://localhost:8001/graphiql)

Try the following query:

```
{
  helloWorld(name:"World")
}
```

Press the big play button, and you should be greeted with a familiar "Hello World!" response.

The GraphQL endpoint is on [http://localhost:8001/graphql](http://localhost:8001/graphql) (note the missing "i"). To integrate this into Q while developing, you will need a tool such as [ngrok](https://ngrok.com/) to expose a **publicly accessible URL**.

## Building Your Own Services

This template has been designed for creating multiple services at the same time, quickly. This encourages you to break your services down into as many smaller services as possible for, amongst other reasons, reusability. 

Inside the **/services** folder you will see our **hello_world** folder. This contains all the code pertaining to that service. To add our second service, we will duplicate this folder and we'll call it **hello_again**.

Next, we need to edit **docker_compose.yml** (found on the root) to add a **new entry** for our service. If you duplicate our hello_world entry, you will only need to update the names and the port, like this:

```
version: "3"
services:
  python-base:
    build:
      context: service_base/
      dockerfile: Dockerfile
    image: base-python-micro:latest
  hello_world:
    build: services/hello_world/
    volumes:
      - ./services/hello_world/:/service_source
      - ./service_base/:/service_base_source  
    ports:
      - "8001:8050"
    depends_on:
      - "python-base"
```
*Becomes...*

<pre><code>version: "3"
services:
  python-base:
    build:
      context: service_base/
      dockerfile: Dockerfile
    image: base-python-micro:latest
  hello_world:
    build: services/hello_world/
    volumes:
      - ./services/hello_world/:/service_source
      - ./service_base/:/service_base_source  
    ports:
      - "8001:8050"
    depends_on:
      - "python-base"
  <b>hello_again:
    build: services/hello_again/
    volumes:
      - ./services/hello_again/:/service_source
      - ./service_base/:/service_base_source  
    ports:
      - "8002:8050"
    depends_on:
      - "python-base"</b>
</code></pre>

All of the services internally run on port 8050, so to change the port of a service you only need to edit this one file - not the service itself. Don't worry if you don't understand what it's doing - as long as you have changed the relevant **names** and **port**.

*(Those familiar with with Docker may be wondering why we are mounting these volumes. These are used by the services built in *watch mode* and are not necessary if running in production.)*

## Schema

There are four key [GraphQL Schema](https://graphql.org/learn/schema/) files that our services will use, stored either in the Service Base (**/service_base/schema**) for shared use, or inside each services own schema folder (eg. **/services/hello_world/schema**)

### Service Schema

**query.gql** and **mutation.gql** are evidently used for defining the queries and mutations that your service exposes. 

In our hello world example, if we wanted to add a new function for generating a Person:

```
type Query {
    info: String
    helloWorld (name: String): String
}
```

*Becomes...*

<pre><code>type Query {
    info: String
    helloWorld (name: String): String
    <b>createPerson (firstName: String, lastName: String): Person</b>
}</code></pre>

### Service Base Schema

These files are stored in **/service_base/schema** and will be used by all services.

**model.gql** is where we will define our types, inputs and scalars etc. that **all** of the services use. When each service is built, it will **automatically remove** anything that is not used on a per-service basis, so you don't need to worry about your model becoming too big. 

As we are using a new type (Person) we would need to add this to our model.gql.

```
schema {
  query: Query
  mutation: Mutation
}
```

*Becomes...*

<pre><code>schema {
  query: Query
  mutation: Mutation
}

<b>type Person {
  firstName: String
  lastName: String
  fullName: String
}</b></code></pre>

Now any of our services will all have access to this new type, Person.

**portal.gql** won't be used by everyone. If you have made a domain model in Q, and want to use it inside your services and you have chosen **not to store your data on Q**, go to the admin panel in Q and find your workspace. Click "Test" and you will get a full schema for your domain model. Paste the contents in to this file and the template will **convert it automatically** to the right format. 

## Resolvers

Now we have a function defined in our schema, we have to write the Python code to *resolve* this function. This is done in **resolvers.py** inside our service. Let's add our new function in.

```
resolvers = {
    'Query': {
        'info': lambda value, info, **args: "Hello World example.",
        'helloWorld': helloWorld
    },
    'Mutation': {
        'info': lambda value, info, **args: "Hello World example."
    }    
}
```

*Becomes...*

<pre><code>resolvers = {
    'Query': {
        'info': lambda value, info, **args: "Hello World example.",
        'helloWorld': helloWorld<b>,
        'createPerson': createPerson</b>
    },
    'Mutation': {
        'info': lambda value, info, **args: "Hello World example."
    }    
}</code></pre>

Now we can define our function in a normal Python manner. We put this function **above** our resolvers variable, or we will get an error. 

```
def createPerson(value, info, **args):
  fullName = f"{args['firstName']} {args['lastName']}"

  return {
    "firstName": args['firstName'], 
    "lastName": args['lastName'],
    "fullName": fullName
  }
```
Notice how all of our query parameters are inside the "args" dictionary. We do whatever processing we want to do and finally, the return value is a dictionary in the shape of the type defined in our query - in this case *Person*.

**To test our new service, terminate the current terminal script (ctrl + c) and re-run the build_and_deploy script.** Your new service will be on port 8002.

## Pip Packages

To add new packages, as you would using pip, simply add a new entry to **requirements.txt**, found in the service_base folder. They will be automatically downloaded and added during the build process for all services.

## Watch Mode

Each service has a built in watch mode. This means, when you change your code, the service will **automatically restart** with the new code changes in place, for quick development. *However, should you adjust requirements.txt, or add new services (as above), you will need to terminate (ctrl + c) the running terminal script and re-run the build_and_deploy script.*

Although this has been tested on Mac and Linux, it is currently not believed to be working on Windows.

## Caching

The template has a built in caching mechanism that is particularly useful for computationally expensive queries. This is done in the form of a decorator.

```
def dummyFunction(value, info, **args):
  pass  
```

*Becomes...*

<pre><code><b>@cache_query()</b>
def dummyFunction(value, info, **args):
  pass  
</code></pre>

Caching is based off the name of the resolver, plus the **parameters provided**. In our example above, it would be cached on a per Person basis, as the parameters would be different. Be careful when caching queries that use dynamic data, such as the current time, or random numbers etc. 

Cache is stored inside the docker container, currently **on disk**. Using this for computationally light functions may in fact be slower due to the overhead of calculating cache keys and disk reads.

The cache_query decorator takes two optional parameters:

### ttl 

> @cache_query(ttl=3600)

This is the time in seconds that the cache is valid for, with a default of **3600** (1 hour)

### persistent

> @cache_query(persistent=True)

When persistent is switched on, the cache is no longer stored inside the docker container, but **on the host** itself. It also **ignores the ttl** parameter. This is mostly useful when developing and you have complex functions that you would like to persist even after you restart the container. 

### Wiping Cache

Each time the container is restarted, or the watch mode restarts the application, the temporary cache is **wiped automatically**. Persistent cache is never wiped automatically. If you would like to wipe either of the caches, two endpoints are exposed to do so.

[http://localhost:8001/clearTemporaryCache](http://localhost:8001/clearTemporaryCache)

[http://localhost:8001/clearPersistentCache](http://localhost:8001/clearPersistentCache)

## Debugging

Each service has a basic debug endpoint, where you can see the last query, how long it took and the payload. You can copy and paste the query/variables directly into GraphiQL for testing queries that might have failed. You will find the [JSON Formatter](https://chrome.google.com/webstore/detail/json-formatter/bcjindcccaagfpapjjmafapmmgkkhgoa/related?hl=en) extension for Google Chrome very useful in making this more human readable. 

[http://localhost:8001/debug](http://localhost:8001/debug)

## Azure Kubernetes Service Deployment Steps

Docker compose will create docker images for each of your services that can be deployed independently of each other, ideal for deployment on Kubernetes or other container management systems.

### Prerequisites

1. Install Azure's AKS CLI
   `az aks install-cli`
2. Get credentials for the AKS cluster
   `az aks get-credentials --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME>`
3. Open the Kubernetes dashboard
   `az aks browse --resource-group <RESOURCE_GROUP> --name <AKS_CLUSTER_NAME>`
4. List deployed assets (Pods, deployments)
   `kubectl get all`

### Kubernetes Deployment

1. Create a name space in Kubernetes
   `kubectl create ns <NAMESPACE_FOR_YOUR_SERVICE>`
2. Apply docker-compose.yml file to the namespace
   kubectl apply -n <NAMESPACE_FOR_YOUR_SERVICE> -f <PATH_TO_DOCKER_COMPOSE>

### Expose your application

`kubectl expose deployment <DEPLOYMENT> --type=LoadBalancer --name=<NAME_FOR_EXPOSED_SERVICE> --namespace=<NAMESPACE_FOR_YOUR_SERVICE>`
