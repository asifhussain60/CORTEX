# User Story Format Quick Reference

**Purpose:** Extract user stories from legacy C# code in standard format

---

## 📋 Standard Format

```
As a [Actor/Persona],
I want to [Action/Capability],
So that [Business Value/Outcome].
```

---

## 🎭 Actor Detection

**Pattern:** Class name analysis

| Code Contains | Actor |
|---------------|-------|
| `Updater`, `Batch` | System Administrator |
| `Employer` | Employer |
| `Account`, `Member` | Account Holder |
| `Invoice`, `Funding` | Finance Team Member |
| `Report` | Business Analyst |
| `Admin` | System Administrator |
| *Default* | System User |

---

## 🎯 Action Parsing

**Pattern:** PascalCase → verb phrase

**Steps:**
1. Extract words: `XGenerateFundingInvoice` → `[X, Generate, Funding, Invoice]`
2. Remove prefixes: `[Generate, Funding, Invoice]`
3. Convert to verb: `Generate` → `generate`
4. Build phrase: `"generate funding invoice"`

**Common Verbs:**
- Create, Generate, Update, Delete
- Process, Validate, Calculate
- Send, Receive, Close, Open

---

## 💡 Business Value Inference

**Pattern:** Context analysis

| Code Pattern | Inferred Value |
|--------------|----------------|
| Funding/Invoice | "ensure accurate and timely reimbursement processing" |
| Batch/Updater | "maintain data consistency and automate operations" |
| INSERT/UPDATE ops | "maintain accurate system records" |
| SELECT ops | "retrieve information for decision making" |
| 3+ validations | "ensure data quality and prevent errors" |

---

## 📊 Supporting Stories

**Generated from business rule themes:**

| Theme | Story |
|-------|-------|
| null/empty checks | "As a Data Quality Manager, I want to validate all inputs, so that system integrity is maintained." |
| date/time | "As a Operations Manager, I want to control timing of operations, so that processes execute at the right time." |
| amount/balance | "As a Finance Controller, I want to validate financial amounts, so that transactions are accurate." |
| status/state | "As a System Administrator, I want to manage entity states, so that workflows progress correctly." |

---

## ✅ Acceptance Criteria Format

```
Given [precondition],
When [action occurs],
Then [expected outcome] (Line [number])
```

**Example:**
```
1. Given InvoiceAmount <= 0, when processing occurs,
   then system must apply InvoiceAmount_0 logic (Line 21)
```

---

## 📁 Output Locations

**Executive Summary:**
- Primary user story
- Supporting stories (up to 4)

**User Stories Section (👥):**
- Primary story with full format
- Acceptance criteria (validation, business logic, data)
- Supporting stories
- Traceability note

---

## 🚀 Quick Example

**Legacy Code:**
```csharp
public class XGenerateFundingInvoice : HETransaction {
    public void Execute() {
        if (InvoiceAmount <= 0) { ... }
        if (InvoiceDate < DateTime.Today) { ... }
        // SELECT from Subaccount
    }
}
```

**Generated User Story:**
```
As a Finance Team Member,
I want to generate funding invoice,
So that ensure accurate and timely reimbursement processing.

Acceptance Criteria:
1. Given InvoiceAmount <= 0, when processing occurs,
   then system must apply validation logic (Line 21)
2. Given InvoiceDate < DateTime.Today, when processing occurs,
   then system must check date validity (Line 23)
3. Given successful processing, when retrieving subaccount,
   then SELECT must execute on Subaccount (Line 29)
```

---

**Version:** 2.1  
**Status:** Production Ready
