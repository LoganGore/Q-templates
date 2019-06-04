from aiohttp import web
from aiohttp.abc import AbstractAccessLogger

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

from collections import deque
import traceback
import hashlib

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

    # For our query list
    running_queries = []
    complete_queries = deque(maxlen=10)

    # We need to know a query not only completed, but it also sent successfully (i.e no hang)
    class AccessLogger(AbstractAccessLogger):

        def log(self, request, response, time):

            for query_information in running_queries:
                if query_information['request'] is request:
                    query_information['response_code'] = response.status
                    query_information['complete'] = True
                    #It's complete so we move it onward
                    complete_queries.append(query_information)
                    #This is O(n) which isn't great, but how many concurrent queries are we going to be handling?
                    running_queries.remove(query_information)
                    break

            #We might still want this debug info! So pass it through to the normal handler
            #It doesn't match exactly the standard - I took it from the aiohttp page
            self.logger.info(f'{request.remote} {request.method} {request.path} done in {time}s: {response.status}')

    app = web.Application(client_max_size=52428800, handler_args={"keepalive_timeout":1200, 'access_log_class' : AccessLogger})

    async def graphql(request):
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

        #A new query/process - ID is just a hash of the timer. Unique enough hopefully.
        query_information = {
            "id" : hashlib.md5(str(timer()).encode('utf-8')).hexdigest(),
            "complete" : False,
            "query" : query,
            "variables" : variables,
            "request" : request
        }

        #Time our query and add it to our queryList       
        query_information['start'] = timer()
        running_queries.append(query_information)
        result = await gql.graphql(executable_schema, query, variable_values=variables, operation_name=operation_name, context_value=context_vars)       
        query_information['end'] = timer()

        # to store our response in
        data = {}

        # handle any errors
        if result.errors:
            for err in result.errors:
                print(traceback.format_exc())
                logger.error("Error: " + str(err))
                continue
            data['errors'] = [str(err) for err in result.errors]
        
        if result.data:
            data['data'] = result.data

        query_information['data'] = False
        query_information['errors'] = False
        query_information['invalid'] = False

        if 'errors' in data:
            query_information['errors'] = data['errors']
        if 'invalid' in data:
            query_information['invalid'] = data['invalid']
        if 'data' in data:
            query_information['data'] = data['data']

        return web.Response(text=json.dumps(data), headers={'Content-Type': 'application/json'})

    async def graphiql(request):
        return web.FileResponse(os.path.join(PROJECT_ROOT, "shared") + "/graphiql/graphiql.html")

    async def queryList(request):
        result = []
        now = timer()

        #We are using the same handler for the list and for the information
        try:
            id = request.match_info['id']
        except:
            id = False

        #This generates a list of running queries and up to 10 of the old queries
        #We reverse them add them together, running at the top
        for query in (running_queries[::-1] + list(complete_queries)[::-1]):

            info = {}

            #If there is an id, this is a request for more information, not the entire list
            if id and not query['id'] == id:
                continue

            #Which paremeters do we want
            all_vars = ['complete', 'response_code', 'invalid', 'errors']

            if id:
                all_vars += ['variables', 'data']
                info['query'] = query['query']
            else:
                info["full_information"] = f"http://{request.host}/queryInformation/{query['id']}"
                info['query'] = (query['query'][:250] + '(...)') if len(query['query']) > 255 else query['query']

            if 'end' in query:
                info['query_time'] = round(query['end'] - query['start'],3)
            else:               
                info['query_time_so_far'] = round(now - query['start'], 3)            
           
            #Copy everything else across
            for var_name in all_vars:
                if var_name in query:
                    info[var_name] = query[var_name]

            
            result.append(info)

        return web.Response(text=json.dumps(result), headers={'Content-Type': 'application/json'})

    async def clearCache(request):
        graphql_tools.empty_cache()
        graphql_tools.empty_cache(persistent=True)
        return web.Response(text='{"result": "success"}', headers={'Content-Type': 'application/json'})

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

    # Add our routes to CORS
    for route in list(app.router.routes()):
        cors.add(route)

    app.router.add_route('*', path='/clearTemporaryCache', handler=clearTemporaryCache)
    app.router.add_route('*', path='/clearPersistentCache', handler=clearPersistentCache)
    app.router.add_route('*', path='/clearCache', handler=clearCache)
    app.router.add_route('*', path='/queryList', handler=queryList)
    app.router.add_route('*', path='/queryInformation/{id}', handler=queryList)
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
        loop.close()
        sys.exit(1)

