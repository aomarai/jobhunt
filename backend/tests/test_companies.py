import uuid


def test_create_company(client, api_login):
    company_name = "Fake company"
    company_site = "www.fakecompany.com"
    company_notes = "Not existing is their specialty"
    auth_token = api_login
    response = client.post(
        "/companies",
        json={
            "name": company_name,
            "website": company_site,
            "notes": company_notes
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "website" in data
    assert "notes" in data
    assert data["name"] == company_name
    assert data["website"] == company_site
    assert data["notes"] == company_notes


def test_create_company_fails_without_login(client):
    company_name = "Fake company"
    company_site = "www.fakecompany.com"
    company_notes = "Not existing is their specialty"
    response = client.post(
        "/companies",
        json={
            "name": company_name,
            "website": company_site,
            "notes": company_notes
        }
    )
    assert response.status_code == 401


def test_list_companies(client, api_login, create_company):
    create_company(
        name="Acme Corp",
        website="https://acme.com",
        notes="Anvil manufacturer"
    )
    
    auth_token = api_login
    response = client.get(
        "/companies",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    acme_corp = data[0]
    assert "id" in acme_corp
    assert "name" in acme_corp
    assert "website" in acme_corp
    assert "notes" in acme_corp


def test_list_companies_fails_without_login(client, create_company):
    create_company(
        name="Acme Corp",
        website="https://acme.com",
        notes="Anvil manufacturer"
    )
    response = client.get(
        "/companies",
    )
    assert response.status_code == 401


def test_get_specific_company(client, api_login, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    auth_token = api_login
    response = client.get(
        f"/companies/{company_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "website" in data
    assert "notes" in data
    assert data["id"] == company_id
    assert data["name"] == company_name
    assert data["website"] == company_site
    assert data["notes"] == company_notes


def test_get_specific_commpany_fails_without_login(client, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    response = client.get(
        f"/companies/{company_id}",
    )
    assert response.status_code == 401


def test_update_company(client, api_login, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    auth_token = api_login
    new_company_name = "Burnt Ends Brewing Co"
    response = client.patch(
        f"/companies/{company_id}",
        json={
            "name": new_company_name,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_company_name
    assert data["website"] == company_site
    assert data["notes"] == company_notes


def test_update_company_fails_without_login(client, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    new_company_name = "Burnt Ends Brewing Co"
    response = client.patch(
        f"/companies/{company_id}",
        json={
            "name": new_company_name,
        },
    )
    assert response.status_code == 401


def test_delete_company(client, api_login, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    auth_token = api_login
    response = client.delete(
        f"/companies/{company_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204
    response = client.get(
        f"/companies/{company_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_company_fails_without_login(client, create_company):
    company_name = str(uuid.uuid4())
    company_site = f"https://{company_name}.com"
    company_notes = f"I love {company_name}"
    company_id = create_company(
        name=company_name,
        website=company_site,
        notes=company_notes
    )["id"]
    response = client.delete(
        f"/companies/{company_id}",
    )
    assert response.status_code == 401