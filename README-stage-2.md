# Stage 2 — Audit Planning

## Overview

Stage 2 introduces **Audit Planning** functionality that allows you to plan and manage audit engagements based on entities defined in the Audit Universe (Stage 1). This stage provides a complete CRUD interface for creating, managing, and tracking audit plans with full calendar integration.

## Features

### 🎯 Core Functionality
- **Plan Audits**: Create detailed audit plans for entities in your audit universe
- **Timeline Management**: Set planned start and end dates for audit engagements
- **Status Tracking**: Track audit plans through planned → in progress → completed → cancelled
- **Team Assignment**: Assign lead auditors to audit plans
- **Rich Details**: Capture objectives, scope, and resource requirements

### 📅 Calendar Integration
- **Automatic Calendar Events**: Audit plans automatically appear in the calendar view
- **Color-coded by Status**: 
  - `planned` → Tertiary (blue)
  - `in_progress` → Warning (yellow)
  - `completed` → Success (green)
  - `cancelled` → Error (red)
- **Direct Navigation**: Click calendar events to view audit plan details

### 🔍 Advanced Filtering
- **Search**: Full-text search across titles, descriptions, and entity names
- **Status Filter**: Filter by audit plan status
- **Entity Filter**: Filter by specific audit universe entities
- **Lead Auditor Filter**: Filter by assigned lead auditor
- **Date Range**: Filter by planned start/end dates

## Data Model

### AuditPlan Model
```python
class AuditPlan(models.Model):
    entity = models.ForeignKey("AuditEntity", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    planned_start = models.DateField()
    planned_end = models.DateField()
    lead_auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    objectives = models.TextField(blank=True)
    scope = models.TextField(blank=True)
    resources = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Status Choices
- `planned` - Planned
- `in_progress` - In Progress  
- `completed` - Completed
- `cancelled` - Cancelled

## API Endpoints

### Audit Plans
- `GET /api/audits/plans/` - List audit plans with filtering
- `POST /api/audits/plans/` - Create new audit plan
- `GET /api/audits/plans/{id}/` - Get specific audit plan
- `PUT /api/audits/plans/{id}/` - Update audit plan
- `DELETE /api/audits/plans/{id}/` - Delete audit plan

### Query Parameters
- `search` - Full-text search
- `status` - Filter by status
- `entity` - Filter by entity ID
- `lead_auditor` - Filter by lead auditor ID
- `planned_start__gte` - Filter by start date (greater than or equal)
- `planned_end__lte` - Filter by end date (less than or equal)

## Frontend Routes

### Main Routes
- `/audits/planning` - Audit plans list page
- `/audits/planning/new` - Create new audit plan
- `/audits/planning/{id}` - View audit plan details
- `/audits/planning/{id}/edit` - Edit audit plan

### Calendar Integration
- `/calendar/{year}/{month}` - Calendar view with audit plan events
- Events appear as `AP: {plan.title}` with status-based color coding

## File Structure

### Backend Files
```
backend/audits/
├── models.py              # AuditPlan model added
├── serializers.py         # AuditPlanSerializer added
├── views.py              # AuditPlanViewSet added
├── urls.py               # Audit plan routing added
└── migrations/
    └── 0012_add_audit_plan_model.py
```

### Frontend Files
```
frontend/src/
├── lib/modules/audits/planning/
│   ├── api.js                    # API helper functions
│   ├── AuditPlanList.svelte      # List view component
│   ├── AuditPlanForm.svelte      # Create/edit form component
│   └── AuditPlanDetail.svelte    # Detail view component
└── routes/(app)/(internal)/audits/planning/
    ├── +page.svelte              # Main planning page
    ├── new/+page.svelte          # Create new plan
    └── [id]/
        ├── +page.svelte          # Plan detail view
        └── edit/+page.svelte     # Edit plan
```

## Installation & Setup

### 1. Backend Setup
```bash
# Apply database migration
cd backend
poetry run python manage.py migrate

# Verify API endpoints
curl http://localhost:8000/api/audits/plans/
```

### 2. Frontend Setup
```bash
# No additional setup required - routes are automatically registered
# Visit http://localhost:5173/audits/planning
```

### 3. Calendar Integration
```bash
# Calendar automatically includes audit plans
# Visit http://localhost:5173/calendar/2025/10
```

## Usage Examples

### Creating an Audit Plan
1. Navigate to `/audits/planning`
2. Click "New Audit Plan"
3. Select an entity from the audit universe
4. Set title, description, and timeline
5. Define objectives and scope
6. Save the plan

### Viewing in Calendar
1. Navigate to `/calendar/{year}/{month}`
2. Look for `AP: {plan.title}` events
3. Click events to view plan details
4. Events are color-coded by status

### Filtering Plans
1. Use the search box for full-text search
2. Filter by status using the dropdown
3. Filter by entity using the entity dropdown
4. Apply multiple filters simultaneously

## Integration with Stage 1

### Audit Universe Dependencies
- **Entity Selection**: All audit plans must be linked to an existing audit entity
- **Entity Information**: Plan details show entity name, type, and ID
- **Navigation**: Direct links between audit plans and their entities

### Calendar Integration
- **Audit Universe Events**: `AU: {entity.name}` (based on next_audit_date)
- **Audit Plan Events**: `AP: {plan.title}` (based on planned_start)
- **Color Coding**: Different color schemes for entities vs plans

## Validation & Business Rules

### Required Fields
- `title` - Audit plan title
- `entity` - Must reference existing audit entity
- `planned_start` - Start date
- `planned_end` - End date (must be after start date)

### Validation Rules
- Title cannot be empty
- Planned end date must be after planned start date
- Entity must exist in audit universe
- Status must be valid choice

## Future Enhancements

### Potential Stage 3 Features
- **Audit Execution**: Track actual audit progress vs planned
- **Resource Management**: Detailed resource allocation and tracking
- **Team Collaboration**: Multi-user audit team management
- **Document Management**: Attach files and documents to plans
- **Reporting**: Audit plan performance and compliance reporting
- **Notifications**: Email alerts for upcoming audits and deadlines

## Testing

### Manual Testing
1. **Create Plan**: Test form validation and submission
2. **List View**: Test filtering and search functionality
3. **Detail View**: Test edit modal and delete functionality
4. **Calendar**: Verify events appear with correct colors
5. **Navigation**: Test all internal links and routing

### API Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/api/audits/plans/
curl -X POST http://localhost:8000/api/audits/plans/ -d '{"title":"Test Plan","entity":1,"planned_start":"2025-10-01","planned_end":"2025-10-15"}'
```

## Troubleshooting

### Common Issues
1. **Empty Entity Dropdown**: Ensure audit entities exist in the system
2. **Calendar Events Missing**: Check that plans have valid planned_start dates
3. **Permission Errors**: Verify user authentication and permissions
4. **Validation Errors**: Check required fields and date constraints

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify API responses in Network tab
3. Check Django logs for backend errors
4. Validate data in Django admin interface

---

## Summary

Stage 2 successfully implements a complete audit planning system that:
- ✅ Integrates seamlessly with Stage 1 (Audit Universe)
- ✅ Provides full CRUD functionality for audit plans
- ✅ Includes advanced filtering and search capabilities
- ✅ Integrates with the existing calendar system
- ✅ Maintains consistent UI/UX with the rest of the application
- ✅ Follows the same architectural patterns as Stage 1

The audit planning system is now ready for production use and provides a solid foundation for future audit management features.
