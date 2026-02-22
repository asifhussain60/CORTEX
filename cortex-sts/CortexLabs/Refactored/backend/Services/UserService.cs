// ✅ CORTEX Refactored — UserService
// ✅ SMELL-5 RESOLVED: No circular dependencies
// ✅ SMELL-17 RESOLVED: Constructor injection

using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Repositories.Interfaces;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Services;

/// <summary>
/// User service — handles user CRUD operations with proper DI
/// </summary>
public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;
    private readonly IValidationService _validationService;
    private readonly ILogger<UserService> _logger;

    // ✅ SMELL-17 RESOLVED: Constructor injection, no direct instantiation
    public UserService(
        IUserRepository userRepository,
        IValidationService validationService,
        ILogger<UserService> logger)
    {
        _userRepository = userRepository ?? throw new ArgumentNullException(nameof(userRepository));
        _validationService = validationService ?? throw new ArgumentNullException(nameof(validationService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<UserDto?> GetByIdAsync(int id)
    {
        _logger.LogDebug("Fetching user by id: {UserId}", id);
        var user = await _userRepository.GetByIdAsync(id);
        return user != null ? MapToDto(user) : null;
    }

    // ✅ SMELL-6 RESOLVED: Pagination support
    public async Task<IEnumerable<UserDto>> GetAllAsync(int page = 1, int pageSize = 20)
    {
        _logger.LogDebug("Fetching users page {Page} with size {PageSize}", page, pageSize);
        var users = await _userRepository.GetPagedAsync(page, pageSize);
        return users.Select(MapToDto);
    }

    public async Task<UserDto?> GetByUsernameAsync(string username)
    {
        _logger.LogDebug("Fetching user by username: {Username}", username);
        var user = await _userRepository.GetByUsernameAsync(username);
        return user != null ? MapToDto(user) : null;
    }

    public async Task<UserDto> CreateAsync(CreateUserDto dto)
    {
        _logger.LogInformation("Creating new user: {Username}", dto.UserName);

        // ✅ SMELL-10 RESOLVED: Use centralized validation
        var validation = _validationService.ValidateUser(dto);
        if (!validation.IsValid)
        {
            throw new ValidationException(validation.Errors);
        }

        var user = new User
        {
            UserName = dto.UserName,
            Email = dto.Email,
            PasswordHash = HashPassword(dto.Password), // ✅ SMELL-2: Hash passwords
            Role = dto.Role ?? "user",
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        var created = await _userRepository.CreateAsync(user);
        _logger.LogInformation("Created user with id: {UserId}", created.Id);

        return MapToDto(created);
    }

    public async Task<bool> UpdateAsync(int id, UpdateUserDto dto)
    {
        _logger.LogInformation("Updating user: {UserId}", id);

        var user = await _userRepository.GetByIdAsync(id);
        if (user == null) return false;

        if (dto.Email != null)
        {
            var validation = _validationService.ValidateEmail(dto.Email);
            if (!validation.IsValid)
            {
                throw new ValidationException(validation.Errors);
            }
            user.Email = dto.Email;
        }

        if (dto.Role != null) user.Role = dto.Role;
        if (dto.IsActive.HasValue) user.IsActive = dto.IsActive.Value;

        user.ModifiedAt = DateTime.UtcNow;

        return await _userRepository.UpdateAsync(user);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        _logger.LogInformation("Deleting user: {UserId}", id);
        return await _userRepository.DeleteAsync(id);
    }

    // ✅ Private helpers

    private static UserDto MapToDto(User user)
    {
        return new UserDto(
            user.Id,
            user.UserName,
            user.Email,
            user.Role,
            user.IsActive);
    }

    private static string HashPassword(string password)
    {
        // ✅ In production: use BCrypt.Net-Next or Argon2
        return BCrypt.Net.BCrypt.HashPassword(password);
    }
}

// ✅ Exception types
public class ValidationException : Exception
{
    public IEnumerable<string> Errors { get; }

    public ValidationException(IEnumerable<string> errors) 
        : base(string.Join("; ", errors))
    {
        Errors = errors;
    }
}
