from aiohttp import web
import aiohttp_cors
import asyncio
import os
import json
import logging
import sys
import graphql as gql
import graphql_tools
from timeit import default_timer as timer

from settings import SERVICE_ADDRESS, SERVICE_PORT, PROJECT_ROOT, LOG_LEVEL
from context import context_vars
from resolvers import resolvers
from scalars import scalars

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
ast = gql.parse(source_schema)
schema = gql.build_ast_schema(ast)
filtered_set = graphql_tools.get_all_types_from_query_and_mutation(schema)
trimmed = graphql_tools.filter_schema(schema, filtered_set)
executable_schema = graphql_tools.build_executable_schema(trimmed, resolvers, scalars)

async def init():
    app = web.Application(client_max_size=52428800)

    # store information here for our /debug endpoint
    last_request = {}

    async def graphql(request):
        query_start = timer()

        #If there is no request, it gives a 500
        try:
            back = await request.json()
        except:
            return web.Response(text="Did you want <a href=/graphiql>GraphiQL</a>?", headers={'Content-Type': 'text/html'})

        variables = back.get('variables', '')
        query = back.get('query', '')
        operation_name = back.get('operationName', '')

        #usually no variables, which causes it to fail
        if not variables:
            variables = {}

        result = await gql.graphql(executable_schema, query, variable_values=variables, operation_name=operation_name, context_value=context_vars)

        # to store our response in
        data = {}

        # handle any errors
        if result.errors:
            for err in result.errors:
                logger.error("Error: " + str(err))
                continue
            data['errors'] = [str(err) for err in result.errors]
        
        if result.data:
            data['data'] = result.data

        query_end = timer()

        # store our debug information
        last_request['query_time'] = query_end - query_start
        last_request['request'] = {
            "query": query,
            "variables": variables
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
        graphql_tools.empty_cache()
        return web.Response(text='{"result": "success"}', headers={'Content-Type': 'application/json'})

    async def clearPersistentCache(request):
        graphql_tools.empty_cache(persistent=True)
        return web.Response(text='{"result": "success"}', headers={'Content-Type': 'application/json'})

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    #Add our routes to CORS - I'm not sure why this is done beforehand?
    #TODO: Check this is working, and/or not included in the aiohttp as standard now
    for route in list(app.router.routes()):
        cors.add(route)

    app.router.add_route('*', path='/clearTemporaryCache', handler=clearTemporaryCache)
    app.router.add_route('*', path='/clearPersistentCache', handler=clearPersistentCache)
    app.router.add_route('*', path='/debug', handler=debug)
    app.router.add_route('*', path='/graphql', handler=graphql)
    app.router.add_route('*', path='/graphiql', handler=graphiql)

    #Start the site
    try:
        runner = web.AppRunner(app)   
        await runner.setup()

        site = web.TCPSite(runner, SERVICE_ADDRESS, SERVICE_PORT)
        await site.start()

        logging.info(f"Started server on {SERVICE_PORT}")
    #Fails to launch
    except Exception as e:
        runner.cleanup()
        logger.error(e)
        sys.exit(-1)

    #so we can terminate cleanly in main
    return runner, site

if __name__ == "__main__":    
    loop = asyncio.get_event_loop()
    runner, site = loop.run_until_complete(init())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(runner.cleanup())
        sys.exit(1)

