// ✅ SMELL-15 FIXED: Magic strings replaced with enum
namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>Account type classification.</summary>
public enum AccountType
{
    Checking,
    Savings,
    Investment,
    Credit
}
