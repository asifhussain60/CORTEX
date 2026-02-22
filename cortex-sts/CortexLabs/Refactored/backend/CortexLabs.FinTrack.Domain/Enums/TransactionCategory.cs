namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>
/// Transaction categories — replaces magic strings "food", "transport", etc. (SMELL-15).
/// Thresholds for auto-categorization defined in TransactionService (not inline in endpoints).
/// </summary>
public enum TransactionCategory
{
    Food,
    Transport,
    Entertainment,
    LargePurchase,
    MediumPurchase,
    Other
}
