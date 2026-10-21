from fastapi.testclient import TestClient
from agricast.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_capabilities_report_unimplemented_features_honestly():
    response = client.get("/v1/system/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert "yield_forecast" in body["features"]
    assert "calibrated_prediction_intervals" in body["not_available"]


def test_evidence_search_validates_query_length():
    assert client.get("/v1/evidence/search", params={"q": "x"}).status_code == 422
