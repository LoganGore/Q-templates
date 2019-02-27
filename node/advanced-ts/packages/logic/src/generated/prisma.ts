import { GraphQLResolveInfo, GraphQLSchema } from 'graphql'
import { IResolvers } from 'graphql-tools/dist/Interfaces'
import { Options } from 'graphql-binding'
import { makePrismaBindingClass, BasePrismaOptions } from 'prisma-binding'

export interface Query {
    grocers: <T = Array<Grocer | null>>(args: { where?: GrocerWhereInput | null, orderBy?: GrocerOrderByInput | null, skip?: Int | null, after?: String | null, before?: String | null, first?: Int | null, last?: Int | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    helloes: <T = Array<Hello | null>>(args: { where?: HelloWhereInput | null, orderBy?: HelloOrderByInput | null, skip?: Int | null, after?: String | null, before?: String | null, first?: Int | null, last?: Int | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    grocer: <T = Grocer | null>(args: { where: GrocerWhereUniqueInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T | null> ,
    grocersConnection: <T = GrocerConnection>(args: { where?: GrocerWhereInput | null, orderBy?: GrocerOrderByInput | null, skip?: Int | null, after?: String | null, before?: String | null, first?: Int | null, last?: Int | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    helloesConnection: <T = HelloConnection>(args: { where?: HelloWhereInput | null, orderBy?: HelloOrderByInput | null, skip?: Int | null, after?: String | null, before?: String | null, first?: Int | null, last?: Int | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    node: <T = Node | null>(args: { id: ID_Output }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T | null> 
  }

export interface Mutation {
    createGrocer: <T = Grocer>(args: { data: GrocerCreateInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    createHello: <T = Hello>(args: { data: HelloCreateInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    updateGrocer: <T = Grocer | null>(args: { data: GrocerUpdateInput, where: GrocerWhereUniqueInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T | null> ,
    deleteGrocer: <T = Grocer | null>(args: { where: GrocerWhereUniqueInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T | null> ,
    upsertGrocer: <T = Grocer>(args: { where: GrocerWhereUniqueInput, create: GrocerCreateInput, update: GrocerUpdateInput }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    updateManyGrocers: <T = BatchPayload>(args: { data: GrocerUpdateInput, where?: GrocerWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    updateManyHelloes: <T = BatchPayload>(args: { data: HelloUpdateInput, where?: HelloWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    deleteManyGrocers: <T = BatchPayload>(args: { where?: GrocerWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> ,
    deleteManyHelloes: <T = BatchPayload>(args: { where?: HelloWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<T> 
  }

export interface Subscription {
    grocer: <T = GrocerSubscriptionPayload | null>(args: { where?: GrocerSubscriptionWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<AsyncIterator<T | null>> ,
    hello: <T = HelloSubscriptionPayload | null>(args: { where?: HelloSubscriptionWhereInput | null }, info?: GraphQLResolveInfo | string, options?: Options) => Promise<AsyncIterator<T | null>> 
  }

export interface Exists {
  Grocer: (where?: GrocerWhereInput) => Promise<boolean>
  Hello: (where?: HelloWhereInput) => Promise<boolean>
}

export interface Prisma {
  query: Query
  mutation: Mutation
  subscription: Subscription
  exists: Exists
  request: <T = any>(query: string, variables?: {[key: string]: any}) => Promise<T>
  delegate(operation: 'query' | 'mutation', fieldName: string, args: {
    [key: string]: any;
}, infoOrQuery?: GraphQLResolveInfo | string, options?: Options): Promise<any>;
delegateSubscription(fieldName: string, args?: {
    [key: string]: any;
}, infoOrQuery?: GraphQLResolveInfo | string, options?: Options): Promise<AsyncIterator<any>>;
getAbstractResolvers(filterSchema?: GraphQLSchema | string): IResolvers;
}

export interface BindingConstructor<T> {
  new(options: BasePrismaOptions): T
}
/**
 * Type Defs
*/

const typeDefs = `type AggregateGrocer {
  count: Int!
}

type AggregateHello {
  count: Int!
}

type BatchPayload {
  """The number of nodes that have been affected by the Batch operation."""
  count: Long!
}

scalar DateTime

type Grocer implements Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  email: String!
}

"""A connection to a list of items."""
type GrocerConnection {
  """Information to aid in pagination."""
  pageInfo: PageInfo!

  """A list of edges."""
  edges: [GrocerEdge]!
  aggregate: AggregateGrocer!
}

input GrocerCreateInput {
  email: String!
}

"""An edge in a connection."""
type GrocerEdge {
  """The item at the end of the edge."""
  node: Grocer!

  """A cursor for use in pagination."""
  cursor: String!
}

enum GrocerOrderByInput {
  id_ASC
  id_DESC
  createdAt_ASC
  createdAt_DESC
  updatedAt_ASC
  updatedAt_DESC
  email_ASC
  email_DESC
}

type GrocerPreviousValues {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  email: String!
}

type GrocerSubscriptionPayload {
  mutation: MutationType!
  node: Grocer
  updatedFields: [String!]
  previousValues: GrocerPreviousValues
}

input GrocerSubscriptionWhereInput {
  """Logical AND on all given filters."""
  AND: [GrocerSubscriptionWhereInput!]

  """Logical OR on all given filters."""
  OR: [GrocerSubscriptionWhereInput!]

  """Logical NOT on all given filters combined by AND."""
  NOT: [GrocerSubscriptionWhereInput!]

  """
  The subscription event gets dispatched when it's listed in mutation_in
  """
  mutation_in: [MutationType!]

  """
  The subscription event gets only dispatched when one of the updated fields names is included in this list
  """
  updatedFields_contains: String

  """
  The subscription event gets only dispatched when all of the field names included in this list have been updated
  """
  updatedFields_contains_every: [String!]

  """
  The subscription event gets only dispatched when some of the field names included in this list have been updated
  """
  updatedFields_contains_some: [String!]
  node: GrocerWhereInput
}

input GrocerUpdateInput {
  email: String
}

input GrocerWhereInput {
  """Logical AND on all given filters."""
  AND: [GrocerWhereInput!]

  """Logical OR on all given filters."""
  OR: [GrocerWhereInput!]

  """Logical NOT on all given filters combined by AND."""
  NOT: [GrocerWhereInput!]
  id: ID

  """All values that are not equal to given value."""
  id_not: ID

  """All values that are contained in given list."""
  id_in: [ID!]

  """All values that are not contained in given list."""
  id_not_in: [ID!]

  """All values less than the given value."""
  id_lt: ID

  """All values less than or equal the given value."""
  id_lte: ID

  """All values greater than the given value."""
  id_gt: ID

  """All values greater than or equal the given value."""
  id_gte: ID

  """All values containing the given string."""
  id_contains: ID

  """All values not containing the given string."""
  id_not_contains: ID

  """All values starting with the given string."""
  id_starts_with: ID

  """All values not starting with the given string."""
  id_not_starts_with: ID

  """All values ending with the given string."""
  id_ends_with: ID

  """All values not ending with the given string."""
  id_not_ends_with: ID
  createdAt: DateTime

  """All values that are not equal to given value."""
  createdAt_not: DateTime

  """All values that are contained in given list."""
  createdAt_in: [DateTime!]

  """All values that are not contained in given list."""
  createdAt_not_in: [DateTime!]

  """All values less than the given value."""
  createdAt_lt: DateTime

  """All values less than or equal the given value."""
  createdAt_lte: DateTime

  """All values greater than the given value."""
  createdAt_gt: DateTime

  """All values greater than or equal the given value."""
  createdAt_gte: DateTime
  updatedAt: DateTime

  """All values that are not equal to given value."""
  updatedAt_not: DateTime

  """All values that are contained in given list."""
  updatedAt_in: [DateTime!]

  """All values that are not contained in given list."""
  updatedAt_not_in: [DateTime!]

  """All values less than the given value."""
  updatedAt_lt: DateTime

  """All values less than or equal the given value."""
  updatedAt_lte: DateTime

  """All values greater than the given value."""
  updatedAt_gt: DateTime

  """All values greater than or equal the given value."""
  updatedAt_gte: DateTime
  email: String

  """All values that are not equal to given value."""
  email_not: String

  """All values that are contained in given list."""
  email_in: [String!]

  """All values that are not contained in given list."""
  email_not_in: [String!]

  """All values less than the given value."""
  email_lt: String

  """All values less than or equal the given value."""
  email_lte: String

  """All values greater than the given value."""
  email_gt: String

  """All values greater than or equal the given value."""
  email_gte: String

  """All values containing the given string."""
  email_contains: String

  """All values not containing the given string."""
  email_not_contains: String

  """All values starting with the given string."""
  email_starts_with: String

  """All values not starting with the given string."""
  email_not_starts_with: String

  """All values ending with the given string."""
  email_ends_with: String

  """All values not ending with the given string."""
  email_not_ends_with: String
}

input GrocerWhereUniqueInput {
  id: ID
  email: String
}

type Hello {
  info: String
}

"""A connection to a list of items."""
type HelloConnection {
  """Information to aid in pagination."""
  pageInfo: PageInfo!

  """A list of edges."""
  edges: [HelloEdge]!
  aggregate: AggregateHello!
}

input HelloCreateInput {
  info: String
}

"""An edge in a connection."""
type HelloEdge {
  """The item at the end of the edge."""
  node: Hello!

  """A cursor for use in pagination."""
  cursor: String!
}

enum HelloOrderByInput {
  info_ASC
  info_DESC
  id_ASC
  id_DESC
  updatedAt_ASC
  updatedAt_DESC
  createdAt_ASC
  createdAt_DESC
}

type HelloPreviousValues {
  info: String
}

type HelloSubscriptionPayload {
  mutation: MutationType!
  node: Hello
  updatedFields: [String!]
  previousValues: HelloPreviousValues
}

input HelloSubscriptionWhereInput {
  """Logical AND on all given filters."""
  AND: [HelloSubscriptionWhereInput!]

  """Logical OR on all given filters."""
  OR: [HelloSubscriptionWhereInput!]

  """Logical NOT on all given filters combined by AND."""
  NOT: [HelloSubscriptionWhereInput!]

  """
  The subscription event gets dispatched when it's listed in mutation_in
  """
  mutation_in: [MutationType!]

  """
  The subscription event gets only dispatched when one of the updated fields names is included in this list
  """
  updatedFields_contains: String

  """
  The subscription event gets only dispatched when all of the field names included in this list have been updated
  """
  updatedFields_contains_every: [String!]

  """
  The subscription event gets only dispatched when some of the field names included in this list have been updated
  """
  updatedFields_contains_some: [String!]
  node: HelloWhereInput
}

input HelloUpdateInput {
  info: String
}

input HelloWhereInput {
  """Logical AND on all given filters."""
  AND: [HelloWhereInput!]

  """Logical OR on all given filters."""
  OR: [HelloWhereInput!]

  """Logical NOT on all given filters combined by AND."""
  NOT: [HelloWhereInput!]
  info: String

  """All values that are not equal to given value."""
  info_not: String

  """All values that are contained in given list."""
  info_in: [String!]

  """All values that are not contained in given list."""
  info_not_in: [String!]

  """All values less than the given value."""
  info_lt: String

  """All values less than or equal the given value."""
  info_lte: String

  """All values greater than the given value."""
  info_gt: String

  """All values greater than or equal the given value."""
  info_gte: String

  """All values containing the given string."""
  info_contains: String

  """All values not containing the given string."""
  info_not_contains: String

  """All values starting with the given string."""
  info_starts_with: String

  """All values not starting with the given string."""
  info_not_starts_with: String

  """All values ending with the given string."""
  info_ends_with: String

  """All values not ending with the given string."""
  info_not_ends_with: String
}

"""
The \`Long\` scalar type represents non-fractional signed whole numeric values.
Long can represent values between -(2^63) and 2^63 - 1.
"""
scalar Long

type Mutation {
  createGrocer(data: GrocerCreateInput!): Grocer!
  createHello(data: HelloCreateInput!): Hello!
  updateGrocer(data: GrocerUpdateInput!, where: GrocerWhereUniqueInput!): Grocer
  deleteGrocer(where: GrocerWhereUniqueInput!): Grocer
  upsertGrocer(where: GrocerWhereUniqueInput!, create: GrocerCreateInput!, update: GrocerUpdateInput!): Grocer!
  updateManyGrocers(data: GrocerUpdateInput!, where: GrocerWhereInput): BatchPayload!
  updateManyHelloes(data: HelloUpdateInput!, where: HelloWhereInput): BatchPayload!
  deleteManyGrocers(where: GrocerWhereInput): BatchPayload!
  deleteManyHelloes(where: HelloWhereInput): BatchPayload!
}

enum MutationType {
  CREATED
  UPDATED
  DELETED
}

"""An object with an ID"""
interface Node {
  """The id of the object."""
  id: ID!
}

"""Information about pagination in a connection."""
type PageInfo {
  """When paginating forwards, are there more items?"""
  hasNextPage: Boolean!

  """When paginating backwards, are there more items?"""
  hasPreviousPage: Boolean!

  """When paginating backwards, the cursor to continue."""
  startCursor: String

  """When paginating forwards, the cursor to continue."""
  endCursor: String
}

type Query {
  grocers(where: GrocerWhereInput, orderBy: GrocerOrderByInput, skip: Int, after: String, before: String, first: Int, last: Int): [Grocer]!
  helloes(where: HelloWhereInput, orderBy: HelloOrderByInput, skip: Int, after: String, before: String, first: Int, last: Int): [Hello]!
  grocer(where: GrocerWhereUniqueInput!): Grocer
  grocersConnection(where: GrocerWhereInput, orderBy: GrocerOrderByInput, skip: Int, after: String, before: String, first: Int, last: Int): GrocerConnection!
  helloesConnection(where: HelloWhereInput, orderBy: HelloOrderByInput, skip: Int, after: String, before: String, first: Int, last: Int): HelloConnection!

  """Fetches an object given its ID"""
  node(
    """The ID of an object"""
    id: ID!
  ): Node
}

type Subscription {
  grocer(where: GrocerSubscriptionWhereInput): GrocerSubscriptionPayload
  hello(where: HelloSubscriptionWhereInput): HelloSubscriptionPayload
}
`

export const Prisma = makePrismaBindingClass<BindingConstructor<Prisma>>({typeDefs})

/**
 * Types
*/

export type GrocerOrderByInput =   'id_ASC' |
  'id_DESC' |
  'createdAt_ASC' |
  'createdAt_DESC' |
  'updatedAt_ASC' |
  'updatedAt_DESC' |
  'email_ASC' |
  'email_DESC'

export type HelloOrderByInput =   'info_ASC' |
  'info_DESC' |
  'id_ASC' |
  'id_DESC' |
  'updatedAt_ASC' |
  'updatedAt_DESC' |
  'createdAt_ASC' |
  'createdAt_DESC'

export type MutationType =   'CREATED' |
  'UPDATED' |
  'DELETED'

export interface GrocerCreateInput {
  email: String
}

export interface GrocerSubscriptionWhereInput {
  AND?: GrocerSubscriptionWhereInput[] | GrocerSubscriptionWhereInput | null
  OR?: GrocerSubscriptionWhereInput[] | GrocerSubscriptionWhereInput | null
  NOT?: GrocerSubscriptionWhereInput[] | GrocerSubscriptionWhereInput | null
  mutation_in?: MutationType[] | MutationType | null
  updatedFields_contains?: String | null
  updatedFields_contains_every?: String[] | String | null
  updatedFields_contains_some?: String[] | String | null
  node?: GrocerWhereInput | null
}

export interface GrocerUpdateInput {
  email?: String | null
}

export interface GrocerWhereInput {
  AND?: GrocerWhereInput[] | GrocerWhereInput | null
  OR?: GrocerWhereInput[] | GrocerWhereInput | null
  NOT?: GrocerWhereInput[] | GrocerWhereInput | null
  id?: ID_Input | null
  id_not?: ID_Input | null
  id_in?: ID_Output[] | ID_Output | null
  id_not_in?: ID_Output[] | ID_Output | null
  id_lt?: ID_Input | null
  id_lte?: ID_Input | null
  id_gt?: ID_Input | null
  id_gte?: ID_Input | null
  id_contains?: ID_Input | null
  id_not_contains?: ID_Input | null
  id_starts_with?: ID_Input | null
  id_not_starts_with?: ID_Input | null
  id_ends_with?: ID_Input | null
  id_not_ends_with?: ID_Input | null
  createdAt?: DateTime | null
  createdAt_not?: DateTime | null
  createdAt_in?: DateTime[] | DateTime | null
  createdAt_not_in?: DateTime[] | DateTime | null
  createdAt_lt?: DateTime | null
  createdAt_lte?: DateTime | null
  createdAt_gt?: DateTime | null
  createdAt_gte?: DateTime | null
  updatedAt?: DateTime | null
  updatedAt_not?: DateTime | null
  updatedAt_in?: DateTime[] | DateTime | null
  updatedAt_not_in?: DateTime[] | DateTime | null
  updatedAt_lt?: DateTime | null
  updatedAt_lte?: DateTime | null
  updatedAt_gt?: DateTime | null
  updatedAt_gte?: DateTime | null
  email?: String | null
  email_not?: String | null
  email_in?: String[] | String | null
  email_not_in?: String[] | String | null
  email_lt?: String | null
  email_lte?: String | null
  email_gt?: String | null
  email_gte?: String | null
  email_contains?: String | null
  email_not_contains?: String | null
  email_starts_with?: String | null
  email_not_starts_with?: String | null
  email_ends_with?: String | null
  email_not_ends_with?: String | null
}

export interface GrocerWhereUniqueInput {
  id?: ID_Input | null
  email?: String | null
}

export interface HelloCreateInput {
  info?: String | null
}

export interface HelloSubscriptionWhereInput {
  AND?: HelloSubscriptionWhereInput[] | HelloSubscriptionWhereInput | null
  OR?: HelloSubscriptionWhereInput[] | HelloSubscriptionWhereInput | null
  NOT?: HelloSubscriptionWhereInput[] | HelloSubscriptionWhereInput | null
  mutation_in?: MutationType[] | MutationType | null
  updatedFields_contains?: String | null
  updatedFields_contains_every?: String[] | String | null
  updatedFields_contains_some?: String[] | String | null
  node?: HelloWhereInput | null
}

export interface HelloUpdateInput {
  info?: String | null
}

export interface HelloWhereInput {
  AND?: HelloWhereInput[] | HelloWhereInput | null
  OR?: HelloWhereInput[] | HelloWhereInput | null
  NOT?: HelloWhereInput[] | HelloWhereInput | null
  info?: String | null
  info_not?: String | null
  info_in?: String[] | String | null
  info_not_in?: String[] | String | null
  info_lt?: String | null
  info_lte?: String | null
  info_gt?: String | null
  info_gte?: String | null
  info_contains?: String | null
  info_not_contains?: String | null
  info_starts_with?: String | null
  info_not_starts_with?: String | null
  info_ends_with?: String | null
  info_not_ends_with?: String | null
}

/*
 * An object with an ID

 */
export interface Node {
  id: ID_Output
}

export interface AggregateGrocer {
  count: Int
}

export interface AggregateHello {
  count: Int
}

export interface BatchPayload {
  count: Long
}

export interface Grocer extends Node {
  id: ID_Output
  createdAt: DateTime
  updatedAt: DateTime
  email: String
}

/*
 * A connection to a list of items.

 */
export interface GrocerConnection {
  pageInfo: PageInfo
  edges: Array<GrocerEdge | null>
  aggregate: AggregateGrocer
}

/*
 * An edge in a connection.

 */
export interface GrocerEdge {
  node: Grocer
  cursor: String
}

export interface GrocerPreviousValues {
  id: ID_Output
  createdAt: DateTime
  updatedAt: DateTime
  email: String
}

export interface GrocerSubscriptionPayload {
  mutation: MutationType
  node?: Grocer | null
  updatedFields?: Array<String> | null
  previousValues?: GrocerPreviousValues | null
}

export interface Hello {
  info?: String | null
}

/*
 * A connection to a list of items.

 */
export interface HelloConnection {
  pageInfo: PageInfo
  edges: Array<HelloEdge | null>
  aggregate: AggregateHello
}

/*
 * An edge in a connection.

 */
export interface HelloEdge {
  node: Hello
  cursor: String
}

export interface HelloPreviousValues {
  info?: String | null
}

export interface HelloSubscriptionPayload {
  mutation: MutationType
  node?: Hello | null
  updatedFields?: Array<String> | null
  previousValues?: HelloPreviousValues | null
}

/*
 * Information about pagination in a connection.

 */
export interface PageInfo {
  hasNextPage: Boolean
  hasPreviousPage: Boolean
  startCursor?: String | null
  endCursor?: String | null
}

/*
The `Boolean` scalar type represents `true` or `false`.
*/
export type Boolean = boolean

export type DateTime = Date | string

/*
The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
*/
export type ID_Input = string | number
export type ID_Output = string

/*
The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. 
*/
export type Int = number

/*
The `Long` scalar type represents non-fractional signed whole numeric values.
Long can represent values between -(2^63) and 2^63 - 1.
*/
export type Long = string

/*
The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
*/
export type String = string