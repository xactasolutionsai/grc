"""
Tests for Asset ITAM (IT Asset Management) fields and API endpoints.
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Asset, Folder
from core.serializers import AssetWriteSerializer

User = get_user_model()


class AssetITAMAPITestCase(TestCase):
    """Test cases for Asset ITAM fields API functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a test folder
        self.folder = Folder.objects.create(
            name="Test Folder", description="Test folder for ITAM tests"
        )

        # Give user permission to access the folder
        from iam.models import Role, RoleAssignment
        from django.contrib.auth.models import Permission

        # Create or get the analyst role
        analyst_role, created = Role.objects.get_or_create(
            name="Analyst", defaults={"description": "Analyst role for testing"}
        )

        # Create role assignment
        role_assignment = RoleAssignment.objects.create(
            user=self.user, role=analyst_role
        )
        role_assignment.perimeter_folders.add(self.folder)

    def test_create_asset_with_itam_fields(self):
        """Test creating an asset with ITAM fields."""
        url = reverse("assets-list")
        data = {
            "name": "Test Laptop",
            "description": "Test laptop for ITAM testing",
            "folder": self.folder.id,
            "asset_type": "hardware",
            "specifications": "Intel i7, 16GB RAM, 512GB SSD",
            "serial_number": "SN123456789",
            "assigned_user": "john.doe@example.com",
            "department": "IT Department",
            "physical_location": "Building A, Floor 2, Room 201",
            "virtual_location": "AWS us-east-1",
            "acquisition_date": "2024-01-15",
            "purchase_cost": "1500.00",
            "vendor": "Dell Technologies",
            "license_number": "LIC-2024-001",
            "license_type": "perpetual",
            "license_expiry_date": "2025-01-15",
            "compliance_status": "Compliant",
            "warranty": "3 years manufacturer warranty",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the asset was created with ITAM fields
        asset = Asset.objects.get(id=response.data["id"])
        self.assertEqual(asset.asset_type, "hardware")
        self.assertEqual(asset.serial_number, "SN123456789")
        self.assertEqual(asset.assigned_user, "john.doe@example.com")
        self.assertEqual(asset.department, "IT Department")
        self.assertEqual(asset.purchase_cost, Decimal("1500.00"))
        self.assertEqual(asset.vendor, "Dell Technologies")

    def test_create_asset_with_json_fields(self):
        """Test creating an asset with JSON ITAM fields."""
        url = reverse("assets-list")
        upgrade_history = [
            {
                "version": "1.0",
                "date": "2024-01-15",
                "description": "Initial installation",
            },
            {"version": "1.1", "date": "2024-02-15", "description": "Security update"},
        ]
        service_history = [
            {
                "date": "2024-01-20",
                "type": "maintenance",
                "description": "Routine check",
            },
            {
                "date": "2024-02-10",
                "type": "repair",
                "description": "Hardware replacement",
            },
        ]

        data = {
            "name": "Test Software",
            "description": "Test software for ITAM testing",
            "folder": self.folder.id,
            "asset_type": "software",
            "upgrade_history": upgrade_history,
            "service_history": service_history,
            "security_config": {"encryption": True, "firewall": "enabled"},
            "known_vulnerabilities": [{"cve": "CVE-2024-001", "severity": "high"}],
            "compliance_standards": ["ISO27001", "SOC2"],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify JSON fields were saved correctly
        asset = Asset.objects.get(id=response.data["id"])
        self.assertEqual(asset.upgrade_history, upgrade_history)
        self.assertEqual(asset.service_history, service_history)
        self.assertEqual(asset.security_config["encryption"], True)
        self.assertIn("CVE-2024-001", asset.known_vulnerabilities[0]["cve"])

    def test_validation_negative_costs(self):
        """Test validation of negative cost fields."""
        url = reverse("assets-list")
        data = {
            "name": "Test Asset",
            "folder": self.folder.id,
            "purchase_cost": "-100.00",  # Negative cost should fail
            "depreciation_value": "-50.00",  # Negative depreciation should fail
            "total_cost_of_ownership": "-200.00",  # Negative TCO should fail
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Purchase cost cannot be negative", str(response.data))

    def test_validation_future_acquisition_date(self):
        """Test validation of future acquisition date."""
        url = reverse("assets-list")
        future_date = (date.today() + timedelta(days=30)).isoformat()
        data = {
            "name": "Test Asset",
            "folder": self.folder.id,
            "acquisition_date": future_date,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Acquisition date cannot be in the future", str(response.data))

    def test_validation_past_end_of_life_date(self):
        """Test validation of past end of life date."""
        url = reverse("assets-list")
        past_date = (date.today() - timedelta(days=30)).isoformat()
        data = {
            "name": "Test Asset",
            "folder": self.folder.id,
            "end_of_life_date": past_date,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("End of life date cannot be in the past", str(response.data))

    def test_validation_cross_field_dates(self):
        """Test cross-field validation for dates."""
        url = reverse("assets-list")
        acquisition_date = "2024-01-15"
        end_of_life_date = "2024-01-10"  # Before acquisition date

        data = {
            "name": "Test Asset",
            "folder": self.folder.id,
            "acquisition_date": acquisition_date,
            "end_of_life_date": end_of_life_date,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "End of life date must be after acquisition date", str(response.data)
        )

    def test_update_asset_itam_fields(self):
        """Test updating an asset with ITAM fields."""
        # Create an asset first
        asset = Asset.objects.create(
            name="Original Asset", folder=self.folder, asset_type="hardware"
        )

        url = reverse("assets-detail", kwargs={"pk": asset.pk})
        data = {
            "name": "Updated Asset",
            "asset_type": "software",
            "vendor": "Microsoft",
            "purchase_cost": "500.00",
            "department": "Engineering",
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify updates
        asset.refresh_from_db()
        self.assertEqual(asset.asset_type, "software")
        self.assertEqual(asset.vendor, "Microsoft")
        self.assertEqual(asset.purchase_cost, Decimal("500.00"))
        self.assertEqual(asset.department, "Engineering")

    def test_filter_by_asset_type(self):
        """Test filtering assets by asset_type."""
        # Create assets with different types
        Asset.objects.create(
            name="Hardware Asset", folder=self.folder, asset_type="hardware"
        )
        Asset.objects.create(
            name="Software Asset", folder=self.folder, asset_type="software"
        )

        url = reverse("assets-list")
        response = self.client.get(url, {"asset_type": "hardware"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["asset_type"], "hardware")

    def test_filter_by_vendor(self):
        """Test filtering assets by vendor."""
        Asset.objects.create(
            name="Dell Laptop", folder=self.folder, vendor="Dell Technologies"
        )
        Asset.objects.create(name="HP Laptop", folder=self.folder, vendor="HP Inc")

        url = reverse("assets-list")
        response = self.client.get(url, {"vendor": "Dell"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("Dell", response.data["results"][0]["vendor"])

    def test_filter_by_license_expiry_date(self):
        """Test filtering assets by license expiry date."""
        Asset.objects.create(
            name="Expired License",
            folder=self.folder,
            license_expiry_date=date.today() - timedelta(days=30),
        )
        Asset.objects.create(
            name="Valid License",
            folder=self.folder,
            license_expiry_date=date.today() + timedelta(days=30),
        )

        url = reverse("assets-list")
        response = self.client.get(
            url, {"license_expiry_date__gte": date.today().isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Valid License")

    def test_search_by_itam_fields(self):
        """Test searching assets by ITAM fields."""
        Asset.objects.create(
            name="Test Asset",
            folder=self.folder,
            vendor="Microsoft",
            department="IT",
            serial_number="SN123456",
        )

        url = reverse("assets-list")
        # Search by vendor
        response = self.client.get(url, {"search": "Microsoft"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Search by department
        response = self.client.get(url, {"search": "IT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Search by serial number
        response = self.client.get(url, {"search": "SN123456"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_serializer_validation(self):
        """Test serializer validation methods."""
        serializer = AssetWriteSerializer()

        # Test negative cost validation
        with self.assertRaises(Exception):
            serializer.validate_purchase_cost(-100.00)

        # Test future acquisition date validation
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(Exception):
            serializer.validate_acquisition_date(future_date)

        # Test past end of life date validation
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(Exception):
            serializer.validate_end_of_life_date(past_date)

    def test_asset_type_choices_display(self):
        """Test that asset_type choices are properly displayed."""
        asset = Asset.objects.create(
            name="Test Asset", folder=self.folder, asset_type="hardware"
        )

        url = reverse("assets-detail", kwargs={"pk": asset.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["asset_type"], "Hardware")

    def test_backward_compatibility(self):
        """Test that existing assets without ITAM fields still work."""
        # Create asset without any ITAM fields
        asset = Asset.objects.create(name="Legacy Asset", folder=self.folder)

        url = reverse("assets-detail", kwargs={"pk": asset.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all ITAM fields are null/empty
        self.assertIsNone(response.data.get("asset_type"))
        self.assertIsNone(response.data.get("vendor"))
        self.assertIsNone(response.data.get("purchase_cost"))
        self.assertIsNone(response.data.get("serial_number"))
