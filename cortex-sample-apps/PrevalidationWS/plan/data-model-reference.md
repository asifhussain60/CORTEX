# Data Model Reference

**Purpose:** Complete field definitions for all 9 PSF record types  
**Source:** Business/PSFValidator.cs analysis

---

## 📋 Record Type Definitions

### PAF (Payment Authorization File) - 19 Fields
```
Field 01: Record Type (PAF)
Field 02: Employer ID (10 chars)
Field 03: Payment Date (YYYYMMDD)
Field 04: Payment Amount (decimal 15,2)
Field 05: Payment Type Code (2 chars)
Field 06: Authorization Number (20 chars)
Field 07: Transaction ID (GUID)
Field 08: Employee Count (int)
Field 09: Total Deductions (decimal 15,2)
Field 10: Total Contributions (decimal 15,2)
Field 11: Currency Code (USD, 3 chars)
Field 12: Processing Status (1 char: P/C/F)
Field 13: Created By User ID (50 chars)
Field 14: Created Date (YYYYMMDD HH:mm:ss)
Field 15: Modified By User ID (50 chars)
Field 16: Modified Date (YYYYMMDD HH:mm:ss)
Field 17: Approval Status (1 char: A/R/P)
Field 18: Comments (255 chars, optional)
Field 19: Checksum (calculated MD5)
```

### PAI (Payment Authorization Item) - 8 Fields
```
Field 01: Record Type (PAI)
Field 02: Employer ID (10 chars)
Field 03: Employee SSN (11 chars, masked)
Field 04: Employee Name (100 chars)
Field 05: Deduction Amount (decimal 15,2)
Field 06: Contribution Amount (decimal 15,2)
Field 07: Item Sequence (int)
Field 08: Item Status (1 char: V/I)
```

### PRF (Payment Request File) - 17 Fields
*(Similar structure to PAF with different fields)*

### Other Record Types
- PRI: Payment Request Item (6 fields)
- PAH: Payment Authorization Header (12 fields)
- PFL: Payment File Line (15 fields)
- PFH: Payment File Header (10 fields)
- PTF: Payment Transaction File (14 fields)
- PTH: Payment Transaction Header (8 fields)

---

## 🔍 Validation Rules

### Required Fields (All Record Types)
- Record Type (position 0-2, must match valid types)
- Employer ID (position varies, 10 chars, alphanumeric)

### Data Type Validations
- Dates: YYYYMMDD format, valid date range 1900-2100
- Decimals: Precision 15,2, non-negative for amounts
- Status codes: Must match allowed values
- GUIDs: Valid GUID format for transaction IDs

### ERROR TYPE Mapping
1. Invalid Record Type → Not in [PAF, PAI, PRF, PRI, PAH, PFL, PFH, PTF, PTH]
2. Invalid Format → Fixed-width position mismatch
3. Empty File → File length = 0 or no records
4. Exceeds Max Lines → > 100,000 records
5. Invalid Header → First record not PAH/PFH/PTH
6. Missing Required Data → Required field is null/empty
7. Invalid Data Format → Field doesn't match expected format
8. Invalid Date → Date parsing fails or out of range
9. Invalid Numeric → Numeric parsing fails
10. Invalid Currency → Decimal parsing fails or negative
11. Duplicate Record → Same transaction ID appears twice
12. Invalid Checksum → Calculated checksum doesn't match field 19
13. Invalid Control Total → Sum of items doesn't match header total
14. Unknown Record Type → Record type starts with 'P' but not in valid list

---

## 📚 Related Documents
- [Phase 3: Business Logic](phase-3-business-logic.md) - Validator implementation
- [Phase 5a: Schema Validation](phase-5a-schema-validation.md) - Schema tests
- [Current State Analysis](current-state-analysis.md) - Legacy analysis
