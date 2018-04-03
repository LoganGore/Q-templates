## Maana Python Template

This is a template for creating a Maana Knowledge Service in Python. This requires python 3.6+

## Installation

To install the python packages required, run this:

pip install -r requirements.txt

## Starting

python server.py

# Queries to try

Adds an employee:
    curl -XPOST http://localhost:7357/graphql -H 'Content-Type: application/json' -d '{"query": "mutation M { addEmployee: addEmployee(id: \"asdf\", name: \"bob\") { name } }"}'

Gets all employees:
    curl -X POST -H "Content-Type: application/json" -d '{ "query": "{ allEmployees { name } }" }' http://localhost:7357/graphql
