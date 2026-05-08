import httpx
from typing import Optional
from .models import PaymentRequest

class BankResponse:
    def __init__(self, authorized: bool, authorization_code: str):
        self.authorized = authorized
        self.authorization_code = authorization_code

class BankClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def process_payment(self, payment_request: PaymentRequest) -> Optional[BankResponse]:
        payload = {
            "card_number": payment_request.card_number,
            "expiry_date": f"{payment_request.expiry_month:02d}/{payment_request.expiry_year}",
            "cvv": payment_request.cvv,
            "amount": payment_request.amount,
            "currency": payment_request.currency
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/payments", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return BankResponse(
                        authorized=data.get("authorized", False),
                        authorization_code=data.get("authorization_code", "")
                    )
                return None
        except Exception as e:
            print(f"An error occurred while processing payment: {e}")
            return None
        
        