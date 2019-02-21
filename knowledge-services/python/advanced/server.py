from schema import schema
from aiohttp import web
import aiohttp_cors
import json
import logging
import asyncio
import sys
import os
from settings import LOG_LEVEL, SERVICE_PORT, SERVICE_ADDRESS, PROJECT_ROOT

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)

# Copy and paste to drop into debugger.
# import code
# code.interact(local=dict(globals(), **locals()))

def init(loopy):
    asyncio.set_event_loop(loopy)
    app = web.Application()

    async def graphql(request):
        back = await request.json()
        result = await schema.execute(back.get('query', ''), variable_values=back.get('variables', ''),
                                      operation_name=back.get('operationName', ''),
                                      return_promise=True, allow_subscriptions=True)
        data = dict()
        if result.errors:
            data['errors'] = [str(err) for err in result.errors]
        if result.data:
            data['data'] = result.data
        if result.invalid:
            data['invalid'] = result.invalid
        return web.Response(text=json.dumps(data), headers={'Content-Type': 'application/json'})

    async def graphiql(request):
        return web.FileResponse(os.path.join(PROJECT_ROOT, "shared") + "/graphiql/graphiql.html")

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

    # For /graphql
    app.router.add_post('/graphql', graphql, name='graphql')
    app.router.add_get('/graphql', graphql, name='graphql')

    app.router.add_route('*', path='/graphiql', handler=graphiql)

    runner = web.AppRunner(app)
    loopy.run_until_complete(runner.setup())
    site = web.TCPSite(runner, SERVICE_ADDRESS, SERVICE_PORT)

    loopy.run_until_complete(
        asyncio.gather(
            asyncio.ensure_future(
                site.start()
            ),
            # For subscribing to rabbitmq
            # asyncio.ensure_future(
            #     amqp_pubsub.AmqpPubSub(configuration.AmqpConnectionConfig(RABBITMQ_ADDR, RABBITMQ_PORT, SERVICE_ID)).
            #     subscribe("fileAdded", lambda x: handle_event(x))
            # )
        )
    )

    try:
        logging.info("Started server on {}:{}".format(
            SERVICE_ADDRESS, SERVICE_PORT))
        loopy.run_forever()
    except Exception as e:
        runner.shutdown()
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
