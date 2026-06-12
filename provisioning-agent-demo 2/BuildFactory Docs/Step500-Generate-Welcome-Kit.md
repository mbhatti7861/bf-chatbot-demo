# Post-Build Step 500: Generate Welcome Kit

## Overview
Automate AWS Landing Zone onboarding documentation by retrieving data from DynamoDB and ServiceNow, generating resource identifiers, and producing HTML, PDF, and Confluence outputs. Critical step that triggers downstream onboarding with other teams.

## Prerequisites

### ⚠️ CRITICAL: Step 400 Must Be Complete
Step 400 produces AWS account numbers required for the Welcome Kit. **This is a vital step that drives all work after Step 300.**

### Required Roles
Request via FedIdentity in base services account:
- Build Factory database auth roles (2 accounts for engineer access)
- CLI session capability for assumed roles

### Required Tools
- Python 3.12+
- wkhtmltopdf (for PDF generation)
- AWS credentials with DynamoDB access
- Azure AD app registration (for SharePoint upload)
- Optional: Jira API token (for automated issue tracking)
- BuildFactory Tools (Jira and DB connection utilities)

## System Integrations

✅ **Database**: Pulls data from LZ metadata table (no manual YAML files needed)  
✅ **Project Management**: Updates issues, assigns tasks, retrieves engineer emails  
✅ **ServiceNow**: Retrieves application service tags via Lambda  
✅ **SharePoint**: Automatic archival of generated documents  
✅ **Multi-Platform**: Dynamic path resolution for different environments  
✅ **Secure**: Uses OS credential manager for API tokens  
✅ **Shareable Links**: Configurable link generation for distribution  

## Architecture

### Data Flow
```
1. Authenticate via SAML
2. Query metadata from DynamoDB (lz_metadata_table)
3. Invoke Lambda function to retrieve ServiceNow CMDB data
4. Lambda securely accesses ServiceNow credentials from Secrets Manager
5. Lambda queries CMDB for application service tags
6. Return CMDB data to application
7. Generate HTML, PDF, and Confluence documents locally
8. Archive documents to SharePoint
```

### Components
- **CLI Application**: `gen_welcomepacket.py` (main orchestrator)
- **Database Module**: `BuildFactoryData.py` (DynamoDB queries)
- **Lambda Invoke**: `LambdaInvoke.py` (ServiceNow relay)
- **Templates**: Jinja2 templates for HTML/PDF/Confluence
- **PDF Generator**: PDFKit for document conversion

### Cloud Resources
- Lambda Function: ServiceNow relay service
- Secrets Manager: ServiceNow credentials
- DynamoDB: LZ metadata table
- CloudWatch Logs: Lambda execution logs
- IAM: Roles and policies for access

## Environment Setup

### 1. Clone Repository
```bash
git clone <welcome-kit-generator-v3-repo-url>
cd welcome-kit-generator-v3
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install wkhtmltopdf
Download and install wkhtmltopdf for your OS. Must be in system PATH.

### 4. Configure AWS Credentials
```bash
# Authenticate
.\auth.ps1

# Or manually configure AWS CLI profiles
aws configure --profile <engineer-role-profile>
```

### 5. Setup API Tokens (Optional)
For Jira integration:
- Store API token in Windows Credential Manager
- Token will be encrypted and secured

## Data Elements

### Retrieved from DynamoDB
- `lz_name` - Landing zone name (partition key)
- `accounts` - Account IDs and types
- `organizational_unit` - Organizational unit (short name)
- `business_unit` - Business unit (short name)
- `primary_gitlab_owner_email` - Primary GitLab owner
- `secondary_gitlab_owner_email` - Secondary GitLab owner
- `dynatrace_ad_group` - Monitoring platform AD group

### Retrieved from ServiceNow (via Lambda)
- `app_service_tag` - Application service tags from CMDB

### Generated Resource Names
All follow organizational naming conventions:

**GitLab Repository Link:**
```
https://gitlab.<domain>/<lz_name>
```

**Compliance Service Application:**
```
cfs-<lz_name>-lz-def
```

**Compliance Service Contexts:**
```
cfs-base01-gov.<lz_name>.<account_type>
```

**Terraform State Buckets:**
```
cicd-adt-tf-state-<customer_id_slug>-<lz_name>-<account_type>-bucket
```

**DynamoDB State Lock Table:**
```
cicd-adt-tf-state-<customer_id_slug>-dynamo
```

## Usage

### Generate Welcome Kit for Single Landing Zone
```bash
python gen_welcomepacket.py <lz_name>
```

### Batch Processing (Multiple Landing Zones)
```bash
python gen_welcomepacket.py <lz_name1> <lz_name2> <lz_name3>
```

### Output Files Generated
For each landing zone, three files are created:

1. **HTML**: `<lz_name>_welcome_kit.html`
   - Web-viewable format
   - Contains all account information, links, and configuration details

2. **PDF**: `<lz_name>_welcome_kit.pdf`
   - Print-ready format
   - Generated from HTML template
   - Includes all sections from HTML version

3. **Confluence**: `<lz_name>_confluence.html`
   - Formatted for Confluence wiki
   - Easy to paste into Confluence pages
   - Maintains formatting and links

### Output Location
```
output/
├── <lz_name>_welcome_kit.html
├── <lz_name>_welcome_kit.pdf
└── <lz_name>_confluence.html
```

## Welcome Kit Contents

### Account Information Section
- Account IDs for all environments
- Account names and types (Dev, Test, UAT, Staging, Prod)
- Services accounts (Prod/Non-Prod)

### Compliance & Governance
- MCS compliance contexts for each account
- Compliance service application name
- Terraform state bucket names
- DynamoDB state lock table name

### Access & Ownership
- Primary GitLab owner (name and email)
- Secondary GitLab owner (name and email)
- Support group information
- Monitoring platform AD group

### Repository & Automation
- GitLab repository link
- Terraform state locations
- State lock table information

### Application Services
- Application service tags from CMDB
- Application CI references
- Support team information

### Monitoring & Observability
- Monitoring platform access information
- Observability role ARNs (optional)
- Log aggregation details

## Validation

### Verify Welcome Kit Contents
Review generated files for:
- [ ] All account IDs present and correct
- [ ] GitLab owner emails valid
- [ ] Compliance contexts match account structure
- [ ] State bucket names follow conventions
- [ ] Application service tags retrieved successfully
- [ ] Links are functional
- [ ] PDF renders correctly
- [ ] Confluence format preserves structure

### Data Quality Checks
- [ ] No placeholder values remaining
- [ ] All emails resolve in directory
- [ ] Account IDs match VM output
- [ ] Resource names follow naming standards
- [ ] Application CIs exist in CMDB

## Upload to SharePoint

### Automatic Upload
Script automatically uploads generated files to SharePoint artifact repository.

### Manual Upload (if needed)
1. Navigate to SharePoint artifacts folder
2. Create subfolder: `<lz_name>_welcome_kit_YYYYMMDD`
3. Upload all three files (HTML, PDF, Confluence)
4. Verify files are accessible
5. Generate shareable links if needed

### SharePoint Folder Structure
```
Artifacts/
└── Welcome_Kits/
    └── <lz_name>_welcome_kit_YYYYMMDD/
        ├── <lz_name>_welcome_kit.html
        ├── <lz_name>_welcome_kit.pdf
        └── <lz_name>_confluence.html
```

## Distribute Welcome Kit

### Partner Notice Email
⚠️ **CRITICAL**: This email triggers onboarding work with other teams

**Recipients:**
- Application development team (primary GitLab owner)
- Application development team (secondary GitLab owner)
- Business development group contact
- Build Factory team distribution list

**Include:**
- Links to Welcome Kit documents in SharePoint
- Summary of accounts created
- Next steps for customer
- Onboarding timeline
- Support contact information

### Confluence Page
1. Create new Confluence page in landing zone space
2. Copy content from `<lz_name>_confluence.html`
3. Paste into Confluence editor
4. Verify formatting and links
5. Publish page
6. Share link with stakeholders

## Troubleshooting

### DynamoDB Query Fails
**Symptom:** Cannot retrieve LZ metadata

**Solutions:**
- Verify AWS credentials are valid
- Check role has DynamoDB read permissions
- Confirm LZ name spelling is correct
- Ensure LZ metadata was imported in Step 10

### Lambda Invocation Fails
**Symptom:** Cannot retrieve ServiceNow data

**Solutions:**
- Verify Lambda function exists
- Check Lambda execution role permissions
- Review CloudWatch logs for Lambda errors
- Verify Secrets Manager credentials are valid

### ServiceNow API Error
**Symptom:** Application service tags not retrieved

**Solutions:**
- Check ServiceNow connectivity
- Verify CMDB CI exists
- Review Lambda logs for API errors
- Confirm application is registered in CMDB

### PDF Generation Fails
**Symptom:** HTML generated but no PDF

**Solutions:**
- Verify wkhtmltopdf is installed
- Check wkhtmltopdf is in system PATH
- Review error logs for rendering issues
- Try generating PDF manually from HTML

### Missing Account IDs
**Symptom:** Account IDs not in Welcome Kit

**Solutions:**
- Confirm Step 400 completed successfully
- Verify VM execution created all accounts
- Check DynamoDB state table for account records
- Rerun Welcome Kit generator after VM completion

### SharePoint Upload Fails
**Symptom:** Files not uploaded to SharePoint

**Solutions:**
- Verify Azure AD app registration
- Check SharePoint permissions
- Ensure network connectivity
- Try manual upload as fallback

## Quality Checklist

Before distributing Welcome Kit:
- [ ] Step 400 Vending Machine completed
- [ ] All accounts created and validated
- [ ] Welcome Kit generated for correct LZ name
- [ ] All three file formats generated (HTML, PDF, Confluence)
- [ ] Account IDs match DynamoDB state table
- [ ] GitLab owner information correct
- [ ] Compliance contexts generated properly
- [ ] State bucket names follow conventions
- [ ] Application service tags retrieved
- [ ] Links tested and functional
- [ ] PDF renders correctly
- [ ] Files uploaded to SharePoint
- [ ] Shareable links generated
- [ ] Partner notice email drafted
- [ ] Confluence page created (if applicable)

## For V2 or V1 Landing Zones

If generating Welcome Kit for legacy (V2 or V1) landing zone:
- Use legacy Welcome Kit process (wk-v2)
- Different data sources and templates
- Different output format
- Consult V2-specific documentation

## Next Steps

After Welcome Kit generation:
1. Validate all output files
2. Upload to SharePoint
3. Send partner notice email to trigger downstream onboarding
4. Create Confluence page for customer reference
5. Proceed to remaining post-build steps (CICD onboarding, QA, etc.)

## Important Notes

### Why This Step Is Critical
- **Triggers downstream work**: Other teams wait for this notification
- **Single source of truth**: Consolidates all LZ information
- **Customer deliverable**: Part of official handoff package
- **Compliance requirement**: Documents account provisioning

### Timing
- Must complete after Step 400 (VM execution)
- Should complete before CICD onboarding
- Partner notice triggers parallel onboarding activities
- Delays here block multiple downstream teams
