# Workpapers & Evidence Module

This module provides a comprehensive system for managing audit workpapers and evidence with an approval workflow.

## Overview

The Workpapers & Evidence module enables organizations to:

1. **Upload and store workpapers** - Support for Excel, Word, PDF, images, and external links
2. **Attach evidence to audits** - Associate files and links to audit engagements and findings
3. **Evidence approval workflow** - Three-state workflow: collected → reviewed → approved

## Features

### File Management
- Support for multiple file types: Excel (.xlsx, .xls), Word (.doc, .docx), PDF, images (.jpg, .png, .gif)
- File size tracking and validation
- External link support for cloud-hosted documents
- Optional S3/MinIO object storage support

### Metadata & Organization
- Customizable tags for categorization
- JSON metadata storage for additional context
- Version tracking
- Full-text search across title and description

### Approval Workflow

**States:**
- **Collected** - Initial state when workpaper is created
- **Reviewed** - Workpaper has been submitted for review
- **Approved** - Workpaper has been approved by an approver

**Actions:**
- `submit_for_review()` - Move from collected → reviewed
- `approve(user, comments)` - Move from reviewed → approved
- `reject(user, reason)` - Reject with reason (status unchanged)

**Audit Trail:**
- Complete approval history tracked in `WorkpaperApproval` model
- Records action, user, timestamp, and comments for each status change

## Models

### Workpaper

Main model for storing workpaper information.

**Key Fields:**
- `title` (required) - Workpaper title
- `description` - Detailed description
- `workpaper_type` - Type of workpaper (excel, word, pdf, image, link, other)
- `file` - FileField for uploaded files
- `file_size` - Automatically calculated file size in bytes
- `external_link` - URL for external documents
- `tags` - JSONField for categorization tags
- `metadata` - JSONField for additional metadata
- `status` - Current workflow status
- `uploaded_by` - User who created the workpaper
- `reviewer` - User who reviewed the workpaper
- `reviewed_at` - Timestamp of review
- `approver` - User who approved the workpaper
- `approved_at` - Timestamp of approval
- `rejection_reason` - Reason for rejection (if rejected)
- `version` - Version number
- `is_active` - Whether workpaper is active

**Methods:**
- `submit_for_review(user)` - Submit for review
- `approve(user, comments)` - Approve workpaper
- `reject(user, reason)` - Reject workpaper
- `can_be_reviewed()` - Check if can be reviewed
- `can_be_approved()` - Check if can be approved
- `get_file_extension()` - Get file extension
- `get_file_name()` - Get file name without path

### WorkpaperApproval

Tracks approval workflow history.

**Key Fields:**
- `workpaper` - Associated workpaper
- `action` - Action performed (submit_for_review, reviewed, approved, rejected)
- `action_by` - User who performed the action
- `comments` - Comments about the action
- `previous_status` - Status before the action
- `new_status` - Status after the action
- `created_at` - Timestamp of the action

## API Endpoints

### Workpapers

**List Workpapers**
```
GET /api/workpapers/workpapers/
```
Query parameters:
- `status` - Filter by status (collected, reviewed, approved)
- `workpaper_type` - Filter by type (excel, word, pdf, image, link, other)
- `uploaded_by` - Filter by uploader user ID
- `reviewer` - Filter by reviewer user ID
- `approver` - Filter by approver user ID
- `my_uploads` - Filter to current user's uploads (true/false)
- `pending_review` - Filter to pending review items (true/false)
- `tag` - Filter by tag
- `search` - Full-text search in title and description

**Get Workpaper**
```
GET /api/workpapers/workpapers/{id}/
```

**Create Workpaper**
```
POST /api/workpapers/workpapers/
```
Body:
```json
{
  "title": "Q1 2024 Audit Evidence",
  "description": "Financial audit evidence for Q1",
  "workpaper_type": "pdf",
  "external_link": "",
  "tags": ["audit", "finance", "Q1-2024"],
  "is_active": true
}
```

**Update Workpaper**
```
PUT /api/workpapers/workpapers/{id}/
```

**Delete Workpaper**
```
DELETE /api/workpapers/workpapers/{id}/
```

### File Operations

**Upload File**
```
POST /api/workpapers/workpapers/{id}/upload_file/
Content-Type: multipart/form-data

file: [file data]
```

**Delete File**
```
DELETE /api/workpapers/workpapers/{id}/delete_file/
```

### Workflow Actions

**Submit for Review**
```
POST /api/workpapers/workpapers/{id}/submit_for_review/
```

**Review Workpaper**
```
POST /api/workpapers/workpapers/{id}/review/
```
Body:
```json
{
  "comments": "Optional review comments"
}
```

**Approve Workpaper**
```
POST /api/workpapers/workpapers/{id}/approve/
```
Body:
```json
{
  "action": "approve",
  "comments": "Optional approval comments"
}
```

**Reject Workpaper**
```
POST /api/workpapers/workpapers/{id}/reject/
```
Body:
```json
{
  "action": "reject",
  "reason": "Rejection reason (required)"
}
```

**Get Approval History**
```
GET /api/workpapers/workpapers/{id}/approval_history/
```

### Approvals

**List Approval History**
```
GET /api/workpapers/approvals/
```
Query parameters:
- `workpaper` - Filter by workpaper ID
- `action` - Filter by action type
- `action_by` - Filter by user ID

## Frontend Integration

### Routes
- `/workpapers` - Main list view with search and filters
- `/workpapers/{id}` - Detail view with approval actions

### Components
- `WorkpaperForm.svelte` - Create/edit form
- `WorkpaperList.svelte` - List with tabs and filters
- `WorkpaperCard.svelte` - Detailed view
- `WorkpaperActions.svelte` - Workflow action buttons

### API Client
Import from `$lib/modules/workpapers/api.js`:
- `listWorkpapers(params)`
- `getWorkpaper(id)`
- `createWorkpaper(data)`
- `updateWorkpaper(id, data)`
- `deleteWorkpaper(id)`
- `uploadFile(id, file)`
- `deleteFile(id)`
- `submitForReview(id)`
- `reviewWorkpaper(id, comments)`
- `approveWorkpaper(id, comments)`
- `rejectWorkpaper(id, reason)`
- `getApprovalHistory(id)`
- `listApprovals(params)`

## Usage Examples

### Create Workpaper with File Upload

```python
# Backend
from workpapers.models import Workpaper

workpaper = Workpaper.objects.create(
    title="Audit Evidence 2024",
    description="Supporting documents for annual audit",
    workpaper_type="pdf",
    uploaded_by=request.user
)

# Frontend
const data = {
    title: "Audit Evidence 2024",
    description: "Supporting documents for annual audit",
    workpaper_type: "pdf"
};

const workpaper = await createWorkpaper(data);

if (file) {
    await uploadFile(workpaper.id, file);
}
```

### Workflow Example

```python
# Backend
workpaper = Workpaper.objects.get(id=1)

# Submit for review
workpaper.submit_for_review(reviewer_user)

# Approve
workpaper.approve(approver_user, "All evidence is complete")

# Or reject
workpaper.reject(approver_user, "Missing transaction details")

# Frontend
await submitForReview(workpaperId);
await approveWorkpaper(workpaperId, "All evidence is complete");
await rejectWorkpaper(workpaperId, "Missing transaction details");
```

### Filter Workpapers

```javascript
// Get all approved workpapers
const approvedWorkpapers = await listWorkpapers({ status: 'approved' });

// Get my uploads that are pending review
const myPendingWorkpapers = await listWorkpapers({
    my_uploads: 'true',
    pending_review: 'true'
});

// Search by tag
const auditWorkpapers = await listWorkpapers({ tag: 'audit' });
```

## Testing

Run tests:
```bash
cd backend
poetry run python manage.py test workpapers
```

Test files:
- `tests/test_models.py` - Model logic and workflow tests
- `tests/test_api.py` - API endpoint tests

## Future Enhancements

The module includes placeholders and comments for future integrations:

1. **Link to AuditEngagement** - Associate workpapers with specific audit engagements
2. **Link to Test/Finding records** - When test and finding models are created
3. **Evidence Approver role** - Dedicated IAM role for evidence approval
4. **Advanced file preview** - In-browser preview for supported file types
5. **Bulk operations** - Upload and approve multiple workpapers at once
6. **Export** - Generate reports with all workpapers for an audit

## Configuration

### File Upload Settings

Edit `backend/ciso_assistant/settings.py`:

```python
# Local storage
MEDIA_ROOT = LOCAL_STORAGE_DIRECTORY
MEDIA_URL = ""

# Or S3 storage
USE_S3 = os.getenv("USE_S3", "False") == "True"
if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
    }
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
```

### File Size Limits

```python
ATTACHMENT_MAX_SIZE_MB = os.environ.get("ATTACHMENT_MAX_SIZE_MB", 25)
```

## License

Part of the CISO Assistant Community project. See main LICENSE file for details.
