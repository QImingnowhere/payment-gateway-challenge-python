from typing import Dict, Optional
from payment_gateway_api.models import Payment

class PaymentRepository:
    def __init__(self):
        self.payments: Dict[str, Payment] = {}

    def save_payment(self, payment: Payment) -> None:
        self.payments[payment.id] = payment

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self.payments.get(payment_id)