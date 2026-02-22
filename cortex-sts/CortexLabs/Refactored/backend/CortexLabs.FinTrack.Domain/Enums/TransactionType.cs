namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>
/// Transaction type — replaces magic strings "income" and "expense" (SMELL-15).
/// </summary>
public enum TransactionType
{
    Income,
    Expense
}
