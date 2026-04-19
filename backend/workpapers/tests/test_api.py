from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from workpapers.models import Workpaper

User = get_user_model()


class WorkpaperAPITestCase(TestCase):
    """Test cases for Workpaper API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_workpaper(self):
        """Test creating a workpaper via API"""
        data = {
            'title': 'Test Workpaper',
            'description': 'Test description',
            'workpaper_type': 'pdf',
            'is_active': True
        }
        
        response = self.client.post('/api/workpapers/workpapers/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Workpaper')
        self.assertEqual(response.data['status'], 'collected')
        self.assertEqual(response.data['uploaded_by'], self.user.id)

    def test_list_workpapers(self):
        """Test listing workpapers"""
        Workpaper.objects.create(
            title='Workpaper 1',
            workpaper_type='pdf',
            uploaded_by=self.user
        )
        Workpaper.objects.create(
            title='Workpaper 2',
            workpaper_type='excel',
            uploaded_by=self.user
        )
        
        response = self.client.get('/api/workpapers/workpapers/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_workpaper(self):
        """Test retrieving a single workpaper"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user
        )
        
        response = self.client.get(f'/api/workpapers/workpapers/{workpaper.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Workpaper')

    def test_update_workpaper(self):
        """Test updating a workpaper"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user
        )
        
        data = {
            'title': 'Updated Workpaper',
            'description': 'Updated description',
            'workpaper_type': 'pdf'
        }
        
        response = self.client.put(f'/api/workpapers/workpapers/{workpaper.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Workpaper')

    def test_delete_workpaper(self):
        """Test deleting a workpaper"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user
        )
        
        response = self.client.delete(f'/api/workpapers/workpapers/{workpaper.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workpaper.objects.filter(id=workpaper.id).exists())

    def test_submit_for_review(self):
        """Test submitting workpaper for review"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user,
            status='collected'
        )
        
        response = self.client.post(f'/api/workpapers/workpapers/{workpaper.id}/submit_for_review/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'reviewed')

    def test_approve_workpaper(self):
        """Test approving a workpaper"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user,
            status='reviewed'
        )
        
        data = {
            'action': 'approve',
            'comments': 'Looks good'
        }
        
        response = self.client.post(f'/api/workpapers/workpapers/{workpaper.id}/approve/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')

    def test_reject_workpaper(self):
        """Test rejecting a workpaper"""
        workpaper = Workpaper.objects.create(
            title='Test Workpaper',
            workpaper_type='pdf',
            uploaded_by=self.user,
            status='reviewed'
        )
        
        data = {
            'action': 'reject',
            'reason': 'Needs more detail'
        }
        
        response = self.client.post(f'/api/workpapers/workpapers/{workpaper.id}/reject/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rejection_reason'], 'Needs more detail')

    def test_filter_by_status(self):
        """Test filtering workpapers by status"""
        Workpaper.objects.create(
            title='Collected WP',
            workpaper_type='pdf',
            uploaded_by=self.user,
            status='collected'
        )
        Workpaper.objects.create(
            title='Reviewed WP',
            workpaper_type='pdf',
            uploaded_by=self.user,
            status='reviewed'
        )
        
        response = self.client.get('/api/workpapers/workpapers/?status=collected')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'collected')

    def test_filter_by_type(self):
        """Test filtering workpapers by type"""
        Workpaper.objects.create(
            title='PDF WP',
            workpaper_type='pdf',
            uploaded_by=self.user
        )
        Workpaper.objects.create(
            title='Excel WP',
            workpaper_type='excel',
            uploaded_by=self.user
        )
        
        response = self.client.get('/api/workpapers/workpapers/?workpaper_type=pdf')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['workpaper_type'], 'pdf')

