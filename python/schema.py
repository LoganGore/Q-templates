import graphene
import resolvers


class Info(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()


class Employee(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)


class Query(graphene.ObjectType):
    info = graphene.Field(Info)
    all_employees = graphene.Field(graphene.List(Employee))

    def resolve_info(self, _):
        return resolvers.info()

    async def resolve_all_employees(self, _):
        return await resolvers.all_employees()


class AddEmployeeInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String(required=True)


class AddEmployee(graphene.Mutation):

    class Arguments:
        input = AddEmployeeInput(required=True)

    Output = Employee

    async def mutate(self, _, input):
        return await resolvers.add_employee(input)


class Mutation(graphene.ObjectType):
    add_employee = AddEmployee.Field()


class FileAdded(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    mimeType = graphene.String()
    size = graphene.Int()


schema = graphene.Schema(query=Query, mutation=Mutation)
