import graphene
import resolvers

people_db = {}

class Info(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    srl = graphene.Int()


class Person(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)

class Query(graphene.ObjectType):
    info = graphene.Field(Info)
    person = graphene.Field(Person, id=graphene.Argument(graphene.ID, required=True))

    def resolve_info(self, _):
        return resolvers.info()

    def resolve_person(self, _, id):
        return Person(
            id=id,
            name=people_db[id]
        )


class AddPersonInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)


class AddPerson(graphene.Mutation):
    class Arguments:
        input = AddPersonInput(required=True)

    Output = graphene.ID

    def mutate(self, _, input):
        people_db[input.id] = input.name
        return input.id

class Mutation(graphene.ObjectType):
    add_person = AddPerson.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
