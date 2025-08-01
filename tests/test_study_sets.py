import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.study_set import StudySet, Term
from app.core.security import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestStudySets:
    def test_create_study_set(self, test_db, auth_headers):
        """Test creating a new study set"""
        study_set_data = {
            "title": "Test Study Set",
            "description": "A test study set",
            "is_public": True,
            "language_from": "en",
            "language_to": "vi"
        }
        
        response = client.post("/api/v1/study-sets/", json=study_set_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == study_set_data["title"]
        assert data["description"] == study_set_data["description"]
        assert data["terms_count"] == 0
        assert data["views_count"] == 0

    def test_get_study_set(self, test_db, auth_headers, test_user):
        """Test getting a study set by ID"""
        # Create a study set first
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Test Study Set",
            description="A test study set",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        db.close()
        
        response = client.get(f"/api/v1/study-sets/{study_set.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Study Set"
        assert data["terms"] == []

    def test_update_study_set(self, test_db, auth_headers, test_user):
        """Test updating a study set"""
        # Create a study set first
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Original Title",
            description="Original description",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        db.close()
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/study-sets/{study_set.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"

    def test_delete_study_set(self, test_db, auth_headers, test_user):
        """Test deleting a study set"""
        # Create a study set first
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Test Study Set",
            description="A test study set",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        db.close()
        
        response = client.delete(f"/api/v1/study-sets/{study_set.id}", headers=auth_headers)
        
        assert response.status_code == 204

    def test_search_study_sets(self, test_db, auth_headers, test_user):
        """Test searching study sets"""
        # Create some study sets
        db = TestingSessionLocal()
        study_sets = [
            StudySet(title="English to Vietnamese", user_id=test_user.id, is_public=True),
            StudySet(title="Math Terms", user_id=test_user.id, is_public=True),
            StudySet(title="Science Vocabulary", user_id=test_user.id, is_public=True)
        ]
        for study_set in study_sets:
            db.add(study_set)
        db.commit()
        db.close()
        
        response = client.get("/api/v1/study-sets/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3


class TestTerms:
    def test_create_term(self, test_db, auth_headers, test_user):
        """Test creating a new term"""
        # Create a study set first
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Test Study Set",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        db.close()
        
        term_data = {
            "term": "Hello",
            "definition": "Xin chào",
            "image_url": None,
            "audio_url": None
        }
        
        response = client.post(f"/api/v1/study-sets/{study_set.id}/terms/", json=term_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["term"] == "Hello"
        assert data["definition"] == "Xin chào"
        assert data["position"] == 1

    def test_get_terms(self, test_db, auth_headers, test_user):
        """Test getting terms for a study set"""
        # Create a study set with terms
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Test Study Set",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        
        terms = [
            Term(term="Hello", definition="Xin chào", study_set_id=study_set.id, position=1),
            Term(term="Goodbye", definition="Tạm biệt", study_set_id=study_set.id, position=2)
        ]
        for term in terms:
            db.add(term)
        db.commit()
        db.close()
        
        response = client.get(f"/api/v1/study-sets/{study_set.id}/terms/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["term"] == "Hello"
        assert data[1]["term"] == "Goodbye"

    def test_bulk_create_terms(self, test_db, auth_headers, test_user):
        """Test creating multiple terms at once"""
        # Create a study set first
        db = TestingSessionLocal()
        study_set = StudySet(
            title="Test Study Set",
            user_id=test_user.id,
            is_public=True
        )
        db.add(study_set)
        db.commit()
        db.refresh(study_set)
        db.close()
        
        terms_data = {
            "terms": [
                {"term": "Hello", "definition": "Xin chào"},
                {"term": "Goodbye", "definition": "Tạm biệt"},
                {"term": "Thank you", "definition": "Cảm ơn"}
            ]
        }
        
        response = client.post(f"/api/v1/study-sets/{study_set.id}/terms/bulk", json=terms_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3
        assert data[0]["term"] == "Hello"
        assert data[1]["term"] == "Goodbye"
        assert data[2]["term"] == "Thank you" 