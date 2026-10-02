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

WEIGHTS={'late_delivery':30,'quotation_anomaly':25,'disputed_order':20,'incomplete_order':15,'invoice_mismatch':10}
def vendor_risk(facts):
    pairs={'late_delivery':('late_deliveries','completed_orders'),'quotation_anomaly':('anomalous_lines','quotation_lines'),'disputed_order':('disputed_orders','total_orders'),'incomplete_order':('incomplete_orders','total_orders'),'invoice_mismatch':('invoice_mismatches','invoiced_orders')}
    factors=[]
    for name,(n,d) in pairs.items():
        den=facts.get(d,0); num=facts.get(n,0)
        rate=min(1,num/den) if den else None
        factors.append({'factor':name,'numerator':num,'denominator':den,'rate_percent':round(rate*100,2) if rate is not None else None,'weight':WEIGHTS[name],'contribution':round(rate*WEIGHTS[name],2) if rate is not None else None})
    if facts.get('total_orders',0)<3 or any(f['rate_percent'] is None for f in factors):
        return {'score':None,'band':'INSUFFICIENT_HISTORY','factors':factors,'reason':'Insufficient completed history for all five factors; review the available evidence manually.'}
    score=round(sum(x['contribution'] for x in factors),2)
    band='Low' if score<=settings.risk_low else 'Medium' if score<=settings.risk_medium else 'High'
    return {'score':score,'band':band,'factors':factors,'reason':'; '.join(f"{f['factor'].replace('_',' ')}: {f['rate_percent']}% × {f['weight']}% = {f['contribution']} points" for f in factors)+'. Human approval required.'}

