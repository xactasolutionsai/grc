"""
Test cases for AuditEngagement API endpoints
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from audits.models import AuditEntity, AuditPlan, AuditEngagement


class AuditEngagementAPITestCase(APITestCase):
    """Test cases for AuditEngagement API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.auditor = User.objects.create_user(
            username='auditor',
            email='auditor@example.com',
            password='testpass123'
        )
        self.lead = User.objects.create_user(
            username='lead',
            email='lead@example.com',
            password='testpass123'
        )
        
        # Create test audit entity
        self.audit_entity = AuditEntity.objects.create(
            name='Test Entity',
            entity_type='system',
            owner=self.user,
            risk_score=7.5,
            is_active=True
        )
        
        # Create test audit plan
        self.audit_plan = AuditPlan.objects.create(
            entity=self.audit_entity,
            title='Test Audit Plan',
            description='Test description',
            planned_start=date.today(),
            planned_end=date.today() + timedelta(days=30),
            lead_auditor=self.lead,
            status='approved'
        )
        
        # Create test engagement
        self.engagement = AuditEngagement.objects.create(
            title='Test Engagement',
            description='Test engagement description',
            audit_plan=self.audit_plan,
            entity=self.audit_entity,
            status='draft',
            priority='medium',
            assigned_auditor=self.auditor,
            engagement_lead=self.lead,
            planned_start_date=date.today(),
            planned_end_date=date.today() + timedelta(days=14),
            created_by=self.user
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_list_engagements(self):
        """Test listing engagements"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Engagement')
    
    def test_retrieve_engagement(self):
        """Test retrieving a single engagement"""
        url = reverse('audit-engagement-detail', kwargs={'pk': self.engagement.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Engagement')
        self.assertEqual(response.data['status'], 'draft')
        self.assertEqual(response.data['priority'], 'medium')
    
    def test_create_engagement(self):
        """Test creating a new engagement"""
        url = reverse('audit-engagement-list')
        data = {
            'title': 'New Engagement',
            'description': 'New engagement description',
            'audit_plan': self.audit_plan.pk,
            'entity': self.audit_entity.pk,
            'status': 'draft',
            'priority': 'high',
            'assigned_auditor': self.auditor.pk,
            'engagement_lead': self.lead.pk,
            'planned_start_date': date.today().isoformat(),
            'planned_end_date': (date.today() + timedelta(days=10)).isoformat(),
            'scope': 'Test scope',
            'objectives': 'Test objectives',
            'estimated_hours': 40,
            'budget_allocated': '5000.00'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Engagement')
        self.assertEqual(response.data['created_by'], self.user.pk)
    
    def test_update_engagement(self):
        """Test updating an engagement"""
        url = reverse('audit-engagement-detail', kwargs={'pk': self.engagement.pk})
        data = {
            'title': 'Updated Engagement',
            'description': 'Updated description',
            'priority': 'critical',
            'progress_percentage': 25
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Engagement')
        self.assertEqual(response.data['priority'], 'critical')
        self.assertEqual(response.data['progress_percentage'], 25)
    
    def test_start_engagement(self):
        """Test starting an engagement"""
        url = reverse('audit-engagement-start', kwargs={'pk': self.engagement.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertIsNotNone(response.data['actual_start_date'])
    
    def test_start_engagement_invalid_status(self):
        """Test starting an engagement with invalid status"""
        # Set engagement to in_progress status
        self.engagement.status = 'in_progress'
        self.engagement.save()
        
        url = reverse('audit-engagement-start', kwargs={'pk': self.engagement.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_results(self):
        """Test submitting engagement results"""
        # Set engagement to in_progress status first
        self.engagement.status = 'in_progress'
        self.engagement.save()
        
        url = reverse('audit-engagement-submit-results', kwargs={'pk': self.engagement.pk})
        data = {
            'findings_summary': 'Test findings',
            'recommendations': 'Test recommendations'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'submitted')
        self.assertEqual(response.data['findings_summary'], 'Test findings')
        self.assertEqual(response.data['recommendations'], 'Test recommendations')
    
    def test_close_engagement(self):
        """Test closing an engagement"""
        # Set engagement to submitted status first
        self.engagement.status = 'submitted'
        self.engagement.save()
        
        url = reverse('audit-engagement-close', kwargs={'pk': self.engagement.pk})
        data = {
            'closure_notes': 'Test closure notes'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'closed')
        self.assertEqual(response.data['closure_notes'], 'Test closure notes')
    
    def test_update_progress(self):
        """Test updating engagement progress"""
        url = reverse('audit-engagement-update-progress', kwargs={'pk': self.engagement.pk})
        data = {
            'progress_percentage': 50,
            'fieldwork_notes': 'Test fieldwork notes'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percentage'], 50)
        self.assertEqual(response.data['fieldwork_notes'], 'Test fieldwork notes')
    
    def test_update_progress_invalid_percentage(self):
        """Test updating progress with invalid percentage"""
        url = reverse('audit-engagement-update-progress', kwargs={'pk': self.engagement.pk})
        data = {
            'progress_percentage': 150  # Invalid percentage
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_engagement_timeline(self):
        """Test getting engagement timeline"""
        url = reverse('audit-engagement-timeline', kwargs={'pk': self.engagement.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('created', response.data)
        self.assertEqual(response.data['created']['action'], 'Engagement created')
    
    def test_engagement_calendar(self):
        """Test getting engagements for calendar view"""
        url = reverse('audit-engagement-calendar')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_engagement_calendar_with_date_filter(self):
        """Test calendar view with date filter"""
        current_year = date.today().year
        current_month = date.today().month
        
        url = reverse('audit-engagement-calendar')
        response = self.client.get(url, {
            'year': current_year,
            'month': current_month
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_engagement_statistics(self):
        """Test getting engagement statistics"""
        url = reverse('audit-engagement-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)
        self.assertIn('by_status', response.data)
        self.assertIn('by_priority', response.data)
        self.assertIn('overdue', response.data)
        self.assertIn('completed_this_month', response.data)
    
    def test_filter_engagements_by_status(self):
        """Test filtering engagements by status"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'status': 'draft'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_priority(self):
        """Test filtering engagements by priority"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'priority': 'medium'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_audit_plan(self):
        """Test filtering engagements by audit plan"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'audit_plan': self.audit_plan.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_entity(self):
        """Test filtering engagements by entity"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'entity': self.audit_entity.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_assigned_auditor(self):
        """Test filtering engagements by assigned auditor"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'assigned_auditor': self.auditor.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_engagement_lead(self):
        """Test filtering engagements by engagement lead"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'engagement_lead': self.lead.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_date_range(self):
        """Test filtering engagements by date range"""
        url = reverse('audit-engagement-list')
        start_date = (date.today() - timedelta(days=1)).isoformat()
        end_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = self.client.get(url, {
            'planned_start_date__gte': start_date,
            'planned_end_date__lte': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_engagements_by_overdue(self):
        """Test filtering overdue engagements"""
        # Create an overdue engagement
        overdue_engagement = AuditEngagement.objects.create(
            title='Overdue Engagement',
            description='Overdue description',
            audit_plan=self.audit_plan,
            entity=self.audit_entity,
            status='in_progress',
            priority='medium',
            planned_start_date=date.today() - timedelta(days=20),
            planned_end_date=date.today() - timedelta(days=5),  # Overdue
            created_by=self.user
        )
        
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'overdue': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Overdue Engagement')
    
    def test_search_engagements(self):
        """Test searching engagements"""
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_ordering_engagements(self):
        """Test ordering engagements"""
        # Create another engagement for ordering test
        AuditEngagement.objects.create(
            title='Another Engagement',
            description='Another description',
            audit_plan=self.audit_plan,
            entity=self.audit_entity,
            status='draft',
            priority='low',
            planned_start_date=date.today(),
            planned_end_date=date.today() + timedelta(days=7),
            created_by=self.user
        )
        
        url = reverse('audit-engagement-list')
        response = self.client.get(url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # Should be ordered by title ascending
        self.assertEqual(response.data['results'][0]['title'], 'Another Engagement')
        self.assertEqual(response.data['results'][1]['title'], 'Test Engagement')
    
    def test_engagement_validation(self):
        """Test engagement validation"""
        url = reverse('audit-engagement-list')
        data = {
            'title': '',  # Empty title should fail
            'audit_plan': self.audit_plan.pk,
            'entity': self.audit_entity.pk,
            'planned_start_date': date.today().isoformat(),
            'planned_end_date': (date.today() - timedelta(days=1)).isoformat(),  # End before start
            'progress_percentage': 150  # Invalid percentage
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('planned_end_date', response.data)
        self.assertIn('progress_percentage', response.data)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to engagements"""
        self.client.force_authenticate(user=None)
        
        url = reverse('audit-engagement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
