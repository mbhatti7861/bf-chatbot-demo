# Post-Build Step 510: Generate CKL LZ Account Page

## Overview
Automatically create landing zone account information pages in the knowledge base/wiki (organizational 2.0 space). Pulls data directly from database tables to generate confluence pages.

## Prerequisites

### ⚠️ CRITICAL: Step 400 Must Be Complete
VM execution produces AWS account numbers required for knowledge base page, Welcome Kit, and partner notice.

### Required Roles
Engineer roles in three environments (dev, uat, prod). Authenticate via:
```powershell
.\auth.ps1
```

### Required Tools
- Python 3.6+
- AWS CLI configured
- OKTA CLI
- Java (for Okta authentication)
- Confluence Personal Access Token
- Optional: Jira API token (for automated issue tracking)
- BuildFactory Tools (Jira and DB-Connection utilities)

## System Integrations

✅ **Database**: Pulls from LZ metadata table and CIDR table (no manual YAML files)  
✅ **Confluence**: Automatically creates pages using user token  
✅ **Jira**: Optional automated issue tracking  

## Purpose

Landing zones consist of AWS accounts referenced by account IDs. These IDs are essential for:
- Identity provider role setup
- CICD onboarding
- Security compliance tooling
- Welcome Kit preparation

Previously provided by infrastructure team post-build. Now Build Factory creates these pages by reading directly from LZ build database (DynamoDB).

## Environment Setup

### One-Time Prerequisites Setup
```bash
# Setup tools environment (ONCE EVER)
cd ..\tools
.\setup-environment.ps1

# RESTART your terminal after this step!
```

### Install Project (After Terminal Restart)
```bash
cd ..\adt-ckl-page-generator
.\install.ps1  # Automated install, activates venv automatically
```

### Setup Confluence Credentials (One-Time)
```bash
# Virtual environment already active from install.ps1
adt-ckl-setup
adt-ckl-test  # Verify credentials work
```

## Usage

### Complete Workflow

```bash
# 1. Authenticate to AWS
.\auth.ps1

# 2. Get account IDs from database
adt-ckl get-accounts <lz_name>

# 3. Create Confluence page
adt-ckl create-page <lz_name>

# 4. Create page with Jira integration (optional)
adt-ckl create-page <lz_name> -j
```

### Example
```bash
.\auth.ps1
adt-ckl get-accounts my-landing-zone
adt-ckl create-page my-landing-zone
```

## Output

The script creates a Confluence page in the organizational cloud services space containing:
- Landing zone name and version
- Account IDs for all environments
- Account types (Dev, Test, UAT, Staging, Prod, Services)
- Organizational and business unit information
- Links to related resources

## Validation

### Verify Page Creation
1. Navigate to knowledge base organizational cloud space
2. Search for landing zone name
3. Verify page exists and contains:
   - [ ] All account IDs correct
   - [ ] Account types labeled properly
   - [ ] No placeholder values
   - [ ] Formatting is clean
   - [ ] Links are functional

### Cross-Reference with Database
Compare page content against:
- DynamoDB metadata table
- VM execution output
- CIDR allocation table

## Troubleshooting

### Database Connection Fails
**Solutions:**
- Re-authenticate: `.\auth.ps1`
- Verify role has DynamoDB read access
- Check network connectivity
- Ensure base services account access

### Confluence API Error
**Solutions:**
- Verify personal access token is valid
- Check token hasn't expired
- Ensure Confluence permissions are correct
- Test credentials: `adt-ckl-test`

### Account IDs Not Found
**Solutions:**
- Confirm Step 400 VM execution completed
- Verify LZ name spelling
- Check DynamoDB state table has records
- Ensure metadata was loaded in Step 10

### Page Already Exists
**Solutions:**
- Check if page needs updating vs creating
- Use update command instead of create
- Verify LZ name is unique
- Check for duplicate requests

### Jira Integration Fails
**Solutions:**
- Verify Jira API token is configured
- Check token stored in credential manager
- Ensure Jira connectivity
- Run without `-j` flag if not needed

## Quality Checklist
- [ ] Authenticated to AWS before running
- [ ] LZ name verified correct
- [ ] get-accounts command succeeded
- [ ] Confluence page created successfully
- [ ] Page contains all expected accounts
- [ ] Account IDs match VM output
- [ ] Page link captured for documentation
- [ ] Page accessible to stakeholders

## Next Steps
After page creation:
1. Capture Confluence page URL
2. Include link in Welcome Kit
3. Reference in partner notice email
4. Proceed to Step 520 (Partner Notification)

## Important Notes

### Why This Step Is Critical
- Provides single source of truth for account IDs
- Required by multiple downstream teams
- Referenced in Welcome Kit and partner notice
- Needed for CICD onboarding
- Used by security and compliance teams

### Timing
- Must complete after Step 400 (VM execution)
- Should complete before partner notice (Step 520)
- Required before CICD onboarding (Step 600)
