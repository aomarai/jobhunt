import uuid


def _make_application(client, api_login, create_company, create_application):
    company_id = create_company(name="Acme Corp")["id"]
    return create_application(
        company_id=company_id,
        job_id="REQ-1234",
        job_title="Backend Engineer",
        job_url="https://acme.com/careers/1234",
        status="applied",
        notes=None,
    )["id"]


def test_create_contact(client, api_login, create_company, create_application):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    response = client.post(
        f"/applications/{application_id}/contacts",
        json={
            "name": "Jane Recruiter",
            "role": "Technical Recruiter",
            "email": "jane@acme.com",
            "linkedin_url": "https://linkedin.com/in/janerecruiter",
            "notes": "Very responsive",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["application_id"] == application_id
    assert "company_id" in data
    assert data["name"] == "Jane Recruiter"
    assert data["role"] == "Technical Recruiter"


def test_create_contact_derives_company_id_from_application(
    client, api_login, create_company, create_application
):
    company_id = create_company(name="Acme Corp")["id"]
    application_id = create_application(
        company_id=company_id,
        job_id="REQ-1234",
        job_title="Backend Engineer",
        job_url="https://acme.com/careers/1234",
        status="applied",
        notes=None,
    )["id"]
    auth_token = api_login

    response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company_id"] == company_id


def test_create_contact_fails_without_login(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)

    response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
    )
    assert response.status_code == 401


def test_create_contact_fails_for_nonexistent_application(client, api_login):
    auth_token = api_login
    fake_id = str(uuid.uuid4())

    response = client.post(
        f"/applications/{fake_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_create_contact_fails_for_other_users_application(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post("/auth/register", json={"email": second_email, "password": second_password})
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403


def test_list_contacts(client, api_login, create_company, create_application):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    response = client.get(
        f"/applications/{application_id}/contacts",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Jane Recruiter"


def test_list_contacts_fails_without_login(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)

    response = client.get(f"/applications/{application_id}/contacts")
    assert response.status_code == 401


def test_get_specific_contact(client, api_login, create_company, create_application):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter", "email": "jane@acme.com"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.get(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id
    assert data["email"] == "jane@acme.com"


def test_get_specific_contact_fails_without_login(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 401


def test_get_specific_contact_fails_for_nonexistent_id(client, api_login):
    auth_token = api_login
    fake_id = str(uuid.uuid4())

    response = client.get(
        f"/contacts/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_get_specific_contact_fails_for_other_users_contact(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post("/auth/register", json={"email": second_email, "password": second_password})
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.get(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403


def test_update_contact(client, api_login, create_company, create_application):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.patch(
        f"/contacts/{contact_id}",
        json={"role": "Engineering Manager"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "Engineering Manager"
    assert data["name"] == "Jane Recruiter"  # untouched field preserved


def test_update_contact_fails_without_login(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.patch(
        f"/contacts/{contact_id}",
        json={"role": "Engineering Manager"},
    )
    assert response.status_code == 401


def test_update_contact_fails_for_other_users_contact(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post("/auth/register", json={"email": second_email, "password": second_password})
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.patch(
        f"/contacts/{contact_id}",
        json={"role": "Engineering Manager"},
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403


def test_delete_contact(client, api_login, create_company, create_application):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    response = client.get(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_contact_fails_without_login(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 401


def test_delete_contact_fails_for_other_users_contact(
    client, api_login, create_company, create_application
):
    application_id = _make_application(client, api_login, create_company, create_application)
    auth_token = api_login

    create_response = client.post(
        f"/applications/{application_id}/contacts",
        json={"name": "Jane Recruiter"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    contact_id = create_response.json()["id"]

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post("/auth/register", json={"email": second_email, "password": second_password})
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403