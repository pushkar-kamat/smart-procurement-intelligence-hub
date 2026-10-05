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
    available_weight=0
    weighted_points=0
    for name,(n,d) in pairs.items():
        den=facts.get(d,0) or 0; num=facts.get(n,0) or 0
        rate=min(1,num/den) if den else None
        contribution=round(rate*WEIGHTS[name],2) if rate is not None else None
        if rate is not None:
            available_weight+=WEIGHTS[name]
            weighted_points+=contribution
        factors.append({'factor':name,'numerator':num,'denominator':den,'rate_percent':round(rate*100,2) if rate is not None else None,'weight':WEIGHTS[name],'contribution':contribution})
    total_orders=facts.get('total_orders',0) or 0
    completed_orders=facts.get('completed_orders',0) or 0
    if total_orders<3:
        return {
            'score':None,'band':'NEW_VENDOR','history_status':'PROVISIONAL','coverage_percent':round(available_weight,2),
            'total_orders':total_orders,'completed_orders':completed_orders,'factors':factors,
            'reason':'New supplier with fewer than 3 historical orders. No risk penalty is applied; procurement should use quotation quality and verification evidence until performance history develops.'
        }
    if not available_weight:
        return {
            'score':None,'band':'HISTORY_UNAVAILABLE','history_status':'REVIEW_REQUIRED','coverage_percent':0,
            'total_orders':total_orders,'completed_orders':completed_orders,'factors':factors,
            'reason':'Historical orders exist, but no measurable risk factors are available. Manual review is required.'
        }
    # Normalize across the factors for which evidence exists so established vendors are not
    # marked "insufficient" just because one denominator (for example invoiced orders) is empty.
    score=round(weighted_points/available_weight*100,2)
    band='Low' if score<=settings.risk_low else 'Medium' if score<=settings.risk_medium else 'High'
    coverage=round(available_weight,2)
    observed=[f for f in factors if f['rate_percent'] is not None]
    explanation='; '.join(f"{f['factor'].replace('_',' ')}: {f['rate_percent']}% × {f['weight']}% = {f['contribution']} points" for f in observed)
    return {
        'score':score,'band':band,'history_status':'ESTABLISHED','coverage_percent':coverage,
        'total_orders':total_orders,'completed_orders':completed_orders,'factors':factors,
        'reason':explanation+f'. Evidence coverage: {coverage:g}% of weighted factors. Human approval remains required.'
    }

def invoice_mismatch(amount,total):
    deviation=abs(float(amount)-float(total))/float(total)*100
    return deviation>settings.mismatch_threshold, f'Invoice differs from PO by {deviation:.2f}%; configured tolerance {settings.mismatch_threshold:g}%.'
