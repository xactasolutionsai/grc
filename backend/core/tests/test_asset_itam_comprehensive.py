"""
Comprehensive tests for Asset ITAM (IT Asset Management) fields including API endpoints.
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Asset, Folder
from core.serializers import AssetWriteSerializer, AssetReadSerializer
from iam.models import Role, RoleAssignment

User = get_user_model()


class AssetITAMComprehensiveTestCase(TestCase):
    """Comprehensive test cases for Asset ITAM fields including API functionality."""

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
        analyst_role, created = Role.objects.get_or_create(
            name="Analyst", defaults={"description": "Analyst role for testing"}
        )

        role_assignment = RoleAssignment.objects.create(
            user=self.user, role=analyst_role
        )
        role_assignment.perimeter_folders.add(self.folder)

    def test_asset_model_itam_fields(self):
        """Test that all ITAM fields can be set on the Asset model."""
        asset_data = {
            "name": "Test Asset",
            "folder": self.folder,
            # Inventory
            "asset_type": "hardware",
            "specifications": "Test specifications",
            "serial_number": "SN123456789",
            "license_key": "LIC-KEY-123",
            # Ownership & Location
            "assigned_user": "john.doe@example.com",
            "department": "IT Department",
            "physical_location": "Building A, Room 101",
            "virtual_location": "AWS us-east-1",
            # Lifecycle
            "acquisition_date": date.today(),
            "deployment_details": "Deployed in production",
            "maintenance_schedule": "Monthly maintenance",
            "upgrade_history": [{"version": "1.0", "date": "2024-01-15"}],
            "end_of_life_date": date.today() + timedelta(days=365),
            # Licensing & Compliance
            "license_number": "LIC-2024-001",
            "license_type": "perpetual",
            "license_expiry_date": date.today() + timedelta(days=365),
            "compliance_status": "Compliant",
            "audit_logs": [{"date": "2024-01-15", "action": "Created"}],
            # Financials
            "purchase_cost": Decimal("1500.00"),
            "depreciation_value": Decimal("300.00"),
            "total_cost_of_ownership": Decimal("2000.00"),
            "vendor": "Dell Technologies",
            "warranty": "3 years manufacturer warranty",
            # Operations
            "service_history": [{"date": "2024-01-20", "type": "maintenance"}],
            "preventive_maintenance": "Monthly checks",
            "sla_details": "99.9% uptime SLA",
            "spare_parts": "Keyboard, mouse, power adapter",
            # Security & Risk
            "security_config": {"encryption": True, "firewall": "enabled"},
            "known_vulnerabilities": [{"cve": "CVE-2024-001", "severity": "high"}],
            "incident_records": [{"date": "2024-01-15", "severity": "medium"}],
            "compliance_standards": ["ISO27001", "SOC2"],
        }

        asset = Asset.objects.create(**asset_data)

        # Verify all fields were saved correctly
        self.assertEqual(asset.asset_type, "hardware")
        self.assertEqual(asset.serial_number, "SN123456789")
        self.assertEqual(asset.assigned_user, "john.doe@example.com")
        self.assertEqual(asset.department, "IT Department")
        self.assertEqual(asset.purchase_cost, Decimal("1500.00"))
        self.assertEqual(asset.vendor, "Dell Technologies")
        self.assertEqual(
            asset.upgrade_history, [{"version": "1.0", "date": "2024-01-15"}]
        )
        self.assertEqual(
            asset.security_config, {"encryption": True, "firewall": "enabled"}
        )

    def test_asset_serializer_validation(self):
        """Test AssetWriteSerializer validation for ITAM fields."""
        serializer = AssetWriteSerializer()

        # Test negative cost validation
        with self.assertRaises(Exception):
            serializer.validate_purchase_cost(-100.00)

        with self.assertRaises(Exception):
            serializer.validate_depreciation_value(-50.00)

        with self.assertRaises(Exception):
            serializer.validate_total_cost_of_ownership(-200.00)

        # Test future acquisition date validation
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(Exception):
            serializer.validate_acquisition_date(future_date)

        # Test past end of life date validation
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(Exception):
            serializer.validate_end_of_life_date(past_date)

    def test_asset_api_create_with_itam_fields(self):
        """Test creating an asset via API with ITAM fields."""
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

    def test_asset_api_create_with_json_fields(self):
        """Test creating an asset via API with JSON ITAM fields."""
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

    def test_asset_api_validation_negative_costs(self):
        """Test API validation of negative cost fields."""
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

    def test_asset_api_validation_future_acquisition_date(self):
        """Test API validation of future acquisition date."""
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

    def test_asset_api_validation_cross_field_dates(self):
        """Test API cross-field validation for dates."""
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

    def test_asset_api_update_with_itam_fields(self):
        """Test updating an asset via API with ITAM fields."""
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

    def test_asset_api_filter_by_itam_fields(self):
        """Test filtering assets via API by ITAM fields."""
        # Create assets with different ITAM data
        Asset.objects.create(
            name="Hardware Asset",
            folder=self.folder,
            asset_type="hardware",
            vendor="Dell Technologies",
            department="IT",
        )
        Asset.objects.create(
            name="Software Asset",
            folder=self.folder,
            asset_type="software",
            vendor="Microsoft",
            department="Engineering",
        )

        # Test filtering by asset_type
        url = reverse("assets-list")
        response = self.client.get(url, {"asset_type": "hardware"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["asset_type"], "hardware")

        # Test filtering by vendor
        response = self.client.get(url, {"vendor": "Dell"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("Dell", response.data["results"][0]["vendor"])

        # Test filtering by department
        response = self.client.get(url, {"department": "IT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["department"], "IT")

    def test_asset_api_search_by_itam_fields(self):
        """Test searching assets via API by ITAM fields."""
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

    def test_asset_read_serializer_itam_fields(self):
        """Test AssetReadSerializer includes ITAM fields."""
        asset = Asset.objects.create(
            name="Test Asset",
            folder=self.folder,
            asset_type="hardware",
            vendor="Dell Technologies",
            purchase_cost=Decimal("1500.00"),
        )

        serializer = AssetReadSerializer(asset)
        data = serializer.data

        # Verify ITAM fields are included in read serializer
        self.assertIn("asset_type", data)
        self.assertIn("vendor", data)
        self.assertIn("purchase_cost", data)
        self.assertEqual(data["asset_type"], "Hardware")  # Display value
        self.assertEqual(data["vendor"], "Dell Technologies")

    def test_asset_import_export_serializer_itam_fields(self):
        """Test AssetImportExportSerializer includes ITAM fields."""
        from core.serializers import AssetImportExportSerializer

        asset = Asset.objects.create(
            name="Test Asset",
            folder=self.folder,
            asset_type="hardware",
            vendor="Dell Technologies",
            purchase_cost=Decimal("1500.00"),
            serial_number="SN123456789",
        )

        serializer = AssetImportExportSerializer(asset)
        data = serializer.data

        # Verify ITAM fields are included in import/export serializer
        self.assertIn("asset_type", data)
        self.assertIn("vendor", data)
        self.assertIn("purchase_cost", data)
        self.assertIn("serial_number", data)
        self.assertEqual(data["asset_type"], "hardware")
        self.assertEqual(data["vendor"], "Dell Technologies")
        self.assertEqual(data["serial_number"], "SN123456789")

    def test_asset_model_string_representation(self):
        """Test Asset model string representation with ITAM fields."""
        asset = Asset.objects.create(
            name="Test Asset",
            folder=self.folder,
            asset_type="hardware",
            serial_number="SN123456789",
        )

        # Test that the model can be converted to string
        str_repr = str(asset)
        self.assertIn("Test Asset", str_repr)

    def test_asset_model_choices_display(self):
        """Test Asset model choices display methods."""
        asset = Asset.objects.create(
            name="Test Asset", folder=self.folder, asset_type="hardware"
        )

        # Test the display method
        self.assertEqual(asset.get_asset_type_display(), "Hardware")

    def test_asset_model_decimal_precision(self):
        """Test that decimal fields maintain precision."""
        asset = Asset.objects.create(
            name="Test Asset",
            folder=self.folder,
            purchase_cost=Decimal("1234.56"),
            depreciation_value=Decimal("987.65"),
            total_cost_of_ownership=Decimal("2345.67"),
        )

        self.assertEqual(asset.purchase_cost, Decimal("1234.56"))
        self.assertEqual(asset.depreciation_value, Decimal("987.65"))
        self.assertEqual(asset.total_cost_of_ownership, Decimal("2345.67"))

    def test_asset_model_json_fields_serialization(self):
        """Test that JSON fields are properly serialized/deserialized."""
        json_data = {
            "upgrade_history": [{"version": "1.0", "date": "2024-01-15"}],
            "service_history": [{"date": "2024-01-20", "type": "maintenance"}],
            "security_config": {"encryption": True, "firewall": "enabled"},
            "known_vulnerabilities": [{"cve": "CVE-2024-001", "severity": "high"}],
            "compliance_standards": ["ISO27001", "SOC2"],
        }

        asset = Asset.objects.create(name="Test Asset", folder=self.folder, **json_data)

        # Verify JSON fields were saved and can be retrieved
        for field_name, expected_value in json_data.items():
            actual_value = getattr(asset, field_name)
            self.assertEqual(actual_value, expected_value)
