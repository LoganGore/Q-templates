namespace netBox.Schemas
{
  using System;
  using System.Collections.Generic;
  using System.Linq;
  using System.Threading;
  using System.Threading.Tasks;
  using Boxed.AspNetCore;
  using GraphQL.Builders;
  using GraphQL.Types;
  using GraphQL.Types.Relay.DataObjects;
  using netBox.Models;
  using netBox.Repositories;
  using netBox.Types;

  /// <summary>
  /// All queries defined in the schema used to retrieve data.
  /// </summary>
  /// <example>
  /// The is an example query to get a human and the details of their friends.
  /// <c>
  /// query getHuman {
  ///   human(id: "94fbd693-2027-4804-bf40-ed427fe76fda")
  ///   {
  ///     id
  ///     name
  ///     dateOfBirth
  ///     homePlanet
  ///     appearsIn
  ///     friends {
  ///       name
  ///       ... on Droid {
  ///         chargePeriod
  ///         created
  ///         primaryFunction
  ///       }
  ///       ... on Human
  ///       {
  ///         dateOfBirth
  ///         homePlanet
  ///       }
  ///     }
  ///   }
  /// }
  /// </c>
  /// </example>
  public class QueryObject : ObjectGraphType<object>
  {
    private const int MaxPageSize = 10;

    public QueryObject(
        IDroidRepository droidRepository,
        IHumanRepository humanRepository)
    {
      this.Name = "Query";
      this.Description = "The query type, represents all of the entry points into our object graph.";

      this.FieldAsync<DroidObject, Droid>(
          "droid",
          "Get a droid by its unique identifier.",
          arguments: new QueryArguments(
              new QueryArgument<NonNullGraphType<IdGraphType>>
              {
                Name = "id",
                Description = "The unique identifier of the droid.",
              }),
          resolve: context =>
              droidRepository.GetDroid(
                  context.GetArgument("id", defaultValue: new Guid("1ae34c3b-c1a0-4b7b-9375-c5a221d49e68")),
                  context.CancellationToken));
      
        this.FieldAsync<DroidObject, Droid>(
          "randomDroid",
          "Get a random droid from the database.",
          resolve: context =>
              droidRepository.GetRandomDroid(context.CancellationToken));

      this.FieldAsync<HumanObject, Human>(
          "human",
          "Get a human by its unique identifier.",
          arguments: new QueryArguments(
              new QueryArgument<NonNullGraphType<IdGraphType>>()
              {
                Name = "id",
                Description = "The unique identifier of the human.",
              }),
          resolve: context => humanRepository.GetHuman(
              context.GetArgument("id", defaultValue: new Guid("94fbd693-2027-4804-bf40-ed427fe76fda")),
              context.CancellationToken));

      this.FieldAsync<HumanObject, Human>(
          "randomHuman",
          "Get a random human from the database.",
          resolve: context =>
              humanRepository.GetRandomHuman(context.CancellationToken));

      // Just include static info for info query in this case as it's not hitting the dummy repository/database.
      this.Field<InfoObject>(
          "info",
          resolve: context =>
          {
            return new Info
            {
              Id = "ed7584-2124-98fs-00s3-t739478t",
              Name = "maana.io.template",
              Description = "Dockerized ASP.NET Core GraphQL Template"

            };
          });
    }
  }
}
