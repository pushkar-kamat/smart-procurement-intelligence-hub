from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
Money=Annotated[Decimal,Field(gt=0,le=10000000,max_digits=12,decimal_places=2)]
Quantity=Annotated[Decimal,Field(gt=0,le=10000,max_digits=12,decimal_places=3)]
Text=Annotated[str,Field(min_length=1,max_length=120)]
class Contract(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True,allow_inf_nan=False)
class ItemIn(Contract):
    item_name:Text
    category:Annotated[str,Field(min_length=1,max_length=80)]
    description:str=Field(default='',max_length=500)
    quantity:Quantity
    unit:str=Field(min_length=1,max_length=30)
    estimated_unit_price:Money
class RequisitionIn(Contract):
    title:str=Field(min_length=3,max_length=180)
    justification:str=Field(min_length=5,max_length=2000)
    department_id:int=Field(gt=0)
    items:list[ItemIn]=Field(min_length=1,max_length=50)
class VendorIn(Contract):
    name:Text
    email:str=Field(min_length=3,max_length=254,pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    contact:str=Field(default='',max_length=80)
    active:bool=True
class InviteIn(Contract):
    vendor_id:int=Field(gt=0)
class QuoteLineIn(Contract):
    requisition_item_id:int=Field(gt=0)
    unit_price:Money
    tax_percent:Decimal=Field(default=0,ge=0,le=100,decimal_places=2)
    discount:Decimal=Field(default=0,ge=0,le=1000000000,decimal_places=2)
class QuoteIn(Contract):
    vendor_id:int=Field(gt=0)
    quotation_number:str=Field(min_length=1,max_length=80)
    quotation_date:date
    valid_until:date|None=None
    delivery_days:int=Field(ge=0,le=3650)
    delivery_terms:str=Field(default='',max_length=500)
    items:list[QuoteLineIn]=Field(min_length=1,max_length=50)
    @model_validator(mode='after')
    def dates(self):
        if self.valid_until and self.valid_until < self.quotation_date: raise ValueError('Validity cannot precede quotation date')
        if self.quotation_date > date.today(): raise ValueError('Quotation date cannot be in the future')
        return self
class VendorQuoteIn(Contract):
    quotation_number:str=Field(min_length=1,max_length=80)
    quotation_date:date
    valid_until:date|None=None
    delivery_days:int=Field(ge=0,le=3650)
    delivery_terms:str=Field(default='',max_length=500)
    items:list[QuoteLineIn]=Field(min_length=1,max_length=50)
    @model_validator(mode='after')
    def dates(self):
        if self.valid_until and self.valid_until < self.quotation_date: raise ValueError('Validity cannot precede quotation date')
        if self.quotation_date > date.today(): raise ValueError('Quotation date cannot be in the future')
        return self
class SelectionIn(Contract):
    vendor_id:int=Field(gt=0)
    comment:str=Field(min_length=5,max_length=2000)
class DecisionIn(Contract):
    decision:Literal['APPROVED','REJECTED']
    comment:str=Field(min_length=5,max_length=2000)
class DeliveryIn(Contract):
    status:Literal['PARTIAL','DELIVERED']
    delivered_at:date
    expected_completion_at:date|None=None
    notes:str=Field(min_length=3,max_length=2000)
    @model_validator(mode='after')
    def dates(self):
        if self.delivered_at > date.today(): raise ValueError('Delivery receipt date cannot be in the future')
        if self.status=='PARTIAL' and self.expected_completion_at and self.expected_completion_at < self.delivered_at:
            raise ValueError('Expected completion cannot precede the partial receipt date')
        if self.status=='DELIVERED': self.expected_completion_at=None
        return self
class InvoiceIn(Contract):
    invoice_number:str=Field(min_length=1,max_length=80)
    invoice_date:date
    amount:Money
    @model_validator(mode='after')
    def dates(self):
        if self.invoice_date > date.today(): raise ValueError('Invoice cannot be in the future')
        return self
class CommentIn(Contract):
    comment:str=Field(min_length=5,max_length=2000)
class ProfileUpdate(Contract):
    role:Literal['requester','procurement','approver','finance_admin','vendor']
    active:bool
    department_id:int|None=None
