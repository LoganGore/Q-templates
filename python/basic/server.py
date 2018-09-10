from aiohttp import web
import aiohttp_cors
import json
import logging
import asyncio
import sys
from jinja2 import Environment
from shared.graphiql import GraphIQL
from shared.maana_amqp_pubsub import amqp_pubsub, configuration
from settings import SERVICE_ID, SERVICE_PORT, RABBITMQ_ADDR, RABBITMQ_PORT, SERVICE_ADDRESS

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

import graphql as gql
import json

from graphql_tools import build_executable_schema

source_schema = """
    schema {
      query: RootQuery
    }

    type RootQuery {
      officers: [Officer]
    }
    
    type Officer {
      title: String
      first: String
      last: String
      uniform: Uniform
    }

    type Uniform {
      pips: Float
    }
"""

resolvers = {
    'RootQuery': {
        # returning direct values, but would normally load fetch db with some info.context
        'officers': lambda value, info, **args: [
            dict(first='william', last='riker'),
            dict(first='geordi', last='laforge'),
        ]
    },
    'Officer': {
        # only declaring the field here which is computed
        'title': lambda value, info, **args: 'Officer: %(first)s %(last)s' % value,
        # and the connection
        'uniform': lambda value, info, **args: value['first'] == 'geordi' and {'i': 2.5} or {'i': 3},
    },
    'Uniform': {
        'pips': lambda value, info, **args: value['i'],
    }
}


executable_schema = build_executable_schema(source_schema, resolvers)

executed = gql.graphql(executable_schema, """
    query Example {
       officers {
         first
         last
         title
         uniform { pips }
       }
    }
""")

print(json.dumps(executed.data, indent=4))


async def handle_event(x):
    data_in = x.decode('utf8')
    logger.info("Got event: " + data_in)
    # await handle(data_in)
    return None


def init(loopy):
    asyncio.set_event_loop(loopy)
    app = web.Application(loop=loopy)

    async def graphql(request):
        back = await request.json()
        result = await  gql.graphql(executable_schema, back.get('query', ''), variable_values=back.get('variables', ''),
                                    operation_name=back.get(
            'operationName', ''),
            return_promise=True, allow_subscriptions=True)
        data = dict()
        if result.errors:
            data['errors'] = [str(err) for err in result.errors]
        if result.data:
            data['data'] = result.data
        if result.invalid:
            data['invalid'] = result.invalid
        return web.Response(text=json.dumps(data), headers={'Content-Type': 'application/json'})

    # For /graphql
    app.router.add_post('/graphql', graphql, name='graphql')
    app.router.add_get('/graphql', graphql, name='graphql')

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    # For graphIQL
    j_env = Environment(enable_async=True)
    gql_view = GraphIQL.GraphIQL(
        schema=executable_schema, jinja_env=j_env, graphiql=True)
    app.router.add_route('*', handler=gql_view,
                         path="/graphiql", name='graphiql')

    loopy.run_until_complete(
        asyncio.gather(
            asyncio.ensure_future(
                loopy.create_server(app.make_handler(),
                                    SERVICE_ADDRESS, SERVICE_PORT)
            ),
            asyncio.ensure_future(
                amqp_pubsub.AmqpPubSub(configuration.AmqpConnectionConfig(RABBITMQ_ADDR, RABBITMQ_PORT, SERVICE_ID)).
                subscribe("fileAdded", lambda x: handle_event(x))
            )
        )
    )

    try:
        logging.info("Started server on {}:{}".format(
            SERVICE_ADDRESS, SERVICE_PORT))
        loopy.run_forever()
    except Exception as e:
        loopy.close()
        logger.error(e)
        sys.exit(-1)
    return None


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        init(loop)
    except KeyboardInterrupt:
        loop.close()
        sys.exit(1)
