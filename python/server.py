from schema import schema
from aiohttp import web
import aiohttp_cors
import json
from pubsub import pubsub
import asyncio


def handle_event(x):
    data_in = x.decode('utf8')
    print("Got event: " + data_in)
    result = schema.execute(json.loads(data_in), return_promise=False)
    data = dict()
    if result.errors:
        data['errors'] = [str(e) for e in result.errors]
    if result.data:
        data['data'] = result.data
    print(json.dumps(data))
    return None

async def main():
    app = web.Application()

    async def graphql(request):
        back = await request.json()
        result = await schema.execute(back.get('query', ''), return_promise=True)
        data = dict()
        if result.errors:
            data['errors'] = [str(e) for e in result.errors]
        if result.data:
            data['data'] = result.data
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

    return web.run_app(app, port=7357)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([
        asyncio.ensure_future(pubsub.subscribe("fileAdded", lambda x: handle_event(x))),
        main()
    ]))
    loop.close()
