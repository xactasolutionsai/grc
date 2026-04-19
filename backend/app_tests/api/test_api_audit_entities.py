import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from audits.models import AuditEntity

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def audit_entity_data():
    return {
        "name": "Test HR Department",
        "entity_type": "business_unit",
        "description": "Human Resources Department",
        "country": "United States",
        "region": "California",
        "city": "San Francisco",
        "address": "123 Main St, San Francisco, CA 94105",
        "postal_code": "94105",
        "timezone": "America/Los_Angeles",
        "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
        "criticality": "High",
        "audit_frequency": "annual",
        "is_active": True,
    }


@pytest.fixture
def audit_entity_with_location(user, audit_entity_data):
    return AuditEntity.objects.create(
        name=audit_entity_data["name"],
        entity_type=audit_entity_data["entity_type"],
        description=audit_entity_data["description"],
        country=audit_entity_data["country"],
        region=audit_entity_data["region"],
        city=audit_entity_data["city"],
        address=audit_entity_data["address"],
        postal_code=audit_entity_data["postal_code"],
        timezone=audit_entity_data["timezone"],
        coordinates=audit_entity_data["coordinates"],
        criticality=audit_entity_data["criticality"],
        audit_frequency=audit_entity_data["audit_frequency"],
        is_active=audit_entity_data["is_active"],
        owner=user,
    )


class TestAuditEntityGeographicalLocation:
    """Test geographical location functionality for AuditEntity."""

    @pytest.mark.django_db
    def test_create_audit_entity_with_geographical_data(
        self, api_client, user, audit_entity_data
    ):
        """Test creating an audit entity with geographical location data."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        response = api_client.post(url, audit_entity_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check geographical fields are saved correctly
        assert data["country"] == audit_entity_data["country"]
        assert data["region"] == audit_entity_data["region"]
        assert data["city"] == audit_entity_data["city"]
        assert data["address"] == audit_entity_data["address"]
        assert data["postal_code"] == audit_entity_data["postal_code"]
        assert data["timezone"] == audit_entity_data["timezone"]
        assert data["coordinates"] == audit_entity_data["coordinates"]

        # Check computed fields
        assert "full_location" in data
        assert data["full_location"] == "San Francisco, California, United States"

    @pytest.mark.django_db
    def test_get_audit_entity_with_geographical_data(
        self, api_client, user, audit_entity_with_location
    ):
        """Test retrieving an audit entity with geographical location data."""
        api_client.force_authenticate(user=user)
        url = reverse(
            "auditentity-detail", kwargs={"pk": audit_entity_with_location.pk}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check geographical fields are returned
        assert data["country"] == "United States"
        assert data["region"] == "California"
        assert data["city"] == "San Francisco"
        assert data["address"] == "123 Main St, San Francisco, CA 94105"
        assert data["postal_code"] == "94105"
        assert data["timezone"] == "America/Los_Angeles"
        assert data["coordinates"]["latitude"] == 37.7749
        assert data["coordinates"]["longitude"] == -122.4194

        # Check computed fields
        assert data["full_location"] == "San Francisco, California, United States"

    @pytest.mark.django_db
    def test_filter_audit_entities_by_country(
        self, api_client, user, audit_entity_with_location
    ):
        """Test filtering audit entities by country."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        response = api_client.get(url, {"country": "United States"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["country"] == "United States"

    @pytest.mark.django_db
    def test_filter_audit_entities_by_region(
        self, api_client, user, audit_entity_with_location
    ):
        """Test filtering audit entities by region."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        response = api_client.get(url, {"region": "California"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["region"] == "California"

    @pytest.mark.django_db
    def test_filter_audit_entities_by_city(
        self, api_client, user, audit_entity_with_location
    ):
        """Test filtering audit entities by city."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        response = api_client.get(url, {"city": "San Francisco"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["city"] == "San Francisco"

    @pytest.mark.django_db
    def test_search_audit_entities_by_geographical_fields(
        self, api_client, user, audit_entity_with_location
    ):
        """Test searching audit entities by geographical fields."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        # Search by country
        response = api_client.get(url, {"search": "United States"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1

        # Search by city
        response = api_client.get(url, {"search": "San Francisco"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1

        # Search by address
        response = api_client.get(url, {"search": "123 Main St"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1

    @pytest.mark.django_db
    def test_update_audit_entity_geographical_data(
        self, api_client, user, audit_entity_with_location
    ):
        """Test updating geographical data of an audit entity."""
        api_client.force_authenticate(user=user)
        url = reverse(
            "auditentity-detail", kwargs={"pk": audit_entity_with_location.pk}
        )

        update_data = {
            "country": "Canada",
            "region": "Ontario",
            "city": "Toronto",
            "address": "456 Queen St, Toronto, ON M5H 2M9",
            "postal_code": "M5H 2M9",
            "timezone": "America/Toronto",
            "coordinates": {"latitude": 43.6532, "longitude": -79.3832},
        }

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check updated geographical fields
        assert data["country"] == "Canada"
        assert data["region"] == "Ontario"
        assert data["city"] == "Toronto"
        assert data["address"] == "456 Queen St, Toronto, ON M5H 2M9"
        assert data["postal_code"] == "M5H 2M9"
        assert data["timezone"] == "America/Toronto"
        assert data["coordinates"]["latitude"] == 43.6532
        assert data["coordinates"]["longitude"] == -79.3832

        # Check computed fields
        assert data["full_location"] == "Toronto, Ontario, Canada"

    @pytest.mark.django_db
    def test_validate_coordinates(self, api_client, user):
        """Test coordinate validation."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        # Test invalid latitude
        invalid_data = {
            "name": "Test Entity",
            "entity_type": "business_unit",
            "coordinates": {
                "latitude": 91.0,  # Invalid latitude
                "longitude": -122.4194,
            },
        }

        response = api_client.post(url, invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "latitude" in str(response.data)

    @pytest.mark.django_db
    def test_validate_timezone(self, api_client, user):
        """Test timezone validation."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        # Test invalid timezone
        invalid_data = {
            "name": "Test Entity",
            "entity_type": "business_unit",
            "timezone": "Invalid/Timezone",
        }

        response = api_client.post(url, invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "timezone" in str(response.data)

    @pytest.mark.django_db
    def test_legacy_location_field_compatibility(self, api_client, user):
        """Test that legacy location field still works for backward compatibility."""
        api_client.force_authenticate(user=user)
        url = reverse("auditentity-list")

        data = {
            "name": "Test Entity",
            "entity_type": "business_unit",
            "location": "US, EU, APAC",  # Legacy field
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["location"] == "US, EU, APAC"
        assert (
            response_data["full_location"] == "US, EU, APAC"
        )  # Should fall back to legacy field
