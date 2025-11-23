from typing import Optional, List, Dict, Any
from decimal import Decimal
from msgspec import Struct

class Amount(Struct):
    value: float
    currency: str

class PaymentMethodData(Struct):
    type: str
    payment_data: Optional[Dict[str, Any]] = None

class Confirmation(Struct):
    type: str
    locale: Optional[str] = None
    return_url: Optional[str] = None

class MarkCodeInfo(Struct):
    mark_code_raw: Optional[str] = None
    unknown: Optional[str] = None
    ean_8: Optional[str] = None
    ean_13: Optional[str] = None
    itf_14: Optional[str] = None
    gs_10: Optional[str] = None
    gs_1m: Optional[str] = None
    short: Optional[str] = None
    fur: Optional[str] = None
    egais_20: Optional[str] = None
    egais_30: Optional[str] = None

class MarkQuantity(Struct):
    numerator: int
    denominator: int

class PaymentItem(Struct):
    description: str
    amount: Amount
    vat_code: int
    quantity: Decimal
    measure: Optional[str] = None
    mark_quantity: Optional[MarkQuantity] = None
    payment_subject: Optional[str] = None
    payment_mode: Optional[str] = None
    country_of_origin_code: Optional[str] = None
    customs_declaration_number: Optional[str] = None
    excise: Optional[str] = None
    product_code: Optional[str] = None
    mark_code_info: Optional[MarkCodeInfo] = None
    mark_mode: Optional[str] = None

class Customer(Struct):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    inn: Optional[str] = None

class Receipt(Struct):
    customer: Customer
    items: List[PaymentItem]
    tax_system_code: Optional[int] = None

class Recipient(Struct):
    account_id: str
    gateway_id: str

class Transfer(Struct):
    account_id: str
    amount: Amount
    platform_fee_amount: Optional[Amount] = None
    description: Optional[str] = None

class CreatePayment(Struct):
    amount: Amount
    description: Optional[str] = None
    receipt: Optional[Receipt] = None
    recipient: Optional[Recipient] = None
    payment_token: Optional[str] = None
    payment_method_id: Optional[str] = None
    payment_method_data: Optional[PaymentMethodData] = None
    confirmation: Optional[Confirmation] = None
    save_payment_method: Optional[bool] = None
    capture: Optional[bool] = None
    client_ip: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    transfers: Optional[List[Transfer]] = None
    deal: Optional[Dict[str, Any]] = None
    merchant_customer_id: Optional[str] = None
