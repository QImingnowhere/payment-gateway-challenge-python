# Instructions for candidates

This is the Python version of the Payment Gateway challenge. If you haven't already read the [README.md](https://github.com/cko-recruitment) in the root of this organisation, please do so now. 

## Template structure
```
├── .editorconfig - don't change this. It ensures a consistent set of rules for submissions when reformatting code
├── .env.example
├── .python-version - Python version used by Pyenv (https://github.com/pyenv/pyenv).
├── Makefile - Makefile with commands such as install, run and test
├── docker-compose.yml - configures the bank simulator
├── pyproject.toml - project metadata, build system and dependencies
├── poetry.lock - Poetry lock file
├── main.py - app's entrypoint
├── payment_gateway_api/ - skeleton FastAPI API
├── imposters/ - contains the bank simulator configuration. Don't change this
└── tests/ - folder for tests
```

Feel free to change the structure of the solution, use a different test library etc.

---

# Payment Gateway API

A simple payment gateway built with FastAPI that processes card payments through a simulated acquiring bank.

The gateway:
- validates payment requests
- forwards valid requests to the bank
- stores processed payments
- allows merchants to retrieve payment details later

---

# Tech Stack

- Python 3.14
- FastAPI
- Pydantic
- httpx
- Pytest
- Docker

---

# Project Structure

```text
├── main.py
├── payment_gateway_api/
│   ├── app.py
│   ├── models.py
│   ├── bank_client.py
│   └── storage.py
├── tests/
│   └── test_payments.py
├── imposters/
│   └── bank_simulator.ejs
├── docker-compose.yml
└── pyproject.toml
```

---

# Setup Instructions (Windows PowerShell)

## 1. Install dependencies

```powershell
poetry install
```

---

## 2. Start the bank simulator

```powershell
docker-compose up -d
```

The simulator runs on:

```text
http://localhost:8080
```

---

## 3. Verify the bank simulator

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8080/payments" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "card_number":"2222405343248877",
    "expiry_date":"04/2030",
    "currency":"GBP",
    "amount":100,
    "cvv":"123"
  }'
```

Expected response:

```json
{
  "authorized": true,
  "authorization_code": "..."
}
```

---

## 4. Start the payment gateway API

```powershell
poetry run python main.py
```

The API runs on:

```text
http://localhost:8000
```

---

# API Usage

## Process a payment

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/payments" `
  -Method POST `
  -ContentType "application/json" `
  -Body @'
{
  "card_number": "2222405343248877",
  "expiry_month": 4,
  "expiry_year": 2030,
  "currency": "USD",
  "amount": 100,
  "cvv": "123"
}
'@
```

Example response:

```json
{
  "id": "uuid",
  "status": "Authorized",
  "card_number_last_four": "8877",
  "expiry_month": 4,
  "expiry_year": 2030,
  "currency": "USD",
  "amount": 100
}
```

---

## Retrieve a payment

```powershell
curl.exe "http://localhost:8000/payments/<payment-id>"
```

---

# Running Tests

```powershell
poetry run pytest tests/ -v
```

Tests do not require Docker because bank responses are mocked.

---

# Design Considerations

## Validation-first design

Input validation is performed before calling the bank.

Invalid requests return:

```text
HTTP 422 Unprocessable Entity
```

without sending unnecessary external requests.

---

## Secure card handling

Only the last 4 digits of the card are stored and returned.

Full card numbers are never persisted.

---

## Async architecture

The project uses:

- FastAPI async routes
- httpx async client

This allows non-blocking communication with the bank simulator.

---

## Error handling

If the bank is unavailable or returns an unexpected response:

```text
HTTP 502 Bad Gateway
```

is returned to the merchant.

---

## Storage

For simplicity, payments are stored in-memory using a Python dictionary.

No database is required for this exercise.

---

# Assumptions

- Supported currencies are limited to USD, CNY, and EUR
- Amounts use minor currency units
- Payment IDs are UUIDs
- Authentication is out of scope
- Storage is non-persistent

A simple payment gateway built with FastAPI that processes card payments through a simulated acquiring bank.

The gateway:
- validates payment requests
- forwards valid requests to the bank
- stores processed payments
- allows merchants to retrieve payment details later

---

# Tech Stack

- Python 3.11
- FastAPI
- Pydantic
- httpx
- Pytest
- Docker / Mountebank (bank simulator)

---

# Project Structure

```text
├── main.py
├── payment_gateway_api/
│   ├── app.py
│   ├── models.py
│   ├── bank_client.py
│   └── storage.py
├── tests/
│   └── test_payments.py
├── imposters/
│   └── bank_simulator.ejs
├── docker-compose.yml
└── pyproject.toml
```