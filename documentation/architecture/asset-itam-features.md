# Asset ITAM (IT Asset Management) Features

## Overview

CISO Assistant now includes comprehensive IT Asset Management (ITAM) capabilities that extend the existing Asset model with 30 new fields organized into 6 logical groups. These features enable organizations to track, manage, and maintain their IT assets throughout their entire lifecycle.

## Features

### 1. Inventory Management
- **Asset Type**: Categorize assets as hardware, software, cloud, or digital
- **Specifications**: Detailed technical specifications and configuration details
- **Serial Number**: Unique identifier for physical assets
- **License Key**: Software license information and keys

### 2. Ownership & Location
- **Assigned User**: Current user or owner of the asset
- **Department**: Organizational unit responsible for the asset
- **Physical Location**: Physical location of hardware assets
- **Virtual Location**: Cloud or virtual environment details

### 3. Lifecycle Management
- **Acquisition Date**: When the asset was purchased or acquired
- **Deployment Details**: Information about how the asset was deployed
- **Maintenance Schedule**: Planned maintenance activities and schedules
- **Upgrade History**: JSON field tracking all upgrades and changes
- **End of Life Date**: Planned retirement or replacement date

### 4. Licensing & Compliance
- **License Number**: Unique license identifier
- **License Type**: Type of license (perpetual, subscription, etc.)
- **License Expiry Date**: When the license expires
- **Compliance Status**: Current compliance status
- **Audit Logs**: JSON field tracking all audit activities

### 5. Financial Management
- **Purchase Cost**: Original purchase price
- **Depreciation Value**: Current depreciated value
- **Total Cost of Ownership**: Complete cost including maintenance, support, etc.
- **Vendor**: Asset vendor or manufacturer
- **Warranty**: Warranty terms and conditions

### 6. Operations
- **Service History**: JSON field tracking all service activities
- **Preventive Maintenance**: Scheduled maintenance procedures
- **SLA Details**: Service level agreement information
- **Spare Parts**: Available spare parts inventory

### 7. Security & Risk
- **Security Configuration**: JSON field with security settings
- **Known Vulnerabilities**: JSON field tracking security vulnerabilities
- **Incident Records**: JSON field recording security incidents
- **Compliance Standards**: Standards the asset must comply with

## Technical Implementation

### Backend Changes
- **Model Extension**: Added 30 new fields to the Asset model
- **Validation**: Comprehensive validation for numeric fields and dates
- **API Support**: Full CRUD operations for all ITAM fields
- **Filtering**: Advanced filtering by ITAM fields
- **Search**: Enhanced search capabilities across ITAM fields

### Frontend Changes
- **Form Enhancement**: Organized ITAM fields into collapsible sections
- **Validation**: Client-side validation for all field types
- **Responsive Design**: Mobile-friendly layout with proper grid system
- **User Experience**: Intuitive interface with helpful tooltips and examples

### Database Schema
All ITAM fields are nullable to ensure backward compatibility with existing data. The fields use appropriate Django field types:
- `CharField` for short text fields
- `TextField` for long text fields
- `DateField` for date fields
- `DecimalField` for monetary values
- `JSONField` for structured data

## Usage Examples

### Creating an Asset with ITAM Data
```python
from core.models import Asset
from decimal import Decimal

asset = Asset.objects.create(
    name="Production Server",
    description="Main production web server",
    folder=folder,
    
    # ITAM fields
    asset_type="hardware",
    specifications="Dell PowerEdge R750, 64GB RAM, 2TB SSD",
    serial_number="DL123456789",
    assigned_user="admin@company.com",
    department="IT Infrastructure",
    physical_location="Data Center A, Rack 15",
    acquisition_date="2024-01-15",
    purchase_cost=Decimal("15000.00"),
    vendor="Dell Technologies",
    license_number="LIC-2024-001",
    compliance_status="Compliant"
)
```

### Filtering Assets by ITAM Fields
```python
# Filter by asset type
hardware_assets = Asset.objects.filter(asset_type="hardware")

# Filter by vendor
dell_assets = Asset.objects.filter(vendor__icontains="Dell")

# Filter by department
it_assets = Asset.objects.filter(department="IT Infrastructure")

# Filter by acquisition date range
recent_assets = Asset.objects.filter(
    acquisition_date__gte="2024-01-01",
    acquisition_date__lte="2024-12-31"
)
```

### API Usage
```bash
# Create asset with ITAM data
curl -X POST http://localhost:8000/api/assets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Asset",
    "folder": "folder-uuid",
    "asset_type": "hardware",
    "vendor": "Dell Technologies",
    "purchase_cost": "1500.00",
    "department": "IT"
  }'

# Filter assets by ITAM fields
curl "http://localhost:8000/api/assets/?asset_type=hardware&vendor=Dell"

# Search assets by ITAM fields
curl "http://localhost:8000/api/assets/?search=Dell"
```

## Validation Rules

### Numeric Fields
- All cost fields (purchase_cost, depreciation_value, total_cost_of_ownership) must be non-negative
- Decimal precision is maintained for monetary values

### Date Fields
- Acquisition date cannot be in the future
- End of life date cannot be in the past (unless acquisition date is also provided)
- License expiry date cannot be in the past (unless acquisition date is also provided)
- Cross-field validation ensures logical date relationships

### JSON Fields
- Upgrade history, service history, audit logs, and other JSON fields accept structured data
- Examples provided in the UI to guide users

## Migration

The ITAM fields are added via Django migration and are fully backward compatible. Existing assets will have null values for all new ITAM fields, which can be populated over time.

## Testing

Comprehensive test coverage includes:
- Model field validation
- API endpoint functionality
- Frontend form rendering and validation
- Cross-field validation rules
- Backward compatibility

## Future Enhancements

Potential future enhancements include:
- Asset lifecycle automation
- Integration with external ITAM systems
- Advanced reporting and analytics
- Asset dependency mapping
- Automated compliance checking
- Cost optimization recommendations

## Example Asset JSON

See `asset-itam-example.json` for a complete example of an asset with all ITAM fields populated.

## Support

For questions or issues related to ITAM features, please refer to the main CISO Assistant documentation or contact the development team.
