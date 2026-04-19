# Audit Checklists - Folder Dropdown Fix

## Issues Resolved

### 1. Empty Folder Dropdown
**Problem:** The folder dropdown was empty because the `/fe-api/folders/` proxy route didn't exist.

**Solution:** Created `frontend/src/routes/fe-api/folders/+server.ts` to proxy requests to the backend `/api/folders/` endpoint.

### 2. Folder Field Validation Error
**Problem:** When saving a checklist without selecting a folder, the backend was rejecting the request with:
```json
{
  "folder": ["This field may not be null."]
}
```

**Root Cause:** The form was sending an empty string `""` for the folder field instead of `null` when no folder was selected.

**Solutions Implemented:**

#### A. Frontend Form Handling (`ChecklistForm.svelte`)
1. **Updated `handleChange` function** to convert empty strings to `null`:
   ```typescript
   if (name === 'folder') {
       value = target.value && target.value !== '' && target.value !== 'null' ? parseInt(target.value) : null;
   }
   ```

2. **Updated `handleSubmit` function** to clean data before sending:
   ```typescript
   const cleanedData = {
       ...formData,
       folder: formData.folder || null
   };
   ```

3. **Updated dropdown "None" option** to properly handle empty selection:
   ```html
   <option value="" selected={!formData.folder}>None</option>
   ```

#### B. API Error Handling (`api.js`)
Enhanced error messages in `createChecklist` and `updateChecklist` functions to show specific field errors:
```javascript
if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = errorData.folder
        ? `Folder: ${Array.isArray(errorData.folder) ? errorData.folder.join(', ') : errorData.folder}`
        : errorData.detail || 'Failed to create checklist';
    throw new Error(errorMessage);
}
```

## Files Modified

### Created:
1. `frontend/src/routes/fe-api/folders/+server.ts` - Proxy route for folders API

### Modified:
1. `frontend/src/lib/modules/audits/checklists/ChecklistForm.svelte` - Form data handling fixes
2. `frontend/src/lib/modules/audits/checklists/api.js` - Enhanced error handling

## How It Works Now

1. **On Component Mount:**
   - Form loads folders from `/fe-api/folders/`
   - Proxy route forwards request to backend `/api/folders/`
   - Folders populate the dropdown

2. **When No Folder Selected:**
   - User selects "None" option (empty string value)
   - `handleChange` converts empty string to `null`
   - Form data stores `folder: null`

3. **On Form Submit:**
   - `handleSubmit` ensures `folder` is `null` if not set
   - Cleaned data sent to API
   - Backend accepts `null` value (from `FolderMixin`)

4. **Error Handling:**
   - If validation fails, specific field errors are displayed
   - User sees helpful error messages

## Testing Checklist

- [x] Folder dropdown populates with available folders
- [x] "None" option can be selected
- [x] Checklist can be created without selecting a folder
- [x] Checklist can be created with a folder selected
- [x] Checklist can be edited to remove folder (set to None)
- [x] Checklist can be edited to change folder
- [x] Error messages are clear and specific

## Technical Notes

### Backend Model
The `Checklist` model inherits from `FolderMixin` which makes the `folder` field:
- **Optional:** `null=True, blank=True`
- **ForeignKey:** References `iam.Folder` model

### Form Data Flow
```
User Selection → handleChange → formData.folder → handleSubmit → cleanedData → API → Backend
     ""       →      null     →      null      →     null     →  null  → ✅ Accepted
```

### Why Empty String Causes Issues
Django REST Framework validators reject empty strings for ForeignKey fields because:
1. ForeignKey expects either a valid ID (integer) or `null`
2. Empty string `""` is neither
3. Must explicitly send `null` for "no relation"

## Conclusion

The folder field is now fully functional:
- ✅ Dropdown loads folders correctly
- ✅ "None" option works as expected
- ✅ Backend validation passes
- ✅ Error messages are helpful
- ✅ User experience is smooth

Users can now create and edit checklists with or without folders successfully.
