# Post-Build Step 900: Perform LZ QA

## Overview
Validate landing zone build to ensure defect-free delivery. Comprehensive quality assurance testing of access, compliance, CMDB relationships, and configurations.

## Prerequisites

### Required Completions Before QA
- [ ] Step 200: Non-Okta access role requests submitted
- [ ] Step 700: Okta/AWS access role requests submitted
- [ ] Step 600: CICD onboarding completed
- [ ] Access to landing zone granted (via role requests)
- [ ] MCS compliance service plan role granted

**Exception:** CMDB QA is not dependent on CICD completion

### Required Access
- Compliance service plan role for this LZ
- Okta roles for account access
- Non-Okta roles for tooling access

## QA Documentation

### During QA Process
- Document outcomes of all validation steps
- Record results in project story
- Screenshot key validations
- Note any deviations from expected

### Issue Resolution
For any defects discovered:
1. Create defect ticket in project system
2. Link to parent LZ story
3. Assign appropriate priority
4. Document reproduction steps
5. Notify relevant teams

### Documentation Updates
- Update QA procedures if gaps found
- Socialize changes with team
- Keep runbooks current

## CICD-Type Landing Zones

CICD landing zones have special validation requirements:

### Characteristics
- Used by CICD team for cloud-hosted GitLab
- Contains only services-prod account
- No customer workload accounts
- Different validation focus

### Validation Steps for CICD LZ
1. Run LZ QA automation (FedIdentity access/verify roles)
2. Verify LZ contains only services-prod account
3. Verify Non-Okta roles
4. Verify Okta roles  
5. Verify Compliance contexts

**Expected Results:**
- CMDB relationship checks not required (handled by VM)
- Only failures should be ELMA and TF Plan (expected for CICD type)

## Standard Landing Zone QA

### Automated QA Tool

**Repository:** LZ QA Automation (FedIdentity)

**What It Validates:**
- FedIdentity role access
- Okta role configuration
- Non-Okta role configuration
- Compliance contexts
- Terraform state
- CMDB relationships
- Account access
- Tool integrations

### Run QA Automation

```bash
# Clone QA automation repository
git clone <lz-qa-automation-repo-url>
cd lz-qa-automation

# Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run QA for landing zone
python qa_automation.py <lz-name>
```

### QA Report Output

Script generates report with sections:
- Access validation results
- Role verification
- Compliance checks
- CMDB validation
- Integration tests
- Summary of findings

## Manual Validation Checklist

### 1. FedIdentity Access Validation

**Okta Roles:**
- [ ] Plan role exists
- [ ] Engineer role exists  
- [ ] ReadOnly role exists
- [ ] Approver groups correct
- [ ] Entitlements mapped

**Non-Okta Roles:**
- [ ] Compliance roles exist
- [ ] Security tool roles exist
- [ ] Observability roles exist
- [ ] Monitoring roles exist

### 2. Account Access Validation

**For Each Account:**
- [ ] Can assume role successfully
- [ ] AWS console access works
- [ ] CLI access works
- [ ] Permissions appropriate for role
- [ ] No access errors

**Test Accounts:**
- Dev, Test, UAT, Staging, Prod
- Services-nonprod, Services-prod
- Exclude Proving Ground from customer access

### 3. Compliance Validation

**MCS Contexts:**
```bash
# Non-prod contexts
SET PIPELINE_SERVICE_URL=https://mcs.services-nonprod.base.awscfs.frb.pvt

tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.proving-ground
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.dev
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.test
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.uat
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.services-nonprod

# Prod contexts
SET PIPELINE_SERVICE_URL=https://compliance.base.awscfs.frb.pvt

tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.staging
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.prod
tf init -app cfs-<lz>-lz-def -context cfs-base01-gov.<lz>.services-prod
```

**Verify:**
- [ ] All contexts initialize successfully
- [ ] No permission errors
- [ ] State backend accessible
- [ ] Compliance policies applied

### 4. CMDB Validation

**Check Relationships:**
- [ ] LZ service CI created
- [ ] Account CIs created for all accounts
- [ ] Application service CIs linked
- [ ] Relationships correct (hosted on, runs on, etc.)
- [ ] CI attributes populated correctly

**Verify in CMDB:**
1. Search for LZ service CI
2. View relationships tab
3. Confirm all account CIs present
4. Check application CI links
5. Validate attributes

### 5. CICD Validation

**GitLab Repository:**
- [ ] Repository created
- [ ] Primary owner has access
- [ ] Secondary owner has access
- [ ] Repository structure correct
- [ ] Default branch configured

**CICD Runners:**
- [ ] Runners registered for all accounts
- [ ] Runner tags correct
- [ ] Runner connectivity validated
- [ ] Pipeline variables configured

### 6. Network Validation

**CIDR Assignments:**
- [ ] Primary CIDRs correct (West)
- [ ] Secondary CIDRs correct (East)
- [ ] Non-routable CIDRs (if requested)
- [ ] No CIDR conflicts
- [ ] Transit gateway attachments
- [ ] Route tables configured

### 7. Security Tool Validation

**Compliance Scanner:**
- [ ] Accounts onboarded
- [ ] Scans running
- [ ] Policies applied
- [ ] Violations reviewed

**Cloud Security Posture:**
- [ ] Accounts visible
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Security groups correct

### 8. Observability Validation

**ELMA (if applicable):**
- [ ] RedShift access granted
- [ ] GitLab owner approved access
- [ ] Log aggregation working

**Grafana:**
- [ ] Dashboards created
- [ ] Metrics flowing
- [ ] Viewer access working
- [ ] Editor access working

**Dynatrace:**
- [ ] Management zone created
- [ ] Hosts visible
- [ ] Customer has access

### 9. EPV Validation

**Enterprise Password Vault:**
- [ ] All GovCloud accounts in EPV
- [ ] Passwords retrievable
- [ ] MFA seeds present
- [ ] Breakglass access works

### 10. Documentation Validation

**Deliverables:**
- [ ] Welcome Kit generated
- [ ] Account page created
- [ ] Confluence page published
- [ ] All links functional
- [ ] Information accurate

## Issue Categories

### Access Issues
- Role not granted
- Permissions insufficient
- Group membership missing
- Entitlement not mapped

### Compliance Issues
- Context won't initialize
- Policies not applied
- State backend inaccessible
- Terraform errors

### CMDB Issues
- CI not created
- Relationship missing
- Attributes incorrect
- Application CI not linked

### Network Issues
- CIDR conflicts
- Routes missing
- TGW attachment failed
- VPC configuration error

### Integration Issues
- Tool not onboarded
- Access not working
- Configuration missing
- Data not flowing

## QA Completion

### Before Marking Complete

**Verify:**
- [ ] All validation steps completed
- [ ] All defects documented
- [ ] Critical issues resolved
- [ ] Known issues documented with workarounds
- [ ] QA report generated and saved
- [ ] Project story updated with results

### Remove Access

**Important:** After QA completion:
1. Go to FedIdentity
2. Request removal from all LZ roles
3. Keep only what's needed for support
4. Document access removal

### Sign-Off

Update project story:
- QA completed date
- QA engineer name
- Summary of findings
- Outstanding issues (if any)
- Ready for delivery (yes/no)

## Expected Timelines

**CICD-Type LZ:** 2-4 hours  
**Standard LZ (3-4 accounts):** 4-6 hours  
**Standard LZ (5-8 accounts):** 6-8 hours  
**Complex LZ:** 1-2 days

Adjust based on:
- Number of accounts
- Defects encountered
- Integration complexity
- Team familiarity

## Troubleshooting

### Can't Access Accounts
- Verify Okta roles granted
- Check FedIdentity for role status
- Wait for provisioning (can take 30 min)
- Try logout/login

### Compliance Context Fails
- Verify MCS onboarding completed (Step 410)
- Check context name spelling
- Ensure account exists
- Validate state backend

### CMDB Relationships Missing
- Check VM execution logs
- Verify CMDB Manager ran
- Look for errors in CloudWatch
- May need manual CMDB update

### Tool Not Onboarded
- Verify onboarding step completed
- Check request ticket status
- Wait for provisioning
- Contact tool team

## Next Steps

After successful QA:
1. Update all defect tickets
2. Verify critical issues resolved
3. Obtain approval from PO if defects remain
4. Proceed to Step 1000 (Welcome Meeting)
5. Schedule customer delivery

## Important Notes

### Quality is Critical
- QA is final gate before customer delivery
- Thorough validation prevents customer issues
- Document everything
- Don't skip steps

### Defects Must Be Tracked
- All issues documented as defects
- Severity assigned appropriately
- Resolution path identified
- PO approval for delivery with open defects

### Access Hygiene
- Remove QA access after completion
- Don't accumulate unnecessary roles
- Reduces security risk
- Improves audit posture
