namespace netBox.Repositories
{
    using System;
    using System.Collections.Generic;
    using System.Threading;
    using System.Threading.Tasks;
    using netBox.Models;

    public interface IDroidRepository
    {
        Task<Droid> GetDroid(Guid id, CancellationToken cancellationToken);

        Task<List<Droid>> GetDroids(
            int? first,
            CancellationToken cancellationToken);

        Task<List<Droid>> GetDroidsReverse(
            int? first,
            CancellationToken cancellationToken);

        Task<bool> GetHasNextPage(
            int? first,
            CancellationToken cancellationToken);

        Task<bool> GetHasPreviousPage(
            int? last,
            CancellationToken cancellationToken);

        Task<List<Droid>> GetFriends(Droid droid, CancellationToken cancellationToken);

        Task<int> GetTotalCount(CancellationToken cancellationToken);
    }
}
