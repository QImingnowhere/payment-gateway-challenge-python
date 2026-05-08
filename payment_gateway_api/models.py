from enum import Enum
from pydantic import BaseModel, field_validator
from datetime import datetime
import uuid

VALID_CURRENCIES = {"USD", "EUR", "CNY"}

class PaymentStatus(str, Enum):
    AUTHORIZED = "Authorized"
    DECLINED = "Declined"
    REJECTED = "Rejected"

class PaymentRequest(BaseModel):
    amount: int
    currency: str
    card_number: str
    expiry_month: int
    expiry_year: int
    cvv: str

    @field_validator('card_number')
    def validate_card_number(cls, v):
        if not v.isdigit():
            raise ValueError('Card number must contain only numeric characters')
        if not (14 <= len(v) <= 19):
            raise ValueError('Card number must be between 14 and 19 digits')
        return v

    @field_validator('expiry_month')
    def validate_expiry_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Expiry month must be between 1 and 12')
        return v

    @field_validator('expiry_year')
    def validate_expiry_year(cls, v):
        if v < datetime.now().year:
            raise ValueError('Expiry year must be in the future')
        return v
    
    @field_validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError('Currency must be a 3-letter code')
        if v.upper() not in VALID_CURRENCIES:
            raise ValueError(f'Currency must be one of {VALID_CURRENCIES}')
        return v.upper()

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be a positive integer')
        return v

    @field_validator('cvv')
    def validate_cvv(cls, v):
        if not v.isdigit():
            raise ValueError('CVV must contain only numeric characters')
        if not (3 <= len(v) <= 4):
            raise ValueError('CVV must be 3 or 4 digits')
        return v
    
    def is_expiry_in_future(self) -> bool:
        now = datetime.now()
        return (self.expiry_year > now.year) or (self.expiry_year == now.year and self.expiry_month >= now.month)
    
class PaymentResponse(BaseModel):
    id: str
    status: PaymentStatus
    card_number_last_four: str
    expiry_month: int
    expiry_year: int
    currency: str
    amount: int

class Payment(BaseModel):
    id: str
    status: PaymentStatus
    card_number_last_four: str
    expiry_month: int
    expiry_year: int
    currency: str
    amount: int

    @staticmethod
    def create(request: PaymentRequest, status: PaymentStatus) -> 'Payment':
        return Payment(
            id=str(uuid.uuid4()),
            status=status,
            card_number_last_four=request.card_number[-4:],
            expiry_month=request.expiry_month,
            expiry_year=request.expiry_year,
            currency=request.currency,
            amount=request.amount
        )