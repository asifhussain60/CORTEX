// ✅ SMELL-15 FIXED: Magic strings "income"/"expense" replaced with typed enum
// ✅ SMELL-7 FIXED: PascalCase throughout

namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>Classifies the financial direction of a transaction.</summary>
public enum TransactionType
{
    Income,
    Expense,
    Transfer
}
