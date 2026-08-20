from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_extract_endpoint():
    payload = {
        "id": "1001",
        "ticketPostedTime": "20.08.26 - 01:53",
        "messages": [
            {
                "sender": "customer",
                "text": "سلام مبلغ 1 میلیون تومان در تاریخ 1405/05/29 ساعت 12:30 از کارت 6037991786315824 به نام محمد سهرابی واریز کردم."
            }
        ]
    }
    response = client.post("/api/v1/extract", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["amount_toman"] == 1000000
    assert data["time"] == "12:30"
    assert data["date"] == "1405/05/29"
    assert data["source_card"] == "6037991786315824"
    assert data["gateway"] == "کارت‌به‌کارت"
