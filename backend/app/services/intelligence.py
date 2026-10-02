from decimal import Decimal, ROUND_HALF_UP
from app.core.config import settings

def money(value): return Decimal(str(value)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)

def calculate_line(price,quantity,tax_percent,discount):
    base=money(Decimal(price)*Decimal(quantity)); discount=money(discount)
    if discount >= base: raise ValueError('Discount must be less than line subtotal')
    tax=money((base-discount)*Decimal(tax_percent)/100)
    return {'subtotal':base,'discount':discount,'tax':tax,'total':money(base-discount+tax)}

