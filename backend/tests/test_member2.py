from app.services.intelligence import vendor_risk, invoice_mismatch

def test_member2_vendor_risk_high_band():
    facts={'total_orders':10,'completed_orders':10,'late_deliveries':9,'anomalous_lines':9,'quotation_lines':10,'disputed_orders':8,'incomplete_orders':7,'invoice_mismatches':8,'invoiced_orders':10}
    result=vendor_risk(facts)
    assert result['band']=='High'
    assert result['score'] is not None

def test_member2_invoice_mismatch():
    flag,reason=invoice_mismatch(110,100)
    assert flag is True
    assert '10.00%' in reason
