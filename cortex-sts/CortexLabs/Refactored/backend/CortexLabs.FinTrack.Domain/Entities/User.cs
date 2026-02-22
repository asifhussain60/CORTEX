using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>
/// User domain entity — fixes SMELL-01 (God Class decomposition),
/// SMELL-04 (hardcoded credentials removed), SMELL-11 (proper hashing).
/// Audit fields (CreatedAt, UpdatedAt) satisfy NFR-MAINT-002.
/// </summary>
public class User
{
    public int Id { get; set; }

    public string Username { get; set; } = string.Empty;

    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// BCrypt-hashed password — never stored in plain text (SMELL-04 fix).
    /// </summary>
    public string PasswordHash { get; set; } = string.Empty;

    public UserRole Role { get; set; } = UserRole.User;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
