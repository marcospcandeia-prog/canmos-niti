

class TestAuthRegister:
    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "nome": "Novo Usuario",
            "cpf": "52998224725",
            "email": "novo@email.com",
            "senha": "senha123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["user"]["nome"] == "Novo Usuario"
        assert data["user"]["email"] == "novo@email.com"
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_duplicate_email(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]

    def test_register_invalid_cpf(self, client):
        response = client.post("/auth/register", json={
            "nome": "Invalido",
            "cpf": "00000000000",
            "email": "invalido@email.com",
            "senha": "senha123",
        })
        assert response.status_code == 400
        assert "CPF inválido" in response.json()["detail"]

    def test_register_weak_password(self, client):
        response = client.post("/auth/register", json={
            "nome": "Fraco",
            "cpf": "52998224725",
            "email": "fraco@email.com",
            "senha": "123",
        })
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "senha": test_user_data["senha"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_wrong_password(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "senha": "senha_errada",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/auth/login", json={
            "email": "naoexiste@email.com",
            "senha": "senha123",
        })
        assert response.status_code == 401


class TestAuthRefresh:
    def test_refresh_success(self, client, test_user_data):
        register_resp = client.post("/auth/register", json=test_user_data)
        refresh_token = register_resp.json()["refresh_token"]

        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client):
        response = client.post("/auth/refresh", json={
            "refresh_token": "token_invalido",
        })
        assert response.status_code == 401


class TestAuthLogout:
    def test_logout_success(self, client, auth_headers):
        response = client.post("/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logout realizado com sucesso"

    def test_logout_unauthenticated(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 401


class TestUserProfile:
    def test_get_me(self, client, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "teste@email.com"
        assert "profile" in data

    def test_get_me_unauthenticated(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_update_profile(self, client, auth_headers):
        response = client.put("/auth/profile", headers=auth_headers, json={
            "profissao": "Engenheiro",
            "estado_civil": "casado",
            "possui_dependentes": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["profissao"] == "Engenheiro"
        assert data["estado_civil"] == "casado"
        assert data["possui_dependentes"] == "sim"

    def test_profile_persists(self, client, auth_headers):
        client.put("/auth/profile", headers=auth_headers, json={
            "profissao": "Advogado",
        })
        response = client.get("/auth/me", headers=auth_headers)
        assert response.json()["profile"]["profissao"] == "Advogado"


class TestAuditLogs:
    def test_audit_logs_after_login(self, client, auth_headers):
        response = client.get("/audit", headers=auth_headers)
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) >= 2
        actions = [log["action"] for log in logs]
        assert "register" in actions
        assert "login" in actions

    def test_audit_logs_unauthenticated(self, client):
        response = client.get("/audit")
        assert response.status_code == 401
