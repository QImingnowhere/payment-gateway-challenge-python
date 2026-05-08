import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from payment_gateway_api.app import app, bank_client, repository
from payment_gateway_api.bank_client import BankResponse

@pytest.fixture(autouse=True)
def clear_repository():
    repository.payments.clear()
    yield

@pytest.fixture
def valid_payment_request():
    return {
        "card_number": "4111111111111111",
        "expiry_month": 12,
        "expiry_year": 2030,
        "cvv": "123",
        "amount": 100,
        "currency": "USD"
    }

@pytest.mark.asyncio
async def test_process_payment_authorized(valid_payment_request):
    with patch.object(bank_client, 'process_payment', new_callable=AsyncMock) as mock_process_payment:
        mock_process_payment.return_value = BankResponse(authorized=True, authorization_code="abc-123")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/payments', json=valid_payment_request)

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'Authorized'
        assert data['card_number_last_four'] == '1111'
        assert data['expiry_month'] == valid_payment_request['expiry_month']
        assert data['expiry_year'] == valid_payment_request['expiry_year']
        assert data['currency'] == valid_payment_request['currency']
        assert "id" in data

@pytest.mark.asyncio
async def test_process_payment_declined(valid_payment_request):
    with patch.object(bank_client, 'process_payment', new_callable=AsyncMock) as mock_process_payment:
        mock_process_payment.return_value = BankResponse(authorized=False, authorization_code="")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/payments', json=valid_payment_request)

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'Declined'
        assert data['card_number_last_four'] == '1111'
        assert data['expiry_month'] == valid_payment_request['expiry_month']
        assert data['expiry_year'] == valid_payment_request['expiry_year']
        assert data['currency'] == valid_payment_request['currency']
        assert "id" in data

@pytest.mark.asyncio
@pytest.mark.parametrize("field, value, label", [
    ("card_number", "123", "Too short card number"),
    ("card_number", "12345678901234567890", "Too long card number"),
    ("card_number", "abecdefghijklmnop", "Card number must contain only numeric characters"),
    ("expiry_month", 0, "Expiry month smaller than minimum range 1"),
    ("expiry_month", 13, "Expiry month must be between 1 and 12"),
    ("expiry_year", 2000, "Expiry year must be in the future"),
    ("currency", "US", "Currency must be a 3-letter code"),
    ("currency", "XYZ", "Invalid currency code"),
    ("amount", -100, "Amount must be a positive integer"),
    ("amount", 0, "Zero amount is not allowed"),
    ("cvv", "12a", "CVV must contain only numeric characters"),
    ("cvv", "12", "CVV too few digits"),
    ("cvv", "12345", "CVV too many digits")
])
async def test_process_payment_invalid(valid_payment_request, field, value, label):
    valid_payment_request[field] = value
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post('/payments', json=valid_payment_request)

    assert response.status_code == 422, f"Expected validation error for {field}: {value} with label {label}"

@pytest.mark.asyncio
async def test_process_payment_bank_unavailable(valid_payment_request):
    with patch.object(bank_client, 'process_payment', new_callable=AsyncMock) as mock_process_payment:
        mock_process_payment.return_value = None

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post('/payments', json=valid_payment_request)

        assert response.status_code == 502
        data = response.json()
        assert data['detail'] == "Failed to process payment with the bank"

@pytest.mark.asyncio
async def test_get_payment_return_previous_payment(valid_payment_request):
    with patch.object(bank_client, 'process_payment', new_callable=AsyncMock) as mock_process_payment:
        mock_process_payment.return_value = BankResponse(authorized=True, authorization_code="abc-123")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            post_response = await client.post('/payments', json=valid_payment_request)
            payment_id = post_response.json()['id']
            get_response = await client.get(f'/payments/{payment_id}')

        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data['id'] == payment_id
        assert get_data['status'] == 'Authorized'
        assert get_data['card_number_last_four'] == '1111'
        assert get_data['expiry_month'] == valid_payment_request['expiry_month']
        assert get_data['expiry_year'] == valid_payment_request['expiry_year']
        assert get_data['currency'] == valid_payment_request['currency']
        assert get_data['amount'] == valid_payment_request['amount']

@pytest.mark.asyncio
async def test_get_payment_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get('/payments/non-existent-id')

    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == "Payment not found"
