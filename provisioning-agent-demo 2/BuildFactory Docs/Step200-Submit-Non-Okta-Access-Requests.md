# Pre-Build Step 200: Submit Non-Okta Access Role Requests

## Overview
Register new IAM roles for landing zones in the identity provider and assign approver groups for access request workflows. Only engineer and compliance roles require access for QA automation.

## Prerequisites
- Cloud engineer role access
- API tokens stored in OS credential manager (encrypted)
- Cloud credentials in standard config location
- Access to metadata database table
- Access to project management system
- Spreadsheet automation repository cloned

## Approver Group Strategy
- **CFS-Owned Roles**: Use CFS approver group
- **Customer-Owned Roles**: Initially use internal approver group for QA access
- **Post-QA**: Reassign approver group to customer's designated group

This eliminates waiting for customer approval before QA testing.

## Environment Setup
```bash
# Clone repository
git clone <fi-spreadsheet-repo-url>
cd lz_fi_spreadsheet_build

# Authenticate
.\auth.ps1

# Activate virtual environment
fi-venv\Scripts\activate
```

## Automated Process (Recommended)

### Generate Spreadsheet for Single Landing Zone
```bash
lz-fi-gen -n <lz_name>
```

### Generate for Multiple Landing Zones
```bash
lz-fi-gen -n lz1 lz2 lz3
```

### What the Tool Does
✅ Queries database for LZ metadata  
✅ Optionally connects to project management:
  - Finds feature by LZ name
  - Locates Step 200 task
  - Moves to 'In Development'
  - Assigns to current user
  - Retrieves engineer emails

✅ Loads Excel template  
✅ Generates spreadsheet entries (OKTA or non-OKTA)  
✅ Saves to output directory with timestamp  
✅ Validates every cell:
  - Business logic checks
  - CICD handling
  - Approver group assignments
  - Special column validation

## Submit Request

### Access Request Form
Use the identity management group request form to submit the spreadsheet.

### Required Fields
- **Requested For**: Person submitting (not customer)
- **Request Type**: "Create Non-AWS Okta Group"
- **Business Justification**: "Compliance, security, and observability roles required for newly built cloud landing zones"
- **File Upload**: Attach generated spreadsheet from output directory
  - Format: `Create non-AWS OKTA FedIdentity Group-{lz_name}.xlsx`
- **Desired Date**: Same as estimated date (unless escalation needed)

### Post-Submission
Update project management story with request ticket number.

## Validation

### Automated Validation
Use automated validation process (see Post-Build Step 900) to verify:
- Roles created correctly
- Entitlements assigned
- Privilege access configured

### Manual Validation Checklist
- [ ] All roles exist in identity provider
- [ ] Approver groups assigned correctly
- [ ] Entitlements mapped properly
- [ ] Privilege access configured

## Handling Issues

### Missing Roles or Entitlements

**If validation finds missing items:**

1. **Open Incident Ticket**
   - Assign to cloud access management team
   - Include details of missing roles/entitlements
   - Reference original request ticket

2. **Create Project Defect**
   - Link to LZ story
   - Include incident ticket number
   - Document missing items

3. **Update Story Task**
   - Add incident ticket number
   - Add defect ticket number
   - Document in discussions/comments

### Request Modifications

**To modify existing OKTA roles:**

1. Submit new request with type: "Modify Okta Group"
2. Create new spreadsheet with:
   - Current approver group
   - New approver group
3. Use helper script or manual template
4. Submit via same request form

**Important**: All compliance roles should use CFS approver group.

## Troubleshooting

### Authentication Fails
- Re-run authentication script
- Verify credentials are valid
- Check role access in identity provider

### Virtual Environment Issues
- Verify Python is installed
- Check venv exists: `fi-venv/`
- Try recreating venv if corrupted

### Landing Zone Not Found
- Verify LZ name spelling
- Check LZ exists in metadata database
- Ensure metadata was imported in Step 10

### Permission Errors
- Verify repository access
- Check database read permissions
- Confirm API token is valid

### Spreadsheet Generation Fails
- Check terminal output for specific errors
- Verify LZ metadata is complete
- Ensure CIDR generation (Step 100) completed
- Validate required fields populated

## Data Flow
1. Check cloud credentials (must be valid)
2. Query database for LZ metadata
3. Optional: Update project management task
4. Load Excel template
5. Generate spreadsheet entries
6. Save with timestamp to output directory
7. Validate all cells and business logic
8. Ready for submission

## Quality Checks
- [ ] Authenticated before running tool
- [ ] Spreadsheet generated without errors
- [ ] All validation checks passed
- [ ] Approver groups assigned correctly
- [ ] CICD landing zones handled properly
- [ ] Spreadsheet saved to output directory
- [ ] Request submitted in identity management system
- [ ] Project story updated with request number
