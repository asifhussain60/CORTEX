// ✅ SMELL-15 FIXED: Magic strings replaced with enum
namespace CortexLabs.FinTrack.Domain.Enums;

/// <summary>Classification for a named transaction category.</summary>
public enum TransactionCategory
{
    Food,
    Transport,
    Entertainment,
    LargePurchase,
    MediumPurchase,
    Utilities,
    Healthcare,
    Other
}
