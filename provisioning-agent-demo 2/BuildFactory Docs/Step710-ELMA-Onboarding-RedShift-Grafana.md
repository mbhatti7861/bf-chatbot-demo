# Post-Build Step 710: ELMA Onboarding - RedShift/Grafana

## Overview
Onboard landing zones to observability platform (ELMA), RedShift log analytics, and Grafana monitoring services. Enables centralized logging, monitoring, and alerting for customer applications.

## Prerequisites

### Before Starting
- [ ] Order details complete in project feature
- [ ] Project owner updated feature with latest information
- [ ] Step 400: VM execution completed
- [ ] Step 200: Non-Okta access roles submitted and validated
- [ ] Step 210: ELMA FedIdentity requests completed

### Exclusions
❌ **Do NOT include:**
- Proving Ground accounts
- Services-Prod accounts
- Services-NonProd accounts
- NY landing zones (skip ELMA onboarding entirely)

## Process Overview

### Pre-Build Preparation (Completed Earlier)
- Customer notified of ELMA onboarding expectations
- Required specs verified (OU, BU, GitLab owner contact)
- GitLab owner granted FedIdentity access to observability portal
- Non-Okta roles created and validated for RedShift and Grafana

### Post-Build Onboarding (This Step)
1. Submit RedShift onboarding request
2. Customer (GitLab owner) approves request
3. Submit Grafana onboarding request
4. ELMA team completes onboarding

## Part 1: RedShift Onboarding

### Prerequisites Validation
- [ ] Step 200: Non-Okta RedShift role created and validated
  - Example format: `REDSHIFT-ELMA (PROD)-NIT-FOUNDATION-<lz-name>`
  - Validate in identity management system
- [ ] Step 210: GitLab owner has access to observability portal

### Gather Required Information

**Source:** LZ metadata file in document repository

Required fields:
- Organizational Unit (OU)
- Business Unit (BU)
- Landing Zone name
- GitLab owner email
- Okta group name

### Submit RedShift Request

**Step 1: Access Portal**
Navigate to observability access request portal.

**Step 2: Complete Form**

**Organizational Unit:**
- Select from dropdown
- Source: LZ metadata file

**Business Unit:**
- Select from dropdown
- Source: LZ metadata file and OU/BU mapping reference
- **If missing from dropdown:** Contact ELMA team to add

**Landing Zone:**
- Select from dropdown
- Source: LZ metadata file

**Enter Okta Group Name:**
- Usually auto-populated after selecting fields
- Format: `REDSHIFT-ELMA (PROD)-NIT-FOUNDATION-<lz-name>`

**Point of Contact Email:**
- Engineer submitting the request

**Approver Email:**
- **Standard LZs:** GitLab Primary Owner email
- **FRFS LZs:** Use designated internal approver (not GitLab owner)

⚠️ **CRITICAL for FRFS Landing Zones:**  
Do NOT use GitLab owner as approver. Use designated internal contact instead.

**Step 3: Submit Form**
Verify all fields complete and submit.

### Send Notification Email

**From:** Team mailbox

**To:**
- GitLab Primary Owner (for non-FRFS LZs)
- OR Internal approvers (for FRFS LZs: specified contacts)
- Business development group email
- Team mailbox (for tracking)

⚠️ **FRFS Exception:** Do not send to GitLab owner for FRFS landing zones.

**Subject:**  
`<AR> ELMA Access Request for Redshift`

**Body Template:**
```
Hello <GitLab Primary Owner>,

A Redshift access request has been submitted to allow members of 
your application development team to see ELMA logs and notifications 
for your landing zone.

Please follow this link to review and approve the pending access request:
[Portal link will be in request notification]

Note: This is a required step to onboard your landing zone to ELMA services.

Thanks!
```

### Verify Approval
- GitLab owner receives email notification
- GitLab owner logs into observability portal
- GitLab owner approves RedShift access request
- Confirmation email sent to requestor

## Part 2: Grafana Onboarding

### Prerequisites Validation
- [ ] `cfs-grafana-readonly-role` exists in each LZ account
  - Created automatically by Vending Machine
- [ ] Non-Okta Grafana roles created and validated
  - Editor roles (Prod and Non-Prod)
  - Viewer roles (Prod and Non-Prod)

### Gather Required Information

**Source:** Account page from Step 510 (knowledge base)

**Excluded Accounts:**
- Proving Ground
- Services-Prod
- Services-NonProd

### Environment Mapping

Map accounts to Grafana environments:

| Account Type | Grafana Environment |
|--------------|---------------------|
| dev | non-prod |
| test | non-prod |
| uat | non-prod |
| staging | Prod |
| prod | Prod |

### Prepare IAM Role ARNs

**Format:**
```
arn:aws-us-gov:iam::<ACCOUNT-ID>:role/cfs-grafana-readonly-role - <environment>
```

**Example for ces-core LZ:**

**Non-Prod:**
```
arn:aws-us-gov:iam::090023294275:role/cfs-grafana-readonly-role - dev
arn:aws-us-gov:iam::090047889258:role/cfs-grafana-readonly-role - uat
```

**Prod:**
```
arn:aws-us-gov:iam::086817484961:role/cfs-grafana-readonly-role - prod
```

### Prepare Non-Okta Role Names

**Format:**
```
GRAFANA-ELMA (Non-Prod)-EDITOR-NIT-FOUNDATION-<LZ-NAME>
GRAFANA-ELMA (PROD)-EDITOR-NIT-FOUNDATION-<LZ-NAME>
GRAFANA-ELMA (Non-Prod)-VIEWER-NIT-FOUNDATION-<LZ-NAME>
GRAFANA-ELMA (PROD)-VIEWER-NIT-FOUNDATION-<LZ-NAME>
```

### Submit Grafana Request

**Step 1: Access Form**
Navigate to ELMA Grafana Access Request page in knowledge base.

**Step 2: Complete Form**

**Today's Date:**
- Auto-populated

**Point of Contact:**
- Engineer working on onboarding

**IAM Role ARN:**
- Enter ARNs with environment tag
- Format: `<arn> - <environment>`
- Include all non-excluded accounts

**Grafana OKTA Editor Groups:**
- Enter Editor groups from Step 200
- Both Prod and Non-Prod

**Grafana OKTA Viewer Groups:**
- Enter Viewer groups from Step 200
- Both Prod and Non-Prod

**Comments:**
```
This request is from the Build Factory to onboard <Landing Zone Name> 
landing zone to Grafana
```

**Step 3: Submit Form**
- Review all entries
- Submit form
- Confirmation email sent to point of contact

### Notify ELMA Team

**Post in ELMA Onboarding Channel:**
```
New Grafana Onboarding Request

Landing Zone: <lz-name>
Request Submitted: <date>
Point of Contact: <your-name>

Please process when ready. Thanks!
```

ELMA contact will coordinate onboarding.

### Grafana Onboarding Schedule

ELMA team onboards Grafana on:
- Tuesdays
- Thursdays

Submit requests before these days for timely processing.

### Confirmation

**You will receive:**
1. Email confirmation of form submission
2. Chat message from Grafana team when onboarding complete
3. Notification that Grafana dashboards are accessible

## Validation

### RedShift Validation
- [ ] Request submitted successfully
- [ ] GitLab owner received notification
- [ ] GitLab owner approved request
- [ ] Confirmation email received
- [ ] RedShift access functional

### Grafana Validation
- [ ] Form submitted successfully
- [ ] Confirmation email received
- [ ] ELMA team notified in chat
- [ ] Grafana team confirms completion
- [ ] Test Grafana dashboard access

### Access Testing
After onboarding completes:
1. Request QA engineer to log into Grafana
2. Verify dashboards visible for LZ accounts
3. Check RedShift query access
4. Confirm observability data flowing

## Troubleshooting

### OU/BU Missing from Dropdown
**Solution:**
- Contact ELMA team via chat channel
- Request addition of missing OU/BU
- Provide OU/BU details from metadata
- Wait for confirmation before resubmitting

### GitLab Owner Hasn't Approved RedShift
**Solutions:**
- Verify GitLab owner received email notification
- Check Step 210 FedIdentity access completed
- Resend notification email if needed
- Contact GitLab owner directly
- For urgent cases, use internal approver (with customer permission)

### IAM Role ARNs Incorrect
**Solutions:**
- Verify account IDs from Step 510 page
- Check role name format: `cfs-grafana-readonly-role`
- Confirm VM created roles in all accounts
- Validate in AWS console if needed

### Non-Okta Roles Not Found
**Solutions:**
- Verify Step 200 completed
- Check role names in identity management system
- Ensure validation passed
- Resubmit Step 200 if roles missing

### Grafana Team Not Responding
**Solutions:**
- Verify posted in correct chat channel
- Check if form submitted successfully
- Review Grafana onboarding schedule (Tue/Thu)
- Follow up in channel if >2 business days
- Escalate to ELMA management if blocking

### FRFS Landing Zone Issues
**Common Mistakes:**
- ❌ Using GitLab owner as approver (should use internal contacts)
- ❌ Sending email to GitLab owner (should use internal contacts)

**Correct Process for FRFS:**
- Always use designated internal approvers
- Do not involve GitLab owner in approval workflow

## Quality Checklist

**RedShift:**
- [ ] Step 200 and 210 completed
- [ ] Non-Okta RedShift role validated
- [ ] OU/BU selected correctly
- [ ] Landing zone name correct
- [ ] Okta group name matches format
- [ ] Correct approver email (check FRFS exception)
- [ ] Form submitted successfully
- [ ] Notification email sent
- [ ] GitLab owner approved request
- [ ] Confirmation received

**Grafana:**
- [ ] `cfs-grafana-readonly-role` exists in all accounts
- [ ] Non-Okta Grafana roles validated (4 roles)
- [ ] IAM ARNs collected for all non-excluded accounts
- [ ] Environment tags added to ARNs
- [ ] Editor and Viewer groups entered correctly
- [ ] Form submitted successfully
- [ ] ELMA team notified
- [ ] Confirmation received
- [ ] Grafana access tested

## Timeline

**RedShift:**
- Submit after VM completion and Non-Okta roles validated
- GitLab owner approval: Usually same day
- Total time: 1-2 business days

**Grafana:**
- Submit after RedShift onboarding complete
- ELMA team processes: Tuesday/Thursday
- Total time: 1-5 business days (depending on submission timing)

## Next Steps

After ELMA onboarding completes:
1. Document completion in project story
2. Update LZ status tracking
3. Proceed to Step 900 (QA)
4. Include observability validation in QA tests

## Important Notes

### NY Landing Zones Exception
⚠️ Skip this entire step for NY landing zones. They are not onboarded to ELMA.

### Account Exclusions
Always exclude:
- Proving Ground (used for testing only)
- Services accounts (managed separately)

### FRFS Special Handling
FRFS landing zones require different approver workflow. Always use internal approvers, never GitLab owner.

### Dependencies
This step depends on:
- Step 200: Non-Okta roles
- Step 210: FedIdentity access
- Step 400: VM execution
- Step 510: Account page creation

### Customer Communication
GitLab owner was notified of ELMA onboarding during Pre-Build. They should be expecting the RedShift approval request.
