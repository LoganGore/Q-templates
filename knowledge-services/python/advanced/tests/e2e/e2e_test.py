import os
import requests
import unittest

SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS", 'localhost')
SERVICE_PORT = os.getenv('SERVICE_PORT', '7357')
URL = 'http://{}:{}/graphql'.format(SERVICE_ADDRESS, SERVICE_PORT)


def run_query(query):
    request = requests.post(URL, json={'query': query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(
            request.status_code, query))

class TestE2E(unittest.TestCase):
    def test_service_info(self):
        query = '''{ info { id name description srl } }'''
        result = {"data": {
            "info": {
                "id": "io.maana.pytemplate",
                "name": "Maana Python Template",
                "description": "This is a python template for using MaanaQ.",
                "srl": 1
            }
        }}

        observed = run_query(query)
        assert observed == result


if __name__ == '__main__':
    unittest.main()
