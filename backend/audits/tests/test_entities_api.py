from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from audits.models import AuditEntity

User = get_user_model()

class AuditEntityAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.login(username='testuser', password='pass')

    def test_create_entity(self):
        url = reverse('audit-entity-list')
        data = {
            'name': 'Finance Department',
            'entity_type': 'business_unit',
            'description': 'Finance BU',
        }
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AuditEntity.objects.count(), 1)

    def test_list_entities(self):
        AuditEntity.objects.create(name='IT System A', entity_type='system')
        url = reverse('audit-entity-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.data, list) or 'results' in resp.data)

    def test_related_endpoint(self):
        # Create a test entity
        entity = AuditEntity.objects.create(
            name='Test Entity',
            entity_type='system',
            description='Test system for related endpoint'
        )
        
        # Test the related endpoint
        url = reverse('audit-entity-related', kwargs={'pk': entity.id})
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('engagements', resp.data)
        self.assertIn('compliance_audits', resp.data)
        self.assertIn('risks', resp.data)
        self.assertIn('controls', resp.data)
        
        # Check that all fields are lists
        self.assertIsInstance(resp.data['engagements'], list)
        self.assertIsInstance(resp.data['compliance_audits'], list)
        self.assertIsInstance(resp.data['risks'], list)
        self.assertIsInstance(resp.data['controls'], list)
