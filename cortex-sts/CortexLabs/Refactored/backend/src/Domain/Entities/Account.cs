// FIX SMELL-7 SMELL-15 SMELL-19 SMELL-20
using System.ComponentModel.DataAnnotations;
namespace CortexLabs.FinTrack.Domain.Entities;
public class Account {
    public int Id { get; set; }
    [Required, MaxLength(200)] public string AccountName { get; set; } = string.Empty;
    public decimal Balance { get; set; }
    public int UserId { get; set; }
    public AccountType AccountType { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;
    [Timestamp] public byte[]? RowVersion { get; set; }
}
public enum AccountType { Checking, Savings, Investment, Credit }