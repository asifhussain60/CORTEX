using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Application.Validators;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// User service — fixes SMELL-01 (God Class), SMELL-02 (DI),
/// SMELL-04 (hardcoded creds), SMELL-11 (plaintext passwords).
/// All business logic for user domain extracted here from Program.cs.
/// </summary>
public class UserService
{
    private readonly IUserRepository _userRepository;
    private readonly ILogger<UserService> _logger;

    public UserService(IUserRepository userRepository, ILogger<UserService> logger)
    {
        _userRepository = userRepository ?? throw new ArgumentNullException(nameof(userRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<UserDto?> GetByIdAsync(int id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        return user is null ? null : MapToDto(user);
    }

    public async Task<PagedResponse<UserDto>> GetAllAsync(int page, int pageSize)
    {
        page = Math.Max(1, page);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var users = await _userRepository.GetAllAsync(page, pageSize);
        var totalCount = await _userRepository.GetCountAsync();

        return new PagedResponse<UserDto>
        {
            Items = users.Select(MapToDto).ToList(),
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount
        };
    }

    public async Task<(UserDto? User, string? Error)> CreateAsync(CreateUserDto dto)
    {
        if (!EmailValidator.IsValid(dto.Email))
            return (null, "Invalid email format");

        var existing = await _userRepository.GetByUsernameAsync(dto.Username);
        if (existing is not null)
            return (null, "Username already exists");

        var existingEmail = await _userRepository.GetByEmailAsync(dto.Email);
        if (existingEmail is not null)
            return (null, "Email already registered");

        var user = new User
        {
            Username = dto.Username,
            Email = dto.Email,
            PasswordHash = HashPassword(dto.Password),
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        var id = await _userRepository.CreateAsync(user);
        user.Id = id;

        _logger.LogInformation("User created: {UserId} ({Username})", id, dto.Username);
        return (MapToDto(user), null);
    }

    public async Task<(UserDto? User, string? Error)> AuthenticateAsync(LoginDto dto)
    {
        var user = await _userRepository.GetByUsernameAsync(dto.Username);
        if (user is null)
        {
            _logger.LogWarning("Login failed: user not found ({Username})", dto.Username);
            return (null, "Invalid credentials");
        }

        if (!VerifyPassword(dto.Password, user.PasswordHash))
        {
            _logger.LogWarning("Login failed: invalid password ({Username})", dto.Username);
            return (null, "Invalid credentials");
        }

        _logger.LogInformation("User authenticated: {UserId}", user.Id);
        return (MapToDto(user), null);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var result = await _userRepository.DeleteAsync(id);
        if (result)
            _logger.LogInformation("User deleted: {UserId}", id);
        return result;
    }

    /// <summary>
    /// Simple hash using SHA256 + salt — production would use BCrypt/Argon2.
    /// Fixes SMELL-11 (plaintext passwords) without adding new NuGet packages.
    /// </summary>
    internal static string HashPassword(string password)
    {
        var salt = Guid.NewGuid().ToString("N")[..16];
        var hash = Convert.ToBase64String(
            System.Security.Cryptography.SHA256.HashData(
                System.Text.Encoding.UTF8.GetBytes(salt + password)));
        return $"{salt}:{hash}";
    }

    internal static bool VerifyPassword(string password, string storedHash)
    {
        var parts = storedHash.Split(':');
        if (parts.Length != 2) return false;

        var salt = parts[0];
        var expectedHash = Convert.ToBase64String(
            System.Security.Cryptography.SHA256.HashData(
                System.Text.Encoding.UTF8.GetBytes(salt + password)));
        return expectedHash == parts[1];
    }

    private static UserDto MapToDto(User user) => new()
    {
        Id = user.Id,
        Username = user.Username,
        Email = user.Email,
        Role = user.Role,
        CreatedAt = user.CreatedAt
    };
}
