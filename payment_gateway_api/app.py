from typing import Dict
from fastapi import FastAPI, HTTPException

from payment_gateway_api.models import (
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    Payment
)
from payment_gateway_api.bank_client import BankClient
from payment_gateway_api.storage import PaymentRepository

app = FastAPI()
repository = PaymentRepository()
bank_client = BankClient("http://localhost:8080")

@app.get("/")
async def ping() -> Dict[str, str]:
    return {"app": "payment-gateway-api"}

@app.post('/payments', status_code=200)
async def process_payment(request: PaymentRequest) -> PaymentResponse:
    if not request.is_expiry_in_future():
        raise HTTPException(status_code=400, detail="Card has expired")

    bank_response = await bank_client.process_payment(request)
    if bank_response is None:
        raise HTTPException(status_code=502, detail="Failed to process payment with the bank")
    
    status = PaymentStatus.AUTHORIZED if bank_response.authorized else PaymentStatus.DECLINED
    payment = Payment.create(request, status)
    repository.save_payment(payment)

    return PaymentResponse(
        id=payment.id,
        status=payment.status,
        card_number_last_four=payment.card_number_last_four,
        expiry_month=payment.expiry_month,
        expiry_year=payment.expiry_year,
        currency=payment.currency,
        amount=payment.amount
    )

@app.get('/payments/{payment_id}', response_model=PaymentResponse)
async def get_payment(payment_id: str) -> PaymentResponse:
    payment = repository.get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return PaymentResponse(
        id=payment.id,
        status=payment.status,
        card_number_last_four=payment.card_number_last_four,
        expiry_month=payment.expiry_month,
        expiry_year=payment.expiry_year,
        currency=payment.currency,
        amount=payment.amount
    )