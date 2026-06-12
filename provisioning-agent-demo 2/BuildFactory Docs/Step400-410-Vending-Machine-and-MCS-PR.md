# Build Steps 400 & 410: Vending Machine and MCS Compliance PR

## Overview
Execute infrastructure automation (Vending Machine) to build cloud accounts, then submit compliance pull requests for security policy enforcement.

## External Landing Zone Requirements
For landing zones with external network access:
- ❌ No proving ground accounts allowed
- ✅ Non-routable IPs highly encouraged for all accounts
- ✅ Services accounts (Prod/Non-Prod) must be "Internal" in config files and CIDR requests

## Prerequisites

### Required Roles
**Base Services Account** - Request via FedIdentity:
- **VM Developer Role** (standing access) - Create/upload parameter files, create PRs
- **Foundation Engineer Role** (standing access) - MCS work after VM completion
- **VM Operator Role** (privileged, time-bound) - Execute VM
  - Start Date: Day change ticket starts
  - End Date: Day after change ticket ends
  - Auto-expires at midnight on end date

### Required Repositories
- LZ Parameters (CodeCommit)
- Compliance Policies Code (CodeCommit)

### Pre-Execution Validation
- [ ] Step 100: CIDRs created (both regions) for all LZs
- [ ] Non-routable CIDRs identified (standard: `100.127.0.0/16`)
- [ ] Step 300: Change request in ServiceNow (Scheduled status)

## Architecture: VM/CMDB Decoupling

**Problem Solved:** Previously, VM crashed frequently due to CMDB updates being tightly coupled.

**New Architecture:**
1. VM runs and completes infrastructure build
2. VM drops message on SQS queue with account information
3. EventBridge triggers Queue Manager lambda periodically
4. Queue Manager invokes CMDB Manager lambda
5. CMDB Manager creates/updates CMDB records separately

**Key Benefit:** VM and CMDB updates are now independent, allowing separate maintenance and troubleshooting.

### CMDB Update Control
Controlled by execution name suffix:
- **Without `-cmdb` suffix**: VM runs, CMDB updates skipped
- **With `-cmdb` suffix**: VM runs, CMDB updates triggered

Example names:
- `CHG0123456-LZ_Create-mylz_Run1` (no CMDB update)
- `CHG0123456-LZ_Create-mylz_Run1-cmdb` (with CMDB update)

### Monitoring CMDB Manager
1. Navigate to Build Factory LZ in console
2. Open `vm-extender-queue-manager` lambda
3. Click "View CloudWatch Logs"
4. Check top log stream for messages

## Step 400: Setup LZ Parameter Files

### 1. Clone Parameters Repository
```bash
# Navigate to code directory
cd <code-directory>

# Clone repository (use VM Developer role)
git clone codecommit::us-gov-west-1://cfs-ents-lz-parameters

# If 403 error, try:
export AWS_PROFILE="<vm-developer-role-profile>"
git clone codecommit::us-gov-west-1://cfs-ents-lz-parameters
```

### 2. Prepare Parameter Files
```bash
# Switch to main and pull latest
git switch main
git pull

# Create feature branch
git checkout -b new-<lz_name>-1

# Create LZ directory
mkdir <lz_name>

# Copy template files
cp -r _template/* <lz_name>

# Remove unused account folders
# Edit YML files with:
# - Values from metadata YAML (Jira feature)
# - CIDRs from Step 100
# - CMDB fields (see sample below)
```

### 3. Commit and Push Changes
```bash
# Check status
git status

# Stage changes
git add .

# Commit with change ticket reference
git commit -am "PATCH: Create new LZ <lz_name> (CHG#######)"

# Switch to main and pull updates
git switch main
git pull

# Switch back to branch and merge
git switch new-<lz_name>-1
git merge main

# Push to remote
git push origin new-<lz_name>-1
```

### 4. Create Pull Request
1. Log into console (VM Developer role)
2. Navigate to parameters repository in CodeCommit
3. Select newly created branch in "Reference" dropdown
4. Click "Create Pull Request"
5. Submit for peer review

### 5. Peer Review & Approval
**Reviewer must verify:**
- [ ] IPs in parameters match CIDR spreadsheet
- [ ] Primary and secondary CIDR correct
- [ ] VMS support group matches feature specification
- [ ] YAML syntax valid
- [ ] All required fields populated

**After approval:** Create merge in console

## Step 400: Execute Vending Machine

### 1. Update Change Request
Mark change ticket status to "Implement"

### 2. Start VM Execution
1. Log into console (VM Operator role - privileged)
2. Search for Step Function: `cfs-lz-vm-orchestration`
3. Click "Start Execution"

### Initial Run (Create LZ)
**Execution Name:**
```
CHG#######-LZ_Create-<lz_name>_Run1-cmdb
```
Note: `-cmdb` flag enables CMDB updates via VM Extender

**Input:**
```json
{
  "dry_run": "false",
  "lz_action": "create_lz",
  "lz_name": "<lz_name>"
}
```

### Re-Run for Failed Accounts (Update LZ)
**Execution Name:**
```
CHG#######-LZ_Update-<lz_name>_<account>_Run1-cmdb
```

**Input:**
```json
{
  "dry_run": "false",
  "lz_action": "update_lz",
  "lz_name": "<lz_name>",
  "lz_account_name": "<account>",
  "lz_account_tier": "<account>"
}
```

### 3. Monitor Execution
- Watch Step Function execution graph
- Review CloudWatch logs for errors
- Check EventBridge logs for CMDB Manager activity

**If VM fails:** Create defect ticket for each rerun required

### 4. Validate VM Output

**Check DynamoDB State Table:**
1. Navigate to DynamoDB in console
2. Query: `cfs-ents-lz-orchestration-state-table`
3. Verify all accounts have records

**Check CloudWatch Logs:**
Review execution logs for errors or warnings

## Step 410: Submit MCS Compliance PR

### Compliance Deadlines
⚠️ **Critical:** Compliance onboarding must complete BEFORE CICD onboarding

**Cutoff Times:**
- Monday EOD → Tuesday release
- Wednesday EOD → Thursday release

**Notification:** Email compliance team from team mailbox (CC team distribution list)

### 1. Validate MCS PR Created by VM
1. Navigate to CodeCommit (Foundation Engineer role)
2. Open repository: `cfs-base-definition-compliance-policies-code`
3. Go to Pull Requests → Changes tab
4. Verify all accounts listed (pg, dev, uat, staging, prod, etc.)

**If accounts missing:** Rerun VM in update mode for missing accounts

### 2. Clone Compliance Repository
```bash
# Navigate to code directory
cd <code-directory>

# Clone repository (use Foundation Engineer role)
git clone codecommit::us-gov-west-1://cfs-base-definition-compliance-policies-code

# If 403 error:
export AWS_PROFILE="<foundation-engineer-role-profile>"
git clone codecommit::us-gov-west-1://cfs-base-definition-compliance-policies-code
```

### 3. Prepare Compliance Release
```bash
# Switch to main and pull
git switch main
git pull

# Checkout LZ branch (created by VM)
git checkout new-<lz_name>-<account>

# Navigate to changelog
cd changelog

# Create release directory (use Thursday release date)
mkdir <YYYYMMDD.1>

# Move unreleased files to release directory
git mv unreleased/<lz_name> <YYYYMMDD.1>/<lz_name>

# Commit changes
git commit -a -m "READY:release w/<YYYYMMDD.1> (<lz_name>)"

# Push to remote
git push
```

### 4. Update PR in Console
1. Log into console (Foundation Engineer role)
2. Navigate to compliance repository in CodeCommit
3. Open Pull Request created by VM
4. Click "Edit Details"
5. Add `READY:` prefix to title
6. Submit changes

### 5. Notify Compliance Team
Send email to compliance team:
- **Subject:** `MCS PRs Ready for Review - <lz_name>`
- **Body:** PR details and landing zone information
- **From:** Team mailbox (required)
- **CC:** Team distribution list

### 6. Close Change Request
After VM validation complete, close change ticket (see Step 300 for closure process)

## Post-Compliance Validation

### After Compliance Onboarding Complete
Validate new contexts using MCS CLI:

**Non-Prod Contexts:**
```bash
SET PIPELINE_SERVICE_URL=https://mcs.services-nonprod.base.awscfs.frb.pvt

tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.proving-ground
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.dev
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.test
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.uat
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.services-nonprod
```

**Prod Contexts:**
```bash
SET PIPELINE_SERVICE_URL=https://compliance.base.awscfs.frb.pvt

tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.staging
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.prod
tf init -app cfs-<lz_name>-lz-def -context cfs-base01-gov.<lz_name>.services-prod
```

### Automated Validation Script
```bash
./tf-init-test.sh <lz_name>
```
Shows results for all accounts. Errors expected for accounts not in this LZ.

## Troubleshooting

### VM Execution Hangs
**Likely Cause:** Terraform state lock issue

**Resolution:**
1. Check state lock table in DynamoDB
2. Clear stale locks if found
3. Rerun VM execution

### VM Completes with Errors
**Common Issues:**
- **External LZ errors**: Review external access configuration
- **VPC dependency errors**: Manual cleanup required (see below)
- **CMDB errors**: Check CMDB Manager logs

### Missing Cloud Accounts
**Likely Causes:**
- Misconfigured parameter files
- Incomplete VM run
- Account folders removed from parameters

**Resolution:**
1. Review all parameter files
2. Validate DynamoDB state table
3. Rerun VM for missing accounts

### Missing CMDB Relationships
**Cause:** Failed VM run or CMDB Manager failure

**Resolution:**
1. Check CMDB Manager logs
2. Rerun VM with `-cmdb` suffix
3. Validate CMDB records created

### Incorrect CIDR Assignment
**Cause:** Misconfigured parameter files

**Resolution:**
1. Review parameter files against CIDR spreadsheet
2. Correct CIDR values
3. Commit and merge PR
4. Rerun VM

### Missing MCS Contexts
**Cause:** Compliance PR not completed successfully

**Resolution:**
1. Validate MCS PR in CodeCommit
2. Ensure "READY:" prefix added
3. Confirm compliance team merged PR
4. Check compliance release schedule

### Manual VPC Cleanup (for update_lz errors)

**When needed:** `DependencyViolation: The vpc has dependencies and cannot be deleted`

**Steps:**
1. Log into account with admin role
2. **Delete Transit Gateway Attachments:**
   - Navigate to VPC → Transit Gateway Attachments
   - Delete all attachments

3. **Remove TGW Routes from Route Tables:**
   - Navigate to VPC → Route Tables
   - For each routable subnet route table:
     - Select Routes → Edit Routes
     - Remove routes with Target = "Transit Gateway"
     - Save changes

4. **Delete VPCs:**
   - Navigate to VPC → Your VPCs
   - Delete VPCs one at a time

5. Rerun VM in update_lz mode

## Process Summary Checklist

**Pre-Execution:**
- [ ] CIDRs created (Step 100)
- [ ] Change request scheduled (Step 300)
- [ ] Parameter files reviewed and correct

**VM Execution:**
- [ ] Parameters repo cloned and updated
- [ ] PR created and peer reviewed
- [ ] PR approved and merged
- [ ] Change request set to "Implement"
- [ ] VM executed successfully
- [ ] DynamoDB records validated
- [ ] CloudWatch logs reviewed

**MCS Compliance:**
- [ ] MCS PR created by VM
- [ ] All accounts present in PR
- [ ] Changelog updated
- [ ] PR title prefixed with "READY:"
- [ ] Compliance team notified
- [ ] PR merged on release day
- [ ] Contexts validated post-onboarding

**Closure:**
- [ ] All accounts validated
- [ ] Change request closed
- [ ] Validation script run successfully

## Important Notes

### SaaS Endpoints
When adding account to existing LZ with SaaS endpoints: Do NOT add endpoints to new account parameter file. They already exist at LZ level.

### Defect Tracking
Create defect ticket for EACH VM rerun required. Track:
- Reason for failure
- Accounts affected
- Resolution steps
- Execution names/IDs

### Compliance Dependencies
⚠️ Compliance onboarding is prerequisite for CICD onboarding. Do not proceed to CICD steps until compliance validation passes.
