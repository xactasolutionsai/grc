from django.test import TestCase
from django.contrib.auth import get_user_model
from workpapers.models import Workpaper, WorkpaperApproval

User = get_user_model()


class WorkpaperModelTestCase(TestCase):
    """Test cases for Workpaper model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.reviewer = User.objects.create_user(
            email="reviewer@example.com", password="testpass123"
        )
        self.approver = User.objects.create_user(
            email="approver@example.com", password="testpass123"
        )

    def test_create_workpaper(self):
        """Test creating a workpaper"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            description="Test description",
            workpaper_type="pdf",
            uploaded_by=self.user,
        )
        self.assertEqual(workpaper.title, "Test Workpaper")
        self.assertEqual(workpaper.status, "collected")
        self.assertTrue(workpaper.is_active)

    def test_workpaper_workflow_submit_for_review(self):
        """Test submitting workpaper for review"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="collected",
        )

        result = workpaper.submit_for_review(self.reviewer)

        self.assertTrue(result)
        self.assertEqual(workpaper.status, "reviewed")
        self.assertEqual(workpaper.reviewer, self.reviewer)
        self.assertIsNotNone(workpaper.reviewed_at)

        # Check approval history was created
        history = WorkpaperApproval.objects.filter(workpaper=workpaper)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().action, "reviewed")

    def test_workpaper_workflow_approve(self):
        """Test approving a workpaper"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="reviewed",
        )

        result = workpaper.approve(self.approver, "Looks good")

        self.assertTrue(result)
        self.assertEqual(workpaper.status, "approved")
        self.assertEqual(workpaper.approver, self.approver)
        self.assertIsNotNone(workpaper.approved_at)

        # Check approval history was created
        history = WorkpaperApproval.objects.filter(workpaper=workpaper)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().action, "approved")
        self.assertEqual(history.first().comments, "Looks good")

    def test_workpaper_workflow_reject(self):
        """Test rejecting a workpaper"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="reviewed",
        )

        result = workpaper.reject(self.approver, "Needs more detail")

        self.assertTrue(result)
        self.assertEqual(workpaper.status, "reviewed")  # Status should remain unchanged
        self.assertEqual(workpaper.rejection_reason, "Needs more detail")

        # Check approval history was created
        history = WorkpaperApproval.objects.filter(workpaper=workpaper)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().action, "rejected")

    def test_can_be_reviewed(self):
        """Test can_be_reviewed check"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="collected",
        )

        self.assertTrue(workpaper.can_be_reviewed())

        workpaper.status = "reviewed"
        workpaper.save()

        self.assertFalse(workpaper.can_be_reviewed())

    def test_can_be_approved(self):
        """Test can_be_approved check"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="reviewed",
        )

        self.assertTrue(workpaper.can_be_approved())

        workpaper.status = "collected"
        workpaper.save()

        self.assertFalse(workpaper.can_be_approved())

    def test_get_file_extension(self):
        """Test getting file extension"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper", workpaper_type="pdf", uploaded_by=self.user
        )

        # Without file
        self.assertIsNone(workpaper.get_file_extension())

    def test_workpaper_str(self):
        """Test string representation"""
        workpaper = Workpaper.objects.create(
            title="Test Workpaper",
            workpaper_type="pdf",
            uploaded_by=self.user,
            status="collected",
        )

        expected = "Test Workpaper (Collected)"
        self.assertEqual(str(workpaper), expected)
