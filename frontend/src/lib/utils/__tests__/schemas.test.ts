/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest';
import { AssetSchema } from '../schemas';

describe('AssetSchema ITAM Fields', () => {
	it('validates ITAM fields correctly', () => {
		const validAssetData = {
			name: 'Test Asset',
			description: 'Test description',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			type: 'PR',
			// ITAM fields
			asset_type: 'hardware',
			specifications: 'Intel i7, 16GB RAM, 512GB SSD',
			serial_number: 'SN123456789',
			license_key: 'LIC-KEY-123',
			assigned_user: 'john.doe@example.com',
			department: 'IT Department',
			physical_location: 'Building A, Room 101',
			virtual_location: 'AWS us-east-1',
			acquisition_date: '2024-01-15',
			deployment_details: 'Deployed in production',
			maintenance_schedule: 'Monthly maintenance',
			upgrade_history: [{ version: '1.0', date: '2024-01-15' }],
			end_of_life_date: '2025-01-15',
			license_number: 'LIC-2024-001',
			license_type: 'perpetual',
			license_expiry_date: '2025-01-15',
			compliance_status: 'Compliant',
			audit_logs: [{ date: '2024-01-15', action: 'Created' }],
			purchase_cost: 1500.00,
			depreciation_value: 300.00,
			total_cost_of_ownership: 2000.00,
			vendor: 'Dell Technologies',
			warranty: '3 years manufacturer warranty',
			service_history: [{ date: '2024-01-20', type: 'maintenance' }],
			preventive_maintenance: 'Monthly checks',
			sla_details: '99.9% uptime SLA',
			spare_parts: 'Keyboard, mouse, power adapter',
			security_config: { encryption: true, firewall: 'enabled' },
			known_vulnerabilities: [{ cve: 'CVE-2024-001', severity: 'high' }],
			incident_records: [{ date: '2024-01-15', severity: 'medium' }],
			compliance_standards: ['ISO27001', 'SOC2']
		};

		const result = AssetSchema.safeParse(validAssetData);
		expect(result.success).toBe(true);
	});

	it('validates asset_type enum correctly', () => {
		const validTypes = ['hardware', 'software', 'cloud', 'digital'];
		
		validTypes.forEach(type => {
			const assetData = {
				name: 'Test Asset',
				folder: '123e4567-e89b-12d3-a456-426614174000',
				asset_type: type
			};
			
			const result = AssetSchema.safeParse(assetData);
			expect(result.success).toBe(true);
		});
	});

	it('rejects invalid asset_type', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			asset_type: 'invalid_type'
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(false);
		if (!result.success) {
			expect(result.error.issues[0].path).toContain('asset_type');
		}
	});

	it('validates numeric fields correctly', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			purchase_cost: 1500.50,
			depreciation_value: 300.25,
			total_cost_of_ownership: 2000.75
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(true);
	});

	it('rejects negative numeric values', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			purchase_cost: -100.00
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(false);
		if (!result.success) {
			expect(result.error.issues[0].path).toContain('purchase_cost');
		}
	});

	it('validates optional fields as nullable', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			// All ITAM fields are optional and can be null
			asset_type: null,
			specifications: null,
			serial_number: null,
			license_key: null,
			assigned_user: null,
			department: null,
			physical_location: null,
			virtual_location: null,
			acquisition_date: null,
			deployment_details: null,
			maintenance_schedule: null,
			upgrade_history: null,
			end_of_life_date: null,
			license_number: null,
			license_type: null,
			license_expiry_date: null,
			compliance_status: null,
			audit_logs: null,
			purchase_cost: null,
			depreciation_value: null,
			total_cost_of_ownership: null,
			vendor: null,
			warranty: null,
			service_history: null,
			preventive_maintenance: null,
			sla_details: null,
			spare_parts: null,
			security_config: null,
			known_vulnerabilities: null,
			incident_records: null,
			compliance_standards: null
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(true);
	});

	it('validates JSON fields correctly', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			upgrade_history: [
				{ version: '1.0', date: '2024-01-15', description: 'Initial installation' },
				{ version: '1.1', date: '2024-02-15', description: 'Security update' }
			],
			service_history: [
				{ date: '2024-01-20', type: 'maintenance', description: 'Routine check' },
				{ date: '2024-02-10', type: 'repair', description: 'Hardware replacement' }
			],
			security_config: {
				encryption: true,
				firewall: 'enabled',
				antivirus: 'active'
			},
			known_vulnerabilities: [
				{ cve: 'CVE-2024-001', severity: 'high', status: 'patched' },
				{ cve: 'CVE-2024-002', severity: 'medium', status: 'pending' }
			],
			incident_records: [
				{ date: '2024-01-15', severity: 'high', description: 'Security incident' },
				{ date: '2024-02-01', severity: 'low', description: 'Minor issue' }
			],
			compliance_standards: ['ISO27001', 'SOC2', 'PCI-DSS']
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(true);
	});

	it('validates minimal required fields only', () => {
		const minimalAssetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000'
		};
		
		const result = AssetSchema.safeParse(minimalAssetData);
		expect(result.success).toBe(true);
	});

	it('validates string length constraints', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			ref_id: 'A'.repeat(101) // Exceeds max length of 100
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(false);
		if (!result.success) {
			expect(result.error.issues[0].path).toContain('ref_id');
		}
	});

	it('validates URL format for reference_link', () => {
		const validUrlData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			reference_link: 'https://example.com/asset'
		};
		
		const result = AssetSchema.safeParse(validUrlData);
		expect(result.success).toBe(true);
	});

	it('rejects invalid URL format for reference_link', () => {
		const invalidUrlData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			reference_link: 'not-a-valid-url'
		};
		
		const result = AssetSchema.safeParse(invalidUrlData);
		expect(result.success).toBe(false);
		if (!result.success) {
			expect(result.error.issues[0].path).toContain('reference_link');
		}
	});

	it('allows empty reference_link', () => {
		const assetData = {
			name: 'Test Asset',
			folder: '123e4567-e89b-12d3-a456-426614174000',
			reference_link: ''
		};
		
		const result = AssetSchema.safeParse(assetData);
		expect(result.success).toBe(true);
	});
});
