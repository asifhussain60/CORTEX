using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.DTOs;

/// <summary>
/// Inbound DTO for user registration — fixes SMELL-07 (typed validation),
/// SMELL-11 (password never returned in response).
/// </summary>
public class CreateUserDto
{
    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string Username { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;

    [Required]
    [StringLength(100, MinimumLength = 8)]
    public string Password { get; set; } = string.Empty;
}

/// <summary>
/// Outbound DTO for user data — password hash is NEVER exposed.
/// </summary>
public class UserDto
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public UserRole Role { get; set; }
    public DateTime CreatedAt { get; set; }
}

/// <summary>
/// Login request DTO — credentials only.
/// </summary>
public class LoginDto
{
    [Required]
    public string Username { get; set; } = string.Empty;

    [Required]
    public string Password { get; set; } = string.Empty;
}
