# Post-Build Step 700: Submit Okta/AWS Access Role Requests

## Overview
Register IAM roles in FedIdentity/Okta and assign approver groups. Creates approval workflows for access requests and enables QA testing before customer delivery.

## Prerequisites

### Requestor Must Have
- Validated application identifier
- Application CIs created via registration process
- Authorization documentation
- Valid Okta approval group
  - Must start with: `GRPOWN-<LZ-specific-name>-OKTA-Approvers`
  - If group doesn't follow convention, submit request to create new workgroup

### Required Roles
Request via FedIdentity in base services account:
- Read-only role (standing access) - Read LZ information
- CLI session capability for assumed role

### Required Tools
- LZ FedIdentity spreadsheet build repository
- Python virtual environment
- AWS CLI configured

## Approver Group Strategy

### Initial Creation (Before QA)
- **CFS-Owned Roles**: Use CFS approver group
- **Customer-Owned Roles**: Use internal HEART approver group
  - Sends approval to internal team for QA access
  - Eliminates waiting for customer approval before delivery

### Post-QA Modification
After QA completes, reassign customer-owned role approver groups to customer's designated group (from feature metadata).

## Process Flow

```
1. Register IAM roles with appropriate approver groups
   ├─ CFS roles → CFS approver group
   └─ Customer roles → Internal approver group (temporary)

2. Complete QA testing (Step 900)

3. Modify customer roles to use customer approver group
```

## Automated Spreadsheet Creation (Recommended)

### 1. Setup Environment

```bash
# Clone repository
git clone <lz-fi-spreadsheet-repo-url>
cd lz_fi_spreadsheet_build

# Create virtual environment
python -m venv venv

# Activate (Git Bash or Linux)
. venv/Scripts/activate

# Activate (PowerShell)
. venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Spreadsheet

```bash
# Authenticate to base services account
# (use authentication helper)

# Generate spreadsheet
./main.py -n <LZ_NAME> -a <ADT_GROUP_NAME>

# PowerShell alternative:
python main.py -n <LZ_NAME> -a <ADT_GROUP_NAME>
```

**Parameters:**
- `LZ_NAME`: Landing zone name
- `ADT_GROUP_NAME`: FedIdentity Okta approver group from feature metadata

### 3. Interactive Prompts

**Email List Prompt:**
- Script prompts for emails of QA engineers
- Enter emails for those who need role access for QA testing
- This is now automated (no manual addition needed)

**Type Selection:**
- Choose: **Okta** (not Non-Okta)

### 4. Locate Output

Spreadsheet created in: `./output/Create AWS OKTA FedIdentity Group-{lz_name}.xlsx`

## Submit ServiceNow Request

### Access Request Form
Navigate to identity management group request form.

### Required Fields

**Request Type:** "Create AWS Okta Group"

**Requested For:** Person submitting request (not customer)

**Business Justification:**  
"Okta roles required for newly built AWS Landing Zones"

**File Upload:**  
Attach: `Create AWS OKTA FedIdentity Group-{lz_name}.xlsx` from output directory

**Desired Date:**  
Usually same as estimated date. Earlier date requires escalation approval.

### Post-Submission
Update project story with:
- ServiceNow request number
- Link to request
- Status and expected completion date

## Validate Okta Roles

### Automated Validation
See: Post Build Step 900: Perform LZ QA - Validation Steps

### Manual Validation Checklist
- [ ] All roles created in FedIdentity
- [ ] Approver groups assigned correctly
- [ ] Entitlements mapped properly
- [ ] Privilege access configured
- [ ] QA engineers have access

## Handling Missing Roles or Entitlements

### If Validation Finds Issues

**1. Open ServiceNow Incident**
- Assign to cloud access management team
- Include details of missing roles/entitlements
- Reference original request ticket

**2. Create Project Defect**
- Create defect ticket for LZ story
- Include incident ticket number
- Document what's missing

**3. Update Story Task**
- Add incident ticket number to story
- Add defect ticket number
- Document in discussions/comments

## Request Modifications (Post-QA)

### Purpose
Change approver group from internal to customer group after QA completion.

### Process

**1. Create New ServiceNow Request**
- Select Request Type: **"Modify Okta Group"**
- Use same request form as initial creation

**2. Generate Modification Spreadsheet**
Spreadsheet contains ONLY:
- Current approver group
- New approver group

**Options:**
- Use helper script to create spreadsheet
- Or manually create using template

**3. Submit Request**
- Attach modification spreadsheet
- Reference original request and QA completion
- Update project story with modification request number

### Important Note
All compliance roles should use CFS approver group:  
`Grpown-Okta-FRIT-CFS-Approvers`

## Troubleshooting

### Script Fails to Generate Spreadsheet
**Solutions:**
- Verify AWS authentication is valid
- Check LZ name spelling
- Ensure metadata exists in database
- Review script logs for specific errors

### ADT Group Name Invalid
**Solutions:**
- Verify group name format: `GRPOWN-<LZ>-OKTA-Approvers`
- Check feature metadata for correct group
- Submit workgroup creation request if needed

### Missing Metadata
**Solutions:**
- Confirm Step 10 metadata import completed
- Verify LZ name in database
- Check metadata file in document repository

### ServiceNow Request Delayed
**Solutions:**
- Follow up if pending >2 business days
- Check for approval holds
- Verify all required fields completed
- Escalate if blocking QA timeline

### Roles Not Appearing in FedIdentity
**Solutions:**
- Allow 24-48 hours for provisioning
- Check ServiceNow request status
- Verify request completed successfully
- Open incident if request shows complete but roles missing

### QA Engineers Can't Access Roles
**Solutions:**
- Verify emails were included in script prompt
- Check users exist in FedIdentity
- Confirm group membership provisioned
- May need to submit modification request to add users

## Quality Checklist

**Pre-Submission:**
- [ ] Prerequisites validated (HexID, CIs, permit, approver group)
- [ ] Authenticated to base services account
- [ ] Spreadsheet generated without errors
- [ ] Output file exists and is valid Excel format
- [ ] QA engineer emails included correctly
- [ ] Okta type selected (not Non-Okta)

**ServiceNow Request:**
- [ ] Request type correct: "Create AWS Okta Group"
- [ ] Requested For is submitter (not customer)
- [ ] Business justification included
- [ ] Spreadsheet attached
- [ ] Desired date set
- [ ] Request number captured

**Post-Submission:**
- [ ] Project story updated with request number
- [ ] Validation completed (automated or manual)
- [ ] All roles created successfully
- [ ] Approver groups assigned correctly
- [ ] QA engineers have access
- [ ] Any issues documented as defects

**Post-QA:**
- [ ] Modification request submitted
- [ ] Customer approver group assigned
- [ ] Internal approver group removed
- [ ] Customer can now approve access requests

## Timeline

**Initial Request:**
- Submit after VM completion (Step 400)
- Must complete before QA (Step 900)
- Allow 3-5 business days for provisioning

**Modification Request:**
- Submit after QA completion
- Must complete before customer delivery
- Allow 2-3 business days for changes

## Next Steps

After Okta roles validated:
1. Proceed to Step 710 (ELMA onboarding)
2. Continue with remaining post-build steps
3. Schedule QA testing (Step 900)
4. After QA, submit modification request to reassign approver groups

## Important Notes

### Why Two-Phase Approval Matters
- **Phase 1 (Internal)**: Allows Build Factory QA without customer involvement
- **Phase 2 (Customer)**: Transfers control to customer for ongoing access management

### Automation Benefits
- Faster spreadsheet generation
- Fewer manual errors
- Consistent formatting
- Automatic QA engineer addition
- Reduced preparation time

### Compliance Consideration
All compliance-related roles must always use CFS approver group, not customer group.
