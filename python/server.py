from schema import schema
from aiohttp import web
import aiohttp_cors
import json
import logging
import asyncio
import sys
from jinja2 import Environment
from shared.graphiql import GraphIQL
from resolvers import handle
from shared.maana_amqp_pubsub import amqp_pubsub, configuration

# DEFINE SERVER AND PORT:
SERV_ADDRESS = '127.0.0.1'
PORT = 7357
SERVICE_NAME = "io.maana.MPT"

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


async def handle_event(x):
    data_in = x.decode('utf8')
    logger.info("Got event: " + data_in)
    await handle(data_in)
    return None

  
async def init(loopy):
    app = web.Application(loop=loopy)

    async def graphql(request):
        back = await request.json()
        result = await schema.execute(back.get('query', ''), variable_values=back.get('variables', ''),
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
    gql_view = GraphIQL.GraphIQL(schema=schema, jinja_env=j_env, graphiql=True)
    app.router.add_route('*', handler=gql_view, path="/graphiql", name='graphiql')

    try:
        serv = await loopy.create_server(app.make_handler(), SERV_ADDRESS, PORT)
    except Exception as e:
        logger.error(e)
        sys.exit(-1)

    logging.info("Started server on {}:{}".format(SERV_ADDRESS, PORT))
    return serv


loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.gather(
        asyncio.ensure_future(init(loop)),
        asyncio.ensure_future(amqp_pubsub.AmqpPubSub(configuration.AmqpConnectionConfig("127.0.0.1", "5672", "MPT")).
                              subscribe("linkAdded", lambda x: handle_event(x)))
    )
)
try:
    loop.run_forever()
except KeyboardInterrupt:
    sys.exit(0)
