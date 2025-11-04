namespace MyApp.Services;

public interface IUserService
{
    Task<IEnumerable<string>> GetUsersAsync();
}

public class UserService : IUserService
{
    public Task<IEnumerable<string>> GetUsersAsync()
    {
        return Task.FromResult<IEnumerable<string>>(new[] { "User1", "User2" });
    }
}
