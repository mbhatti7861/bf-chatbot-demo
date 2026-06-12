# Post-Build Step 600: CICD Onboarding

## Overview
Configure CICD runners and create merge request for landing zone pipeline onboarding. Shared responsibility: Build Factory creates configuration and MR, CICD team merges and runs pipelines.

## Prerequisites

### ⚠️ CRITICAL: Step 400 Must Be Complete
VM execution produces account numbers needed for CICD configuration.

### Pre-Validation Checklist
Before CICD onboarding date:
- [ ] MCS compliance onboarding completed (Step 410 validation)
- [ ] GitLab owners logged into GitLab (must be done by Friday before onboarding)

### CICD Onboarding Schedule
CICD team onboards new LZs/accounts twice per week:
- **Cutoff**: 11:00 AM ET
- **Session 1**: [Day/Time TBD]
- **Session 2**: [Day/Time TBD]

Submit onboarding requests before cutoff to make the next session.

## Beta Automation Available

⚠️ **Note**: Task has been largely automated for reliable, consistent results.  
See: CICD Automation Repository for detailed instructions.

**Status**: Still in beta testing, not fully validated yet.  
**Recommendation**: Compare CLI output with manual instructions below.

## Required Access

### GitLab Management Repository
- Verify access to gitlab-management repo
- This is the services-prod GitLab instance (not prod instance)
- Only specific people have access to this repository

### Git Configuration
Ensure Git config ready for HTTPS:
```bash
git config --global http.sslBackend schannel
```

## Process

### 1. Clone Source Repository

```bash
# Using Git Bash, navigate to your GitLab directory
cd <your-gitlab-repos-directory>

# Clone repository
# Option 1: Use new Personal Access Token
git clone https://<TOKEN-NAME>:<PERSONAL-ACCESS-TOKEN>@<gitlab-services-prod-url>/cicd/Customer-management.git

# Option 2: Use existing Personal Access Token
git clone https://<gitlab-services-prod-url>/cicd/Customer-management.git
```

### 2. Create Feature Branch

One merge request per landing zone:

```bash
# Navigate to configs directory
cd ./customer-management/configs/

# Create feature branch
git checkout -b feature/<JIRA-TICKET>_ob_<lz-name>
# Example: git checkout -b feature/TASK-123_ob_my-landing-zone
```

### 3. Create Configuration Folder

```bash
# Copy template directory
cp -rp _template <lz-name>
# Example: cp -rp _template my-landing-zone

# Change to new directory
cd ./<lz-name>
```

### 4. Update customer.yaml File

**Determine Batch Number:**
```bash
# Count customers in each batch (max 20 per batch)
grep -R BATCH ../* | awk -F '\"' ' { print $2 } ' | sort | uniq -c | egrep -v '^ *2[0-9]|\-1'

# Use highest batch number with <20 customers
```

**Update customer.yaml fields:**
```yaml
LANDING_ZONE_NAME: <lz-name>
CUSTOMER_NAME: <organization-name>
BATCH: "<batch-number>"  # e.g., "02"
DISTRICT: <district-code>
BUSINESS_UNIT: <business-unit>
ORGANIZATIONAL_UNIT: <org-unit>
APPLICATION_SYSTEM_CI_NAME: <app-service-tag>
PRIMARY_GITLAB_OWNER: <email>
SECONDARY_GITLAB_OWNER: <email>
```

**Important Notes:**
- **APPLICATION_SYSTEM_CI_NAME**: Found in feature file under app-service-tag
- Copy tag WITHOUT environment suffix
- Example: `NY-CLD-MarketServices` (not `NY-CLD-MarketServices-PROD`)
- Verify GitLab owners have logged into GitLab before proceeding

### 5. Update Environment Files

```bash
# Delete non-production file (if not used)
rm environments/non-production.yaml

# Update production.yaml with account IDs
vi environments/production.yaml
```

**Production.yaml structure:**
```yaml
accounts:
  proving-ground:
    account_id: "<pg-account-id>"
  dev:
    account_id: "<dev-account-id>"
  test:
    account_id: "<test-account-id>"
  uat:
    account_id: "<uat-account-id>"
  staging:
    account_id: "<staging-account-id>"
  prod:
    account_id: "<prod-account-id>"
  services-nonprod:
    account_id: "<services-nonprod-id>"
  services-prod:
    account_id: "<services-prod-id>"
```

**Source**: Get account IDs from Confluence page created in Step 510

### 6. Commit Configuration Updates

```bash
# Add all changes
git add -A

# Commit with descriptive message
git commit -m "<JIRA-TICKET> - Customer-management - Add onboarding folder/files for new LZ: <lz-name>"
# Example: git commit -m "TASK-123 - Customer-management - Add onboarding folder/files for new LZ: my-landing-zone"

# Push to remote
git push -u origin <branch-name>
# Example: git push origin feature/TASK-123_ob_my-landing-zone
```

### 7. Create Merge Request

**In GitLab Web UI:**

1. Navigate to merge requests page
2. Click "New merge request"
3. Select your feature branch

**MR Configuration:**
- **Assign to**: Yourself
- **Mark as**: Draft
- **Require approval from**: CICD team member

**Description Template:**
```
**<JIRA-TICKET> - Customer Management**

This MR is for CICD Runner onboarding for this new version 3 LZ <lz-name>

**PURPOSE:** CFS2 CICD Onboarding
**District:** <district>
**LZ Name:** <lz-name>
**LZ Version:** 3

_Updated customer and LZ info in customer.yaml and environments/production.yaml_

**Promotion Account info source:**
<confluence-page-link-from-step-510>
```

**Example Description:**
```
**TASK-123 - Customer Management**

This MR is for CICD Runner onboarding for this new version 3 LZ my-landing-zone

**PURPOSE:** CFS2 CICD Onboarding
**District:** NY
**LZ Name:** my-landing-zone
**LZ Version:** 3

_Updated customer and LZ info in customer.yaml and environments/production.yaml_

**Promotion Account info source:**
https://confluence.example.com/landing-zone-my-landing-zone-accounts
```

### 8. Update Jira Ticket

Update onboarding Jira ticket with:
- Merge request number
- Link to MR
- Status: Ready for CICD team

### 9. Notify CICD Team

**Post in CICD Teams Channel:**
```
New CICD Onboarding Request

LZ Name: <lz-name>
Jira Ticket: <ticket-number>
Merge Request: <mr-number>
Requested Onboarding Date: <date>

Confluence Page: <link>
```

### 10. Update Project Story

Update project management story with:
- Jira ticket number
- CICD onboarding date
- MR link
- Status update

## Verify GitLab Owners

### Why This Matters
GitLab owners must be logged into GitLab **before Friday prior to onboarding** (onboarding typically occurs Mondays).

### How to Verify

**Method 1: Search in GitLab Console**
1. Log into GitLab console
2. Click search box
3. Type GitLab owner's email
4. If account appears in results → user has logged in ✅
5. If account not found → contact user to log in ❌

**Method 2: Direct URL**
1. Find user's Employee ID in FedIdentity (View Identity)
2. Navigate to: `https://<gitlab-url>/<EMPLOYEE-ID>`
3. If profile loads → user exists ✅
4. If 404 error → user hasn't logged in ❌

### If Owner Not Found
1. Contact GitLab owner via email/Teams
2. Request they log into GitLab immediately
3. Provide login URL and instructions
4. Verify again after they report logging in
5. Don't proceed to onboarding without confirmation

## Troubleshooting

### Cannot Clone Repository
**Solutions:**
- Verify repository access granted
- Check personal access token is valid
- Try token-based clone method
- Verify network connectivity to GitLab instance

### Batch Number Unclear
**Solutions:**
- Run batch count command again
- Contact CICD team for guidance
- Use batch "01" if unsure (CICD will adjust)

### Missing Account IDs
**Solutions:**
- Verify Step 510 Confluence page created
- Check VM execution completed for all accounts
- Review DynamoDB state table
- Contact team if accounts truly missing

### Application Service Tag Not Found
**Solutions:**
- Check feature metadata carefully
- Look for "app-service-tag" field
- Remove environment suffix if present
- Contact requestor if truly missing

### GitLab Owners Not in GitLab
**Solutions:**
- Contact owners immediately
- Provide login instructions
- Escalate if no response
- Don't proceed without owner access

### MR Creation Fails
**Solutions:**
- Verify branch pushed successfully
- Check GitLab permissions
- Ensure no merge conflicts
- Try creating via command line

## Quality Checklist

**Configuration:**
- [ ] Feature branch created with correct naming
- [ ] customer.yaml all fields populated
- [ ] Batch number determined correctly
- [ ] Application service tag without environment suffix
- [ ] GitLab owner emails verified
- [ ] environments/production.yaml has all account IDs
- [ ] Account IDs match Confluence page
- [ ] Non-production.yaml removed if not needed

**Version Control:**
- [ ] Changes committed with descriptive message
- [ ] Branch pushed to remote
- [ ] No merge conflicts

**Merge Request:**
- [ ] MR created and marked as Draft
- [ ] Assigned to yourself
- [ ] CICD team member required as approver
- [ ] Description is detailed and complete
- [ ] Confluence page link included

**Communication:**
- [ ] Jira ticket updated with MR number
- [ ] CICD team notified in Teams channel
- [ ] Project story updated with onboarding date
- [ ] GitLab owners verified in system

**Pre-Onboarding:**
- [ ] MCS compliance onboarding validated
- [ ] GitLab owners confirmed logged in (by Friday)
- [ ] Request submitted before cutoff time
- [ ] All required fields validated

## Next Steps

### Build Factory Responsibility Complete
After MR creation and notification:
1. CICD team reviews MR
2. CICD team approves and merges
3. CICD team runs onboarding pipelines
4. CICD team validates successful onboarding

### Build Factory Monitors For
- CICD team questions or feedback
- Onboarding completion notification
- Any errors requiring configuration updates

### After CICD Onboarding Complete
- Validate pipelines created
- Test runner connectivity
- Proceed to next post-build steps
- Update project status

## Important Notes

### Shared Responsibility Model
- **Build Factory**: Creates configuration, submits MR
- **CICD Team**: Reviews, merges, runs pipelines

### Timing Critical
- Friday deadline for GitLab owner verification
- 11 AM ET cutoff for onboarding requests
- Miss deadline = wait for next session

### Batch Management
- Max 20 customers per batch
- CICD team uses batches for maintenance
- Proper batch assignment prevents bottlenecks

### Why GitLab Owner Login Matters
- Required for repository creation
- Needed for permission assignment
- Blocks onboarding if not completed
- Cannot be resolved quickly on onboarding day
