# Migration Instructions for Audit Plan Enhancements

## Issue
The audit plans are showing 500 errors because new database fields haven't been created yet.

## Solution

### If running via Docker:
```bash
# Stop the containers
docker-compose down

# Run migrations
docker-compose run backend python manage.py migrate audits

# Start the containers
docker-compose up -d
```

### If running via startup script:
```bash
# Stop the backend server (Ctrl+C in terminal)

# Navigate to backend directory
cd backend

# Apply the migration
python manage.py migrate audits

# Restart the server
python manage.py runserver
# OR
./startup.sh
```

### If running in production/deployed environment:
Contact your system administrator or use your deployment pipeline to run:
```bash
python manage.py migrate audits
```

## What this migration does:
1. Adds `audit_domain` as a new entity type
2. Adds `auditable_entities` field (many-to-many relationship)
3. Adds `audit_team` field (JSON field for team members)
4. Adds `actual_start` date field
5. Adds `actual_end` date field

## Temporary Fix
The code has been updated to gracefully handle missing fields, so the app won't crash. However, the new features won't work until the migration is applied.

## Verification
After applying the migration, verify by:
1. Navigate to Audit Plans page - should load without errors
2. Create a new audit plan - should see new fields
3. Check that "Audit Domain" is available as an entity type

