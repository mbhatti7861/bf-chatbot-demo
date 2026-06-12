# Pre-Build Step 10: Prepare LZ Order for Build

## Overview
Create four landing zone order files from service request data: parameter file, metadata file, feature file, and release file.

## Prerequisites
- Cloud engineer role access (3 accounts)
- Service request platform access
- Version control repository access
- Document repository with synced local folder
- Python environment with dependencies installed

## Process Summary

### 1. Validate Service Request Data
- Add tracking tag in service request system
- Verify all required fields complete
- Check LZ name doesn't already exist
- Validate configuration items (CIs) match account environments
- Verify business unit against application registration
- Cross-reference with organizational mapping docs
- Contact requestor for clarifications

### 2. Setup Environment
```bash
# Authenticate
.\auth.ps1

# Start automation tool
python src/main.py
```

### 3. Create Parameter File
- Select "Direct Import" → "Customer Intake"
- Find LZ name and click "Configure"
- Verify form data
- Click "Create Parameter Template"
- Tool generates: `<lz_name>_parm.yml`

### 4. Manual Review & Edits
Verify critical parameters:
- `organizational_unit` - correct OU format
- `business_unit` - correct BU abbreviation
- YAML syntax valid
- No placeholder values

### 5. Generate Artifacts
- Click "Artifacts" button for this LZ
- Tool creates three additional files:
  - `<lz_name>_meta.yml`
  - `<lz_name>_feature.html`
  - `<lz_name>_release.html`

### 6. Verify Document Upload
Confirm all 4 files copied to document repository:
- Parameters folder
- Metadata folder
- Features folder
- Releases folder

### 7. Update Project Management Feature
Auto-created feature location: Pre-Build task data block in service request

Update required fields:
- Add fix version
- Add file links to description (metadata, feature, release, parameter)
- Remove "- NOT READY" flag from title and feature name
- Verify description format matches previous features
- Ensure lowercase LZ name

### 8. Complete & Notify
- Mark Build Prep task complete in service request
- Send email to application team contacts for observability onboarding
- Notify build team in chat that feature is ready

## Common Issues

**Business Unit Mismatch**: Use organizational reference docs, not application registration if they differ

**File Not Uploading**: Verify OneDrive sync status, manually upload if needed

**Missing CI**: Contact requestor, don't proceed without complete CI data

**YAML Errors**: Check indentation (spaces not tabs) and special characters

## Quality Checks
- [ ] LZ name validated (no duplicates)
- [ ] CIs match environments
- [ ] Business unit verified
- [ ] All 4 files generated
- [ ] Files in document repository
- [ ] Project feature updated and marked ready
- [ ] Service request task completed
