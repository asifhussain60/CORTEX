// FIX SMELL-7 SMELL-19 SMELL-20
using System.ComponentModel.DataAnnotations;
namespace CortexLabs.FinTrack.Domain.Entities;
public class User {
    public int Id { get; set; }
    [Required, MaxLength(100)] public string UserName { get; set; } = string.Empty;
    [Required, EmailAddress, MaxLength(255)] public string Email { get; set; } = string.Empty;
    [Required] public string PasswordHash { get; set; } = string.Empty;
    [MaxLength(50)] public string Role { get; set; } = "user";
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;
}