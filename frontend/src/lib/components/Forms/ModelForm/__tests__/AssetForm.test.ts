/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import AssetForm from '../AssetForm.svelte';
import type { SuperValidated } from 'sveltekit-superforms';

// Mock the paraglide messages
vi.mock('$paraglide/messages', () => ({
	m: {
		assetClass: () => 'Asset Class',
		refId: () => 'Reference ID',
		owner: () => 'Owner',
		domain: () => 'Domain',
		parentAssets: () => 'Parent Assets',
		link: () => 'Link',
		linkHelpText: () => 'Link help text',
		securityObjectives: () => 'Security Objectives',
		disasterRecoveryObjectives: () => 'Disaster Recovery Objectives',
		labels: () => 'Labels',
		labelsHelpText: () => 'Labels help text',
		observation: () => 'Observation',
		observationHelpText: () => 'Observation help text',
		ebiosRmStudies: () => 'EBIOS RM Studies',
		// ITAM field translations
		inventory: () => 'Inventory',
		assetType: () => 'Asset Type',
		specifications: () => 'Specifications',
		serialNumber: () => 'Serial Number',
		licenseKey: () => 'License Key',
		ownershipLocation: () => 'Ownership & Location',
		assignedUser: () => 'Assigned User',
		department: () => 'Department',
		physicalLocation: () => 'Physical Location',
		virtualLocation: () => 'Virtual Location',
		lifecycle: () => 'Lifecycle',
		acquisitionDate: () => 'Acquisition Date',
		endOfLifeDate: () => 'End of Life Date',
		deploymentDetails: () => 'Deployment Details',
		maintenanceSchedule: () => 'Maintenance Schedule',
		upgradeHistory: () => 'Upgrade History',
		licensingCompliance: () => 'Licensing & Compliance',
		licenseNumber: () => 'License Number',
		licenseType: () => 'License Type',
		licenseExpiryDate: () => 'License Expiry Date',
		complianceStatus: () => 'Compliance Status',
		auditLogs: () => 'Audit Logs',
		financials: () => 'Financials',
		purchaseCost: () => 'Purchase Cost',
		depreciationValue: () => 'Depreciation Value',
		totalCostOfOwnership: () => 'Total Cost of Ownership',
		vendor: () => 'Vendor',
		warranty: () => 'Warranty',
		operations: () => 'Operations',
		serviceHistory: () => 'Service History',
		preventiveMaintenance: () => 'Preventive Maintenance',
		slaDetails: () => 'SLA Details',
		spareParts: () => 'Spare Parts',
		securityRisk: () => 'Security & Risk',
		securityConfig: () => 'Security Configuration',
		knownVulnerabilities: () => 'Known Vulnerabilities',
		incidentRecords: () => 'Incident Records',
		complianceStandards: () => 'Compliance Standards'
	}
}));

// Mock the page store
vi.mock('$app/state', () => ({
	page: {
		data: {
			settings: {
				security_objective_scale: '0-3'
			}
		}
	}
}));

// Mock fetch for API calls
global.fetch = vi.fn();

describe('AssetForm ITAM Fields', () => {
	let mockForm: SuperValidated<any>;
	let mockModel: any;

	beforeEach(() => {
		// Mock form data
		mockForm = {
			valid: true,
			errors: {},
			data: {
				name: '',
				description: '',
				folder: '',
				asset_type: '',
				specifications: '',
				serial_number: '',
				license_key: '',
				assigned_user: '',
				department: '',
				physical_location: '',
				virtual_location: '',
				acquisition_date: '',
				deployment_details: '',
				maintenance_schedule: '',
				upgrade_history: null,
				end_of_life_date: '',
				license_number: '',
				license_type: '',
				license_expiry_date: '',
				compliance_status: '',
				audit_logs: null,
				purchase_cost: null,
				depreciation_value: null,
				total_cost_of_ownership: null,
				vendor: '',
				warranty: '',
				service_history: null,
				preventive_maintenance: '',
				sla_details: '',
				spare_parts: '',
				security_config: null,
				known_vulnerabilities: null,
				incident_records: null,
				compliance_standards: null
			}
		} as SuperValidated<any>;

		// Mock model data
		mockModel = {
			selectOptions: {
				type: [
					{ label: 'Primary', value: 'PR' },
					{ label: 'Supporting', value: 'SU' }
				]
			}
		};

		// Mock fetch responses
		(global.fetch as any).mockResolvedValue({
			json: () => Promise.resolve([])
		});
	});

	it('renders all ITAM field sections', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		// Wait for async operations to complete
		await waitFor(() => {
			expect(screen.getByText('Inventory')).toBeInTheDocument();
			expect(screen.getByText('Ownership & Location')).toBeInTheDocument();
			expect(screen.getByText('Lifecycle')).toBeInTheDocument();
			expect(screen.getByText('Licensing & Compliance')).toBeInTheDocument();
			expect(screen.getByText('Financials')).toBeInTheDocument();
			expect(screen.getByText('Operations')).toBeInTheDocument();
			expect(screen.getByText('Security & Risk')).toBeInTheDocument();
		});
	});

	it('renders inventory fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Asset Type')).toBeInTheDocument();
			expect(screen.getByLabelText('Serial Number')).toBeInTheDocument();
			expect(screen.getByLabelText('Specifications')).toBeInTheDocument();
			expect(screen.getByLabelText('License Key')).toBeInTheDocument();
		});
	});

	it('renders ownership & location fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Assigned User')).toBeInTheDocument();
			expect(screen.getByLabelText('Department')).toBeInTheDocument();
			expect(screen.getByLabelText('Physical Location')).toBeInTheDocument();
			expect(screen.getByLabelText('Virtual Location')).toBeInTheDocument();
		});
	});

	it('renders lifecycle fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Acquisition Date')).toBeInTheDocument();
			expect(screen.getByLabelText('End of Life Date')).toBeInTheDocument();
			expect(screen.getByLabelText('Deployment Details')).toBeInTheDocument();
			expect(screen.getByLabelText('Maintenance Schedule')).toBeInTheDocument();
			expect(screen.getByLabelText('Upgrade History')).toBeInTheDocument();
		});
	});

	it('renders licensing & compliance fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('License Number')).toBeInTheDocument();
			expect(screen.getByLabelText('License Type')).toBeInTheDocument();
			expect(screen.getByLabelText('License Expiry Date')).toBeInTheDocument();
			expect(screen.getByLabelText('Compliance Status')).toBeInTheDocument();
			expect(screen.getByLabelText('Audit Logs')).toBeInTheDocument();
		});
	});

	it('renders financial fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Purchase Cost')).toBeInTheDocument();
			expect(screen.getByLabelText('Depreciation Value')).toBeInTheDocument();
			expect(screen.getByLabelText('Total Cost of Ownership')).toBeInTheDocument();
			expect(screen.getByLabelText('Vendor')).toBeInTheDocument();
			expect(screen.getByLabelText('Warranty')).toBeInTheDocument();
		});
	});

	it('renders operations fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Service History')).toBeInTheDocument();
			expect(screen.getByLabelText('Preventive Maintenance')).toBeInTheDocument();
			expect(screen.getByLabelText('SLA Details')).toBeInTheDocument();
			expect(screen.getByLabelText('Spare Parts')).toBeInTheDocument();
		});
	});

	it('renders security & risk fields correctly', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			expect(screen.getByLabelText('Security Configuration')).toBeInTheDocument();
			expect(screen.getByLabelText('Known Vulnerabilities')).toBeInTheDocument();
			expect(screen.getByLabelText('Incident Records')).toBeInTheDocument();
			expect(screen.getByLabelText('Compliance Standards')).toBeInTheDocument();
		});
	});

	it('handles asset type selection', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			const assetTypeSelect = screen.getByLabelText('Asset Type');
			expect(assetTypeSelect).toBeInTheDocument();

			// Check that it's a select element
			expect(assetTypeSelect.tagName).toBe('SELECT');
		});
	});

	it('handles date input fields', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			const acquisitionDateInput = screen.getByLabelText('Acquisition Date');
			const endOfLifeDateInput = screen.getByLabelText('End of Life Date');
			const licenseExpiryDateInput = screen.getByLabelText('License Expiry Date');

			expect(acquisitionDateInput).toBeInTheDocument();
			expect(endOfLifeDateInput).toBeInTheDocument();
			expect(licenseExpiryDateInput).toBeInTheDocument();

			// Check that they are date inputs
			expect(acquisitionDateInput).toHaveAttribute('type', 'date');
			expect(endOfLifeDateInput).toHaveAttribute('type', 'date');
			expect(licenseExpiryDateInput).toHaveAttribute('type', 'date');
		});
	});

	it('handles number input fields for costs', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			const purchaseCostInput = screen.getByLabelText('Purchase Cost');
			const depreciationValueInput = screen.getByLabelText('Depreciation Value');
			const totalCostInput = screen.getByLabelText('Total Cost of Ownership');

			expect(purchaseCostInput).toBeInTheDocument();
			expect(depreciationValueInput).toBeInTheDocument();
			expect(totalCostInput).toBeInTheDocument();

			// Check that they are number inputs
			expect(purchaseCostInput).toHaveAttribute('type', 'number');
			expect(depreciationValueInput).toHaveAttribute('type', 'number');
			expect(totalCostInput).toHaveAttribute('type', 'number');
		});
	});

	it('handles textarea fields for multi-line text', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			const specificationsTextarea = screen.getByLabelText('Specifications');
			const deploymentDetailsTextarea = screen.getByLabelText('Deployment Details');
			const maintenanceScheduleTextarea = screen.getByLabelText('Maintenance Schedule');

			expect(specificationsTextarea).toBeInTheDocument();
			expect(deploymentDetailsTextarea).toBeInTheDocument();
			expect(maintenanceScheduleTextarea).toBeInTheDocument();

			// Check that they are textarea elements
			expect(specificationsTextarea.tagName).toBe('TEXTAREA');
			expect(deploymentDetailsTextarea.tagName).toBe('TEXTAREA');
			expect(maintenanceScheduleTextarea.tagName).toBe('TEXTAREA');
		});
	});

	it('shows help text for JSON fields', async () => {
		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' }
			}
		});

		await waitFor(() => {
			// Check that JSON format help text is present
			expect(screen.getByText(/JSON format:/)).toBeInTheDocument();
		});
	});

	it('handles form data binding', async () => {
		const formDataCache = {};

		render(AssetForm, {
			props: {
				form: mockForm,
				model: mockModel,
				data: { type: 'PR' },
				formDataCache
			}
		});

		await waitFor(() => {
			const serialNumberInput = screen.getByLabelText('Serial Number');
			const vendorInput = screen.getByLabelText('Vendor');

			// Test that inputs can be interacted with
			fireEvent.input(serialNumberInput, { target: { value: 'SN123456789' } });
			fireEvent.input(vendorInput, { target: { value: 'Dell Technologies' } });

			expect(serialNumberInput).toHaveValue('SN123456789');
			expect(vendorInput).toHaveValue('Dell Technologies');
		});
	});
});
