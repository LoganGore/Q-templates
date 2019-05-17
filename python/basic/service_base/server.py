import os
from aiohttp import web
import aiohttp_cors
import json
import logging
import asyncio
import sys
import graphql as gql
import json
import traceback
import graphql_tools
from resolvers import resolvers
from scalars import scalars
from graphql.execution.executors.asyncio import AsyncioExecutor
import graphql
from graphqlclient import GraphQLClient
from graphql_tools import build_executable_schema
from graphql_tools import empty_cache

from shared.graphiql import GraphIQL
from CKGClient import CKGClient
from settings import SERVICE_ADDRESS, SERVICE_PORT, PROJECT_ROOT, LOG_LEVEL
from context import context_vars
import sys
from timeit import default_timer as timer

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)

# load and process our portal schema
# TODO: Change portal_to_model to accept string, not a file
try:
    source_schema = graphql_tools.portal_to_model("schema/portal.gql")
except:
    source_schema = ""

with open("schema/model.gql", "r") as f:
    model_schema = f.read()
   
    try:
        # Anything in the model overrides anything in portal
        source_schema = graphql_tools.schema_prioritise(source_schema, model_schema)
    except:
        source_schema = source_schema + "\n" + model_schema

# Open our schema one by one and override anything we find in the portal
with open("schema/mutation.gql", "r") as f:
    mutation_schema = f.read()
    source_schema = source_schema + "\n" + mutation_schema

with open("schema/query.gql", "r") as f:
    query_schema = f.read()
    source_schema = source_schema + "\n" + query_schema

# Remove any unused types from our schema so our service is nice and trim
ast = graphql.parse(source_schema)
schema = graphql.build_ast_schema(ast)
filtered_set = graphql_tools.get_all_types_from_query_and_mutation(schema)
trimmed = graphql_tools.filter_schema(schema, filtered_set)

executable_schema = build_executable_schema(trimmed, resolvers, scalars)

async def handle_event(x):
    data_in = x.decode('utf8')
    logger.info("Got event: " + data_in)
    # await handle(data_in)
    return None

def init(loopy):
    asyncio.set_event_loop(loopy)
    app = web.Application(client_max_size=52428800)
    graphql_executor = AsyncioExecutor(loop=loopy)

    # store information here for our /debug endpoint
    last_request = {}

    async def graphql(request):
        query_start = timer()
        back = await request.json()
        variables = back.get('variables', '')
        if not variables:
            variables = {}

        result = await gql.graphql(executable_schema, back.get('query', ''), variable_values=variables, operation_name=back.get('operationName', ''), context_value=context_vars)
        # to store our response in
        data = {}

        # handle any errors
        if result.errors:
            for err in result.errors:
                #tb = traceback.format_exc()
                logger.error("error " + str(err))
                continue
            data['errors'] = [str(err) for err in result.errors]
        if result.data:
            data['data'] = result.data

        query_end = timer()

        # store our debug information
        last_request['query_time'] = query_end - query_start
        last_request['request'] = {
            "query": back.get('query', ''),
            "variables": back.get('variables', '')
        }
        last_request['data'] = False
        last_request['errors'] = False
        last_request['invalid'] = False

        if 'errors' in data:
            last_request['errors'] = data['errors']
        if 'invalid' in data:
            last_request['invalid'] = data['invalid']
        if 'data' in data:
            last_request['data'] = data['data']

        return web.Response(text=json.dumps(data), headers={'Content-Type': 'application/json'})

    async def graphiql(request):
        return web.FileResponse(os.path.join(PROJECT_ROOT, "shared") + "/graphiql/graphiql.html")

    async def debug(request):
        return web.Response(text=json.dumps(last_request), headers={'Content-Type': 'application/json'})

    async def clearTemporaryCache(request):
        empty_cache()
        return web.Response(text='{"result": "success"}', headers={'Content-Type': 'application/json'})

    async def clearPersistentCache(request):
        empty_cache(persistent=True)
        return web.Response(text='{"result": "success"}', headers={'Content-Type': 'application/json'})

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

    # used for fetching things like the last queries
    app.router.add_post('/debug', debug, name='debug')
    app.router.add_get('/debug', debug, name='debug')

    # Delete cache
    app.router.add_post('/clearTemporaryCache',
                        clearTemporaryCache, name='clearTemporaryCache')
    app.router.add_get('/clearTemporaryCache',
                       clearTemporaryCache, name='clearTemporaryCache')

    # Delete persistent cache
    app.router.add_post('/clearPersistentCache',
                        clearPersistentCache, name='clearPersistentCache')
    app.router.add_get('/clearPersistentCache',
                       clearPersistentCache, name='clearPersistentCache')

    app.router.add_route('*', path='/graphiql', handler=graphiql)

    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except:
            continue

    runner = web.AppRunner(app)
    loopy.run_until_complete(runner.setup())
    site = web.TCPSite(runner, SERVICE_ADDRESS, SERVICE_PORT)

    loopy.run_until_complete(
        asyncio.gather(
            asyncio.ensure_future(
                site.start()
            )
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
