from decimal import Decimal, ROUND_HALF_UP
from statistics import median, quantiles
from app.core.config import settings

def money(value): return Decimal(str(value)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)

def calculate_line(price,quantity,tax_percent,discount):
    base=money(Decimal(price)*Decimal(quantity)); discount=money(discount)
    if discount >= base: raise ValueError('Discount must be less than line subtotal')
    tax=money((base-discount)*Decimal(tax_percent)/100)
    return {'subtotal':base,'discount':discount,'tax':tax,'total':money(base-discount+tax)}

def analyze_price(price,history,threshold=None):
    threshold=settings.price_threshold if threshold is None else threshold
    values=[float(v) for v in history if v>0]
    result={'sample_count':len(values),'threshold_percent':threshold,'reference_median':None,'deviation_percent':None,'q1':None,'q3':None,'iqr':None,'upper_boundary':None,'anomaly_flag':False}
    if len(values)<3:
        return dict(result,status='INSUFFICIENT_HISTORY',reason='Fewer than 3 matching historical observations; human review required.')
    ref=median(values); deviation=(float(price)-ref)/ref*100
    result.update(reference_median=round(ref,2),deviation_percent=round(deviation,2))
    flagged=deviation>threshold; reasons=[]
    if flagged: reasons.append(f'exceeds configured {threshold:g}% above-median threshold')
    if len(values)>=5:
        q1,_,q3=quantiles(values,n=4,method='inclusive'); iqr=q3-q1; upper=q3+1.5*iqr
        result.update(q1=q1,q3=q3,iqr=iqr,upper_boundary=upper)
        if float(price)>upper:
            flagged=True; reasons.append(f'exceeds IQR upper boundary {upper:,.2f}')
    result.update(status='FLAGGED' if flagged else 'NORMAL',anomaly_flag=flagged,reason=f'Quoted INR {float(price):,.2f}; historical median INR {ref:,.2f}; {deviation:+.2f}%; '+('; '.join(reasons) if reasons else 'within evaluated boundaries')+'.')
    return result

