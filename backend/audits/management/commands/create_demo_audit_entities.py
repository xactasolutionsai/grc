from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from audits.models import AuditEntity
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo audit entities with hierarchy to showcase tree structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing audit entities before creating demo data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing audit entities...')
            AuditEntity.objects.all().delete()

        # Create demo users if they don't exist
        users = self.create_demo_users()
        
        # Create demo audit entities with hierarchy
        self.create_demo_entities(users)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created demo audit entities with hierarchy!')
        )

    def create_demo_users(self):
        """Create demo users for ownership"""
        users = []
        
        # Create some demo users
        demo_users = [
            {'email': 'john.doe@company.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'email': 'jane.smith@company.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'email': 'mike.johnson@company.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
            {'email': 'sarah.wilson@company.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
            {'email': 'david.brown@company.com', 'first_name': 'David', 'last_name': 'Brown'},
        ]
        
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults=user_data
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {user.email}')
        
        return users

    def create_demo_entities(self, users):
        """Create demo audit entities with hierarchy"""
        
        # Level 1: Business Units (Root level)
        business_units = [
            {
                'name': 'Finance Department',
                'entity_type': 'business_unit',
                'description': 'Handles all financial operations, accounting, and financial reporting',
                'owner': users[0],
                'risk_score': 8.5,
                'regulatory_relevance': {'SOX': True, 'GAAP': True, 'IFRS': True},
                'last_audited': date.today() - timedelta(days=30),
                'is_active': True
            },
            {
                'name': 'Human Resources',
                'entity_type': 'business_unit',
                'description': 'Manages employee lifecycle, payroll, benefits, and compliance',
                'owner': users[1],
                'risk_score': 7.2,
                'regulatory_relevance': {'GDPR': True, 'Labor_Law': True},
                'last_audited': date.today() - timedelta(days=45),
                'is_active': True
            },
            {
                'name': 'Information Technology',
                'entity_type': 'business_unit',
                'description': 'IT infrastructure, security, and digital transformation',
                'owner': users[2],
                'risk_score': 9.1,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=15),
                'is_active': True
            },
            {
                'name': 'Operations',
                'entity_type': 'business_unit',
                'description': 'Core business operations and supply chain management',
                'owner': users[3],
                'risk_score': 6.8,
                'regulatory_relevance': {'ISO9001': True, 'Environmental': True},
                'last_audited': date.today() - timedelta(days=60),
                'is_active': True
            }
        ]

        # Create business units
        created_business_units = []
        for bu_data in business_units:
            entity = AuditEntity.objects.create(**bu_data)
            created_business_units.append(entity)
            self.stdout.write(f'Created business unit: {entity.name}')

        # Level 2: Processes (Children of Business Units)
        processes = [
            # Finance processes
            {
                'name': 'Financial Reporting Process',
                'entity_type': 'process',
                'description': 'Monthly and quarterly financial statement preparation and review',
                'parent': created_business_units[0],  # Finance Department
                'owner': users[0],
                'risk_score': 9.2,
                'regulatory_relevance': {'SOX': True, 'GAAP': True},
                'last_audited': date.today() - timedelta(days=25),
                'is_active': True
            },
            {
                'name': 'Accounts Payable Process',
                'entity_type': 'process',
                'description': 'Vendor invoice processing and payment authorization',
                'parent': created_business_units[0],  # Finance Department
                'owner': users[0],
                'risk_score': 7.8,
                'regulatory_relevance': {'SOX': True},
                'last_audited': date.today() - timedelta(days=40),
                'is_active': True
            },
            {
                'name': 'Payroll Process',
                'entity_type': 'process',
                'description': 'Employee salary calculation, tax withholding, and payment processing',
                'parent': created_business_units[1],  # Human Resources
                'owner': users[1],
                'risk_score': 8.1,
                'regulatory_relevance': {'Tax_Compliance': True, 'Labor_Law': True},
                'last_audited': date.today() - timedelta(days=20),
                'is_active': True
            },
            {
                'name': 'Employee Onboarding Process',
                'entity_type': 'process',
                'description': 'New employee hiring, documentation, and orientation',
                'parent': created_business_units[1],  # Human Resources
                'owner': users[1],
                'risk_score': 6.5,
                'regulatory_relevance': {'GDPR': True, 'Labor_Law': True},
                'last_audited': date.today() - timedelta(days=35),
                'is_active': True
            },
            {
                'name': 'IT Security Management Process',
                'entity_type': 'process',
                'description': 'Cybersecurity monitoring, incident response, and access control',
                'parent': created_business_units[2],  # Information Technology
                'owner': users[2],
                'risk_score': 9.5,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=10),
                'is_active': True
            },
            {
                'name': 'System Development Process',
                'entity_type': 'process',
                'description': 'Software development lifecycle and change management',
                'parent': created_business_units[2],  # Information Technology
                'owner': users[2],
                'risk_score': 8.7,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True},
                'last_audited': date.today() - timedelta(days=18),
                'is_active': True
            },
            {
                'name': 'Supply Chain Management Process',
                'entity_type': 'process',
                'description': 'Vendor selection, procurement, and supplier relationship management',
                'parent': created_business_units[3],  # Operations
                'owner': users[3],
                'risk_score': 7.3,
                'regulatory_relevance': {'ISO9001': True, 'Environmental': True},
                'last_audited': date.today() - timedelta(days=50),
                'is_active': True
            }
        ]

        # Create processes
        created_processes = []
        for process_data in processes:
            entity = AuditEntity.objects.create(**process_data)
            created_processes.append(entity)
            self.stdout.write(f'Created process: {entity.name} (Parent: {entity.parent.name})')

        # Level 3: Systems (Children of Processes)
        systems = [
            # Financial systems
            {
                'name': 'ERP Financial Module',
                'entity_type': 'system',
                'description': 'Enterprise resource planning system for financial management and reporting',
                'parent': created_processes[0],  # Financial Reporting Process
                'owner': users[0],
                'risk_score': 9.0,
                'regulatory_relevance': {'SOX': True, 'GAAP': True},
                'last_audited': date.today() - timedelta(days=22),
                'is_active': True
            },
            {
                'name': 'Invoice Processing System',
                'entity_type': 'system',
                'description': 'Automated invoice scanning, validation, and approval workflow',
                'parent': created_processes[1],  # Accounts Payable Process
                'owner': users[0],
                'risk_score': 8.2,
                'regulatory_relevance': {'SOX': True},
                'last_audited': date.today() - timedelta(days=38),
                'is_active': True
            },
            {
                'name': 'Payroll Management System',
                'entity_type': 'system',
                'description': 'Employee payroll calculation, tax processing, and payment distribution',
                'parent': created_processes[2],  # Payroll Process
                'owner': users[1],
                'risk_score': 8.5,
                'regulatory_relevance': {'Tax_Compliance': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=18),
                'is_active': True
            },
            {
                'name': 'HR Information System (HRIS)',
                'entity_type': 'system',
                'description': 'Employee data management, onboarding workflows, and HR analytics',
                'parent': created_processes[3],  # Employee Onboarding Process
                'owner': users[1],
                'risk_score': 7.8,
                'regulatory_relevance': {'GDPR': True, 'Labor_Law': True},
                'last_audited': date.today() - timedelta(days=32),
                'is_active': True
            },
            {
                'name': 'Security Information and Event Management (SIEM)',
                'entity_type': 'system',
                'description': 'Real-time security monitoring, threat detection, and incident response',
                'parent': created_processes[4],  # IT Security Management Process
                'owner': users[2],
                'risk_score': 9.8,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=8),
                'is_active': True
            },
            {
                'name': 'Identity and Access Management (IAM)',
                'entity_type': 'system',
                'description': 'User authentication, authorization, and access control management',
                'parent': created_processes[4],  # IT Security Management Process
                'owner': users[2],
                'risk_score': 9.3,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=12),
                'is_active': True
            },
            {
                'name': 'Code Repository and CI/CD Platform',
                'entity_type': 'system',
                'description': 'Source code management, continuous integration, and deployment automation',
                'parent': created_processes[5],  # System Development Process
                'owner': users[2],
                'risk_score': 8.9,
                'regulatory_relevance': {'ISO27001': True, 'SOC2': True},
                'last_audited': date.today() - timedelta(days=16),
                'is_active': True
            },
            {
                'name': 'Supply Chain Management System',
                'entity_type': 'system',
                'description': 'Vendor management, procurement workflows, and supplier performance tracking',
                'parent': created_processes[6],  # Supply Chain Management Process
                'owner': users[3],
                'risk_score': 7.5,
                'regulatory_relevance': {'ISO9001': True, 'Environmental': True},
                'last_audited': date.today() - timedelta(days=48),
                'is_active': True
            }
        ]

        # Create systems
        created_systems = []
        for system_data in systems:
            entity = AuditEntity.objects.create(**system_data)
            created_systems.append(entity)
            self.stdout.write(f'Created system: {entity.name} (Parent: {entity.parent.name})')

        # Level 4: Some vendors (Children of Systems)
        vendors = [
            {
                'name': 'SAP Corporation',
                'entity_type': 'vendor',
                'description': 'ERP software provider and implementation services',
                'parent': created_systems[0],  # ERP Financial Module
                'owner': users[0],
                'risk_score': 8.8,
                'regulatory_relevance': {'SOX': True, 'Data_Protection': True},
                'last_audited': date.today() - timedelta(days=20),
                'is_active': True
            },
            {
                'name': 'Microsoft Corporation',
                'entity_type': 'vendor',
                'description': 'Cloud services, productivity tools, and security solutions provider',
                'parent': created_systems[4],  # SIEM
                'owner': users[2],
                'risk_score': 9.1,
                'regulatory_relevance': {'SOC2': True, 'ISO27001': True, 'GDPR': True},
                'last_audited': date.today() - timedelta(days=5),
                'is_active': True
            },
            {
                'name': 'GitHub Inc.',
                'entity_type': 'vendor',
                'description': 'Code repository hosting and development collaboration platform',
                'parent': created_systems[6],  # Code Repository and CI/CD Platform
                'owner': users[2],
                'risk_score': 8.6,
                'regulatory_relevance': {'SOC2': True, 'ISO27001': True},
                'last_audited': date.today() - timedelta(days=14),
                'is_active': True
            }
        ]

        # Create vendors
        for vendor_data in vendors:
            entity = AuditEntity.objects.create(**vendor_data)
            self.stdout.write(f'Created vendor: {entity.name} (Parent: {entity.parent.name})')

        # Level 5: Compliance Domains (Some standalone, some with parents)
        compliance_domains = [
            {
                'name': 'SOX Compliance Program',
                'entity_type': 'compliance_domain',
                'description': 'Sarbanes-Oxley Act compliance monitoring and reporting',
                'parent': created_business_units[0],  # Finance Department
                'owner': users[0],
                'risk_score': 9.5,
                'regulatory_relevance': {'SOX': True, 'PCAOB': True},
                'last_audited': date.today() - timedelta(days=15),
                'is_active': True
            },
            {
                'name': 'GDPR Compliance Program',
                'entity_type': 'compliance_domain',
                'description': 'General Data Protection Regulation compliance and data privacy management',
                'parent': created_business_units[2],  # Information Technology
                'owner': users[2],
                'risk_score': 9.2,
                'regulatory_relevance': {'GDPR': True, 'Data_Protection': True},
                'last_audited': date.today() - timedelta(days=7),
                'is_active': True
            },
            {
                'name': 'ISO 27001 Information Security Management',
                'entity_type': 'compliance_domain',
                'description': 'Information security management system certification and maintenance',
                'parent': created_business_units[2],  # Information Technology
                'owner': users[2],
                'risk_score': 8.9,
                'regulatory_relevance': {'ISO27001': True, 'ISO27002': True},
                'last_audited': date.today() - timedelta(days=12),
                'is_active': True
            },
            {
                'name': 'Environmental Compliance Program',
                'entity_type': 'compliance_domain',
                'description': 'Environmental regulations compliance and sustainability reporting',
                'parent': created_business_units[3],  # Operations
                'owner': users[3],
                'risk_score': 7.8,
                'regulatory_relevance': {'Environmental': True, 'Sustainability': True},
                'last_audited': date.today() - timedelta(days=25),
                'is_active': True
            }
        ]

        # Create compliance domains
        for compliance_data in compliance_domains:
            entity = AuditEntity.objects.create(**compliance_data)
            self.stdout.write(f'Created compliance domain: {entity.name} (Parent: {entity.parent.name})')

        # Create some inactive entities to show status filtering
        inactive_entities = [
            {
                'name': 'Legacy Payroll System',
                'entity_type': 'system',
                'description': 'Old payroll system being phased out',
                'parent': created_processes[2],  # Payroll Process
                'owner': users[1],
                'risk_score': 6.0,
                'regulatory_relevance': {'Legacy': True},
                'last_audited': date.today() - timedelta(days=180),
                'is_active': False
            },
            {
                'name': 'Deprecated Vendor Portal',
                'entity_type': 'system',
                'description': 'Old vendor management portal replaced by new system',
                'parent': created_processes[6],  # Supply Chain Management Process
                'owner': users[3],
                'risk_score': 4.5,
                'regulatory_relevance': {'Deprecated': True},
                'last_audited': date.today() - timedelta(days=365),
                'is_active': False
            }
        ]

        # Create inactive entities
        for inactive_data in inactive_entities:
            entity = AuditEntity.objects.create(**inactive_data)
            self.stdout.write(f'Created inactive entity: {entity.name} (Parent: {entity.parent.name})')

        # Summary
        total_entities = AuditEntity.objects.count()
        self.stdout.write(f'\nDemo data creation complete!')
        self.stdout.write(f'Total entities created: {total_entities}')
        self.stdout.write(f'Business Units: {AuditEntity.objects.filter(entity_type="business_unit").count()}')
        self.stdout.write(f'Processes: {AuditEntity.objects.filter(entity_type="process").count()}')
        self.stdout.write(f'Systems: {AuditEntity.objects.filter(entity_type="system").count()}')
        self.stdout.write(f'Vendors: {AuditEntity.objects.filter(entity_type="vendor").count()}')
        self.stdout.write(f'Compliance Domains: {AuditEntity.objects.filter(entity_type="compliance_domain").count()}')
        self.stdout.write(f'Active entities: {AuditEntity.objects.filter(is_active=True).count()}')
        self.stdout.write(f'Inactive entities: {AuditEntity.objects.filter(is_active=False).count()}')
