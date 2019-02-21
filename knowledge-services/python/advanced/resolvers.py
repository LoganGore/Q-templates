import sys
import json
import schema
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Resolvers


def info():
    return schema.Info(
        id="io.maana.pytemplate",
        name="Maana Python Template",
        description="This is a python template for using MaanaQ.",
        srl=1
    )


async def all_employees():
    employee_res = await kindDB.getAllInstancesByName(kindName="Employee")
    base = employee_res.get("allInstances")
    employees = []
    if base is not None:
        records = base.get("records")
        for r in records:
            employees.append(schema.Employee(id=r[0].get("ID"), name=r[1].get("STRING")))
    return employees


async def add_employee(employee):
    new_employee = schema.Employee(id=employee.get("id", str(uuid.uuid4())), name=employee.get("name"))
    await kindDB.addInstanceByKindName(
        "Employee",
        {
            "id": new_employee.id,
            "name": new_employee.name
        }
    )

    return new_employee


# Handlers


async def handle(event):

    parsed_event = json.loads(event)
    
    if "fileAdded" in parsed_event.keys():
        if parsed_event['fileAdded']['mimeType'] == 'text/plain':
            return await handle_file(parsed_event)


async def handle_file(blob):

    print("Got it! " + blob['fileAdded']['url'])

    return None
