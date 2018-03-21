from schema import schema
from aiohttp import web
import aiohttp_cors
import json
import sys
from resolvers import handle
from shared.maana_amqp_pubsub import amqp_pubsub, configuration
import asyncio

# import code
# code.interact(local=dict(globals(), **locals()))

async def handle_event(x):
    data_in = x.decode('utf8')
    print("Got event: " + data_in)
    result = await handle(data_in)
    data = dict()
    try:
        if result.errors:
            data['errors'] = [str(e) for e in result.errors]
        if result.data:
            data['data'] = result.data
        if result.invalid:
            data['invalid'] = result.invalid
    except:
        print("Return was malformed: " + result)
        pass
    print(json.dumps(data))
    return None

async def init(loopy):
    app = web.Application(loop=loopy)

    async def graphql(request):
        back = await request.json()
        result = await schema.execute(back.get('query', ''), return_promise=True, allow_subscriptions=True)
        data = dict()
        if result.errors:
            data['errors'] = [str(e) for e in result.errors]
        if result.data:
            data['data'] = result.data
        if result.invalid:
            data['invalid'] = result.invalid
        return web.Response(text=json.dumps(data), headers={'Content-Type': 'application/json'})

    # for /graphiql (the web interface)
    # app.router.add_put('/graphiql', graphiqlR, name='graphiql')
    # app.router.add_get('/graphiql', graphiqlR, name='graphiql')
    # app.router.add_post('/graphiql', graphiqlR, name='graphiql')

    # For /graphql
    app.router.add_post('/graphql', graphql, name='graphql')

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

    # web.run_app(app, port=7357)
    try:
        serv = await loopy.create_server(app.make_handler(), '127.0.0.1', 7357)
    except Exception as e:
        print(e)
        sys.exit(-1)
    print("=started server on 127.0.0.1:7357")
    return serv


loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.gather(
        asyncio.ensure_future(init(loop)),
        asyncio.ensure_future(amqp_pubsub.AmqpPubSub(configuration.AmqpConnectionConfig("127.0.0.1", "5672", "MPT")).subscribe("fileAdded", lambda x: handle_event(x)))
    )
)

try:
    loop.run_forever()
except KeyboardInterrupt:
    sys.exit(0)
