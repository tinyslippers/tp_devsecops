def test_home_page(client):
    """Vérifie que la page d'accueil s'affiche bien"""
    resp = client.get("/")
    assert resp.status_code == 200

def test_health_check(client):
    """Vérifie que l'API de santé répond"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"
