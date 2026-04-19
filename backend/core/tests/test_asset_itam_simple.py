"""
Simple tests for Asset ITAM (IT Asset Management) fields.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Asset, Folder
from core.serializers import AssetWriteSerializer

User = get_user_model()


class AssetITAMSimpleTestCase(TestCase):
    """Simple test cases for Asset ITAM fields functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        # Create a test folder
        self.folder = Folder.objects.create(
            name="Test Folder", description="Test folder for ITAM tests"
        )

    def test_create_asset_with_itam_fields(self):
        """Test creating an asset with ITAM fields."""
        asset = Asset.objects.create(
            name="Test Laptop",
            description="Test laptop for ITAM testing",
            folder=self.folder,
            asset_type="hardware",
            specifications="Intel i7, 16GB RAM, 512GB SSD",
            serial_number="SN123456789",
            assigned_user="john.doe@example.com",
            department="IT Department",
            physical_location="Building A, Floor 2, Room 201",
            virtual_location="AWS us-east-1",
            purchase_cost=Decimal("1500.00"),
            vendor="Dell Technologies",
            license_number="LIC-2024-001",
            license_type="perpetual",
            compliance_status="Compliant",
            warranty="3 years manufacturer warranty",
        )

        # Verify the asset was created with ITAM fields
        self.assertEqual(asset.asset_type, "hardware")
        self.assertEqual(asset.serial_number, "SN123456789")
        self.assertEqual(asset.assigned_user, "john.doe@example.com")
        self.assertEqual(asset.department, "IT Department")
        self.assertEqual(asset.purchase_cost, Decimal("1500.00"))
        self.assertEqual(asset.vendor, "Dell Technologies")

    def test_create_asset_with_json_fields(self):
        """Test creating an asset with JSON ITAM fields."""
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

        asset = Asset.objects.create(
            name="Test Software",
            description="Test software for ITAM testing",
            folder=self.folder,
            asset_type="software",
            upgrade_history=upgrade_history,
            service_history=service_history,
            security_config={"encryption": True, "firewall": "enabled"},
            known_vulnerabilities=[{"cve": "CVE-2024-001", "severity": "high"}],
            compliance_standards=["ISO27001", "SOC2"],
        )

        # Verify JSON fields were saved correctly
        self.assertEqual(asset.upgrade_history, upgrade_history)
        self.assertEqual(asset.service_history, service_history)
        self.assertEqual(asset.security_config["encryption"], True)
        self.assertIn("CVE-2024-001", asset.known_vulnerabilities[0]["cve"])

    def test_serializer_validation_negative_costs(self):
        """Test validation of negative cost fields."""
        serializer = AssetWriteSerializer()

        # Test negative cost validation
        with self.assertRaises(Exception):
            serializer.validate_purchase_cost(-100.00)

        with self.assertRaises(Exception):
            serializer.validate_depreciation_value(-50.00)

        with self.assertRaises(Exception):
            serializer.validate_total_cost_of_ownership(-200.00)

    def test_asset_type_choices(self):
        """Test that asset_type choices work correctly."""
        # Test all asset types
        asset_types = ["hardware", "software", "cloud", "digital"]

        for asset_type in asset_types:
            asset = Asset.objects.create(
                name=f"Test {asset_type.title()} Asset",
                folder=self.folder,
                asset_type=asset_type,
            )
            self.assertEqual(asset.asset_type, asset_type)

    def test_backward_compatibility(self):
        """Test that existing assets without ITAM fields still work."""
        # Create asset without any ITAM fields
        asset = Asset.objects.create(name="Legacy Asset", folder=self.folder)

        # Verify all ITAM fields are null/empty
        self.assertIsNone(asset.asset_type)
        self.assertIsNone(asset.vendor)
        self.assertIsNone(asset.purchase_cost)
        self.assertIsNone(asset.serial_number)
        self.assertIsNone(asset.assigned_user)
        self.assertIsNone(asset.department)

    def test_serial_number_uniqueness(self):
        """Test that serial numbers are unique."""
        # Create first asset with serial number
        Asset.objects.create(
            name="Asset 1", folder=self.folder, serial_number="SN123456"
        )

        # Try to create second asset with same serial number
        with self.assertRaises(Exception):
            Asset.objects.create(
                name="Asset 2", folder=self.folder, serial_number="SN123456"
            )

    def test_decimal_fields_precision(self):
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

    def test_asset_type_display(self):
        """Test that asset_type display works correctly."""
        asset = Asset.objects.create(
            name="Test Asset", folder=self.folder, asset_type="hardware"
        )

        # Test the display method
        self.assertEqual(asset.get_asset_type_display(), "Hardware")
