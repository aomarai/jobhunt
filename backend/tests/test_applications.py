import uuid


def test_create_application(client, api_login, create_company):
    company_id = create_company(
        name="Acme Corp"
        )["id"]
    auth_token = api_login

    response = client.post(
        "/applications",
        json={
            "company_id": company_id,
            "job_id": "REQ-1234",
            "job_title": "Backend Engineer",
            "job_url": "https://acme.com/careers/1234",
            "status": "applied",
            "notes": "Referred by a friend",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "applied_at" in data
    assert "updated_at" in data
    assert data["job_id"] == "REQ-1234"
    assert data["job_title"] == "Backend Engineer"
    assert data["job_url"] == "https://acme.com/careers/1234"
    assert data["notes"] == "Referred by a friend"


def test_create_application_fails_without_login(client, create_company, api_login):
    company_id = create_company(name="Acme Corp")["id"]

    response = client.post(
        "/applications",
        json={
            "company_id": company_id,
            "job_id": "REQ-1234",
            "job_title": "Backend Engineer",
            "job_url": "https://acme.com/careers/1234",
            "status": "applied",
            "notes": "Referred by a friend",
        },
    )
    assert response.status_code == 401


def test_create_application_fails_with_unknown_company(client, api_login):
    auth_token = api_login
    fake_company_id = str(uuid.uuid4())

    response = client.post(
        "/applications",
        json={
            "company_id": fake_company_id,
            "job_id": "REQ-1234",
            "job_title": "Backend Engineer",
            "job_url": "https://acme.com/careers/1234",
            "status": "applied",
            "notes": None,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_list_applications(client, api_login, create_company, create_application):
    company_id = create_company(name="Acme Corp")["id"]
    create_application(
        company_id=company_id,
        job_id="REQ-1234",
        job_title="Backend Engineer",
        job_url="https://acme.com/careers/1234",
        status="applied",
        notes=None,
    )

    auth_token = api_login
    response = client.get(
        "/applications",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    application = data[0]
    assert "id" in application
    assert "status" in application


def test_list_applications_fails_without_login(client):
    response = client.get("/applications")
    assert response.status_code == 401


def test_list_applications_only_returns_own_applications(
    client, api_login, create_company, create_application
):
    company_id = create_company(name="Acme Corp")["id"]
    create_application(
        company_id=company_id,
        job_id="REQ-1234",
        job_title="Backend Engineer",
        job_url="https://acme.com/careers/1234",
        status="applied",
        notes=None,
    )

    # A second, different user should see zero applications
    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post(
        "/auth/register",
        json={"email": second_email, "password": second_password},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.get(
        "/applications",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_specific_application(client, api_login, create_company, create_application):
    company_id = create_company(name="Acme Corp")["id"]
    application_id = create_application(
        company_id=company_id,
        job_id="REQ-1234",
        job_title="Backend Engineer",
        job_url="https://acme.com/careers/1234",
        status="applied",
        notes="Referred by a friend",
    )["id"]

    auth_token = api_login
    response = client.get(
        f"/applications/{application_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == application_id
    assert data["job_title"] == "Backend Engineer"


def test_get_specific_application_fails_without_login(
    client, create_company, create_application
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

    response = client.get(f"/applications/{application_id}")
    assert response.status_code == 401


def test_get_specific_application_fails_for_nonexistent_id(client, api_login):
    auth_token = api_login
    fake_id = str(uuid.uuid4())

    response = client.get(
        f"/applications/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_get_specific_application_fails_for_other_users_application(
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

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post(
        "/auth/register",
        json={"email": second_email, "password": second_password},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.get(
        f"/applications/{application_id}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403


def test_update_application(client, api_login, create_company, create_application):
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
    response = client.patch(
        f"/applications/{application_id}",
        json={"status": "interviewing"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Backend Engineer"  # untouched fields preserved


def test_update_application_fails_without_login(
    client, create_company, create_application
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

    response = client.patch(
        f"/applications/{application_id}",
        json={"status": "interviewing"},
    )
    assert response.status_code == 401


def test_update_application_fails_for_other_users_application(
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

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post(
        "/auth/register",
        json={"email": second_email, "password": second_password},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.patch(
        f"/applications/{application_id}",
        json={"status": "interviewing"},
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403


def test_delete_application(client, api_login, create_company, create_application):
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
    response = client.delete(
        f"/applications/{application_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    response = client.get(
        f"/applications/{application_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_application_fails_without_login(
    client, create_company, create_application
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

    response = client.delete(f"/applications/{application_id}")
    assert response.status_code == 401


def test_delete_application_fails_for_other_users_application(
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

    second_email = f"{uuid.uuid4()}@example.com"
    second_password = str(uuid.uuid4())
    client.post(
        "/auth/register",
        json={"email": second_email, "password": second_password},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": second_email, "password": second_password},
    )
    second_token = login_response.json()["access_token"]

    response = client.delete(
        f"/applications/{application_id}",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert response.status_code == 403