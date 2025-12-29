# STS E-Commerce Application

## Architecture

This is a multi-layered e-commerce application with the following structure:

### Layers

**API Layer (`src/api/`)**
- Handles HTTP requests and responses
- REST endpoints for users, products, orders
- Authentication and authorization

**Business Logic Layer (`src/business/`)**
- Payment processing (Stripe, PayPal, Square)
- Inventory management
- Pricing calculations
- Shipping integration

**Data Layer (`src/data/`)**
- Database operations
- Caching
- Data models
- Repositories

**Utilities (`src/utils/`)**
- Helper functions
- Validators
- Formatters

### Database Schema

```
users
- id (PRIMARY KEY)
- username
- email
- password
- tier (standard, silver, gold, premium)

products
- id (PRIMARY KEY)
- name
- price
- stock
- category_id

orders
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- total
- status
```

### API Endpoints

**Authentication:**
- POST /api/auth/login
- POST /api/auth/register

**Users:**
- GET /api/users
- POST /api/users
- GET /api/users/{id}

**Products:**
- GET /api/products
- POST /api/products

**Orders:**
- POST /api/orders
- GET /api/orders/{id}

---

**Note:** This documentation is intentionally incomplete and may not match the actual implementation (DOC-02: Contradicts actual code).
