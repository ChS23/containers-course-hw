from datetime import datetime
from typing import Optional, List, Dict, Any
from msgspec import Struct
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"

class ReceiptRegistrationStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"

class Amount(Struct):
    value: str
    currency: str

class Recipient(Struct):
    account_id: str
    gateway_id: str

class CardProduct(Struct):
    code: str
    name: str

class Card(Struct, kw_only=True):
    first6: str
    last4: str
    expiry_month: str
    expiry_year: str
    card_type: str
    issuer_country: str
    issuer_name: str
    card_product: Optional[CardProduct] = None

class PaymentMethod(Struct):
    type: str
    id: str
    saved: bool
    card: Card
    title: str

class ThreeDSecure(Struct):
    applied: bool

class AuthorizationDetails(Struct):
    rrn: str
    auth_code: str
    three_d_secure: ThreeDSecure

class CancellationDetails(Struct):
    party: str
    reason: str

class Transfer(Struct):
    account_id: str
    amount: Amount
    status: str
    description: Optional[str] = None

class InvoiceDetails(Struct):
    id: str
    type: str

class Payment(Struct, kw_only=True):
    id: str
    status: PaymentStatus
    amount: Amount
    recipient: Recipient
    created_at: datetime
    paid: bool
    refundable: bool
    test: bool
    income_amount: Optional[Amount] = None
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    captured_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    confirmation: Optional[Dict[str, Any]] = None
    refunded_amount: Optional[Amount] = None
    receipt_registration: Optional[ReceiptRegistrationStatus] = None
    metadata: Optional[Dict[str, str]] = None
    cancellation_details: Optional[CancellationDetails] = None
    authorization_details: Optional[AuthorizationDetails] = None
    transfers: Optional[List[Transfer]] = None
    deal: Optional[Dict[str, Any]] = None
    merchant_customer_id: Optional[str] = None
    invoice_details: Optional[InvoiceDetails] = None
