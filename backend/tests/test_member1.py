from app.services.intelligence import analyze_price

def test_member1_price_anomaly_flag():
    result=analyze_price(150,[100,100,105,95,102],threshold=25)
    assert result['anomaly_flag'] is True
    assert result['status']=='FLAGGED'

def test_member1_insufficient_price_history():
    result=analyze_price(150,[100,105],threshold=25)
    assert result['status']=='INSUFFICIENT_HISTORY'
