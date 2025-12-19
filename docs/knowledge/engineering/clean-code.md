# Clean Code Principles

**Author:** Robert C. Martin (Uncle Bob)
**Source:** Clean Code: A Handbook of Agile Software Craftsmanship
**Version:** 1.0 | **Updated:** 2025-12-19

---

## Overview

This guide provides authoritative clean code principles for AI-powered code generation, review, and refactoring.

---

## 1. Meaningful Names

**Principle:** Names should reveal intent without requiring comments

**Importance:** Critical - names are everywhere in code

### Rules

#### NAMING_001: Use Intention-Revealing Names

**Description:** Name should answer why it exists, what it does, how it's used

**Severity:** `HIGH`

✅ **Good Examples:**

```python
elapsed_time_in_days = 365  # Clear intent
days_since_creation = 100
days_since_modification = 50
```
*Variable names explain what they measure*

```csharp
List<Customer> activeCustomers = GetActiveCustomers();
decimal totalRevenueThisQuarter = CalculateQuarterlyRevenue();
```
*Names describe content and purpose*

❌ **Bad Examples:**

```python
d = 365  # What does 'd' represent?
elap = 100
t = 50
```
*Single-letter names require mental mapping*

```csharp
List<Customer> list1 = GetCustomers();
decimal amt = Calculate();
```
*Generic names hide intent*

---

#### NAMING_002: Avoid Disinformation

**Description:** Don't use names that mislead about what the code does

**Severity:** `CRITICAL`

✅ **Good Examples:**

```python
account_group = []  # It's a list, not a dict
customer_collection = {}  # It's a dict
```
*Names match actual data structures*

❌ **Bad Examples:**

```python
accountList = {}  # Misleading - it's a dict, not a list
hp = calculate_distance()  # 'hp' suggests health points, not distance
```
*Names contradict implementation*

---

#### NAMING_003: Make Meaningful Distinctions

**Description:** If names must be different, they should also mean something different

**Severity:** `HIGH`

✅ **Good Examples:**

```python
def copy_chars(source: str, destination: str):
    """Clear distinction between source and destination"""
    pass
```
*Names explain roles*

❌ **Bad Examples:**

```python
def copy_chars(a1: str, a2: str):  # Which is source? Which is destination?
    pass

# Number-series naming
product_info = {}
product_data = {}  # What's the difference?
```
*Indistinguishable names cause confusion*

---

#### NAMING_004: Use Pronounceable Names

**Description:** If you can't pronounce it, you can't discuss it

**Severity:** `MEDIUM`

✅ **Good Examples:**

```python
generation_timestamp = datetime.now()
modification_timestamp = datetime.now()
```
*Easy to discuss: 'generation timestamp'*

❌ **Bad Examples:**

```python
genymdhms = datetime.now()  # Generate YMDHMS?
modymdhms = datetime.now()
```
*Unpronounceable abbreviations*

---

#### NAMING_005: Use Searchable Names

**Description:** Single-letter names and numeric constants are hard to locate

**Severity:** `HIGH`

✅ **Good Examples:**

```python
MAX_CLASSES_PER_STUDENT = 7

for student in students:
    if student.class_count > MAX_CLASSES_PER_STUDENT:
        raise ValueError("Too many classes")
```
*Can search for 'MAX_CLASSES_PER_STUDENT'*

❌ **Bad Examples:**

```python
for s in students:
    if s.count > 7:  # What is 7? Why 7?
        raise ValueError("error")
```
*Can't search for '7' or 's'*

---

#### NAMING_006: Avoid Encodings (No Hungarian Notation)

**Description:** Modern IDEs make type prefixes unnecessary

**Severity:** `LOW`

✅ **Good Examples:**

```python
phone_number: str = "+1-555-0100"
customer: Customer = Customer()
```
*Type hints > prefixes*

❌ **Bad Examples:**

```python
str_phone_number = "+1-555-0100"  # Redundant
obj_customer = Customer()  # Type obvious from constructor
```
*Type prefixes are noise*

---

#### NAMING_007: Class Names Should Be Nouns

**Description:** Classes represent things, so use noun or noun phrases

**Severity:** `HIGH`

✅ **Good Examples:**

```python
class Customer:
    pass

class Account:
    pass

class AddressParser:
    pass
```
*Nouns describe entities*

❌ **Bad Examples:**

```python
class Manager:  # Too generic
    pass

class Process:  # Verb, not noun
    pass
```
*Verbs or generic nouns*

---

#### NAMING_008: Method Names Should Be Verbs

**Description:** Methods do things, so use verb or verb phrases

**Severity:** `HIGH`

✅ **Good Examples:**

```python
def save_customer(customer: Customer):
    pass

def delete_page(page: Page):
    pass

def is_valid_email(email: str) -> bool:
    return True
```
*Verbs describe actions*

❌ **Bad Examples:**

```python
def customer(data):  # Noun, not verb
    pass

def page():  # What does it do?
    pass
```
*Nouns don't describe actions*

---
