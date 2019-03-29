namespace netBox.Repositories
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Threading;
    using System.Threading.Tasks;
    using netBox.Models;

    public class DroidRepository : IDroidRepository
    {
        public Task<Droid> GetDroid(Guid id, CancellationToken cancellationToken) =>
            Task.FromResult(Database.Droids.FirstOrDefault(x => x.Id == id));

        public Task<List<Droid>> GetDroids(
            int? first,
            CancellationToken cancellationToken) =>
            Task.FromResult(Database
                .Droids
                .If(first.HasValue, x => x.Take(first.Value))
                .ToList());

        public Task<List<Droid>> GetDroidsReverse(
            int? last,
            CancellationToken cancellationToken) =>
            Task.FromResult(Database
                .Droids
                .If(last.HasValue, x => x.TakeLast(last.Value))
                .ToList());

        public Task<bool> GetHasNextPage(
            int? first,
            CancellationToken cancellationToken) =>
            Task.FromResult(Database
                .Droids
                .Skip(first.Value)
                .Any());

        public Task<bool> GetHasPreviousPage(
            int? last,
            CancellationToken cancellationToken) =>
            Task.FromResult(Database
                .Droids
                .SkipLast(last.Value)
                .Any());

        public Task<List<Droid>> GetFriends(Droid droid, CancellationToken cancellationToken) =>
            Task.FromResult(Database.Droids.Where(x => droid.Friends.Contains(x.Id)).ToList());

        public Task<int> GetTotalCount(CancellationToken cancellationToken) =>
            Task.FromResult(Database.Droids.Count);
    }
}
