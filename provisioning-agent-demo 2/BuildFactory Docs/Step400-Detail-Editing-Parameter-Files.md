# Build Step 400 Detail: Editing LZ Vending Machine Parameter Files

## Overview
Guide for completing parameter YAML files for each cloud account in the landing zone. Each account environment (Dev, Test, UAT, Staging, Prod, Services) requires its own parameter file.

## Parameter File Location
Repository: LZ Parameters (CodeCommit)  
Path: `<lz_name>/<account_name>/parameters.yml`

## Finding Parameter Values
Source: Project management feature for the landing zone request

## YML Template Field Guide

### Account Configuration
```yaml
accountname: <dev|test|uat|services-nonprod|staging|prod|services-prod>
```
**Action:** Remove folders for accounts not being provisioned

### Basic Fields
```yaml
accountingcode: ${account_code}
appciid: 
  - ${app_sys_id}
lztype: ${internal_or_external}
supportgroup: ${support_group}
vmssupport: ${vms_support_group}
systemowner: ${email_lz_owner}
assignedto: ${email_compliance_contact}
```

**Field Details:**
- `appciid`: Can have multiple entries (one per application)
- `systemowner`: Find email using directory/collaboration tools
- `assignedto`: Find email using directory/collaboration tools

### Boundary Type
```yaml
boundary: ${cfs_or_frfs}
```
**Logic:**
- If boundary indicator = "N" → use `cfs`
- If boundary indicator = "Y" → use `frfs`

### Non-Routable CIDR
```yaml
nonroutablecidr: 100.127.0.0/16
```

**Important Rules:**
- Standard non-routable CIDR: `100.127.0.0/16`
- **Only uncomment for non-service accounts** (PG, Dev, Test, UAT, Staging, Prod)
- Check request - some customers want it only in specific accounts
- **DO NOT uncomment for services accounts** unless explicitly requested

### VPC CIDRs
```yaml
cidr:
  primary: ${vpc_cidr_primary}    # West region
  secondary: ${vpc_cidr_secondary} # East region
```

**Source:** Reference CIDR allocation spreadsheet from Step 100:
- Primary CIDR = West region column
- Secondary CIDR = East region column

## Complete Example

### Sample DEV Account Parameter File
```yaml
accountname: dev
accountingcode: "12345"
appciid:
  - "app-sys-id-001"
  - "app-sys-id-002"
lztype: internal
supportgroup: "application-support-team"
vmssupport: "infrastructure-support-team"
systemowner: "lz.owner@example.com"
assignedto: "compliance.contact@example.com"
boundary: cfs
nonroutablecidr: 100.127.0.0/16  # Only for non-service accounts
cidr:
  primary: "10.100.0.0/16"      # West
  secondary: "10.101.0.0/16"    # East
```

## Workflow Steps

### 1. Copy Template
```bash
# From _template folder
cp -r _template/* <lz_name>/
```

### 2. Remove Unused Account Folders
Delete directories for accounts not being provisioned:
```bash
# Example: If only creating Dev, Test, and Prod
rm -rf <lz_name>/uat
rm -rf <lz_name>/staging
rm -rf <lz_name>/services-nonprod
rm -rf <lz_name>/services-prod
```

### 3. Edit Each Account Parameter File
For each account folder:
1. Open `parameters.yml`
2. Fill in values from feature metadata
3. Add CIDRs from Step 100 spreadsheet
4. Apply non-routable CIDR rules
5. Set boundary based on compliance requirements
6. **Save the file**

### 4. Validate YAML Syntax
- Check indentation (spaces, not tabs)
- Verify list formatting for multi-value fields
- Ensure quotes around string values
- Validate CIDR notation format

## Common Patterns

### Multiple Application CIs
```yaml
appciid:
  - "app-sys-id-001"
  - "app-sys-id-002"
  - "app-sys-id-003"
```

### Internal vs External Landing Zone
```yaml
# Internal LZ
lztype: internal
boundary: cfs

# External LZ (with boundary)
lztype: external
boundary: frfs
```

### Services Account Configuration
```yaml
# Services accounts (prod/nonprod)
# - DO NOT add nonroutablecidr unless explicitly requested
# - Always use "Internal" location even for external LZs

accountname: services-prod
lztype: internal
# nonroutablecidr: COMMENTED OUT (unless specified in request)
cidr:
  primary: "10.100.100.0/24"
  secondary: "10.101.100.0/24"
```

### Non-Routable Request Variations
```yaml
# Scenario 1: Non-routable for all non-service accounts
# Uncomment nonroutablecidr in: dev, test, uat, staging, prod

# Scenario 2: Non-routable only for dev and test
# Uncomment nonroutablecidr in: dev, test only
# Leave commented in: uat, staging, prod

# Scenario 3: Non-routable for all accounts including services
# Uncomment nonroutablecidr in: ALL account parameter files
# (This is rare - verify request explicitly states this)
```

## Quality Checks

### Before Committing
- [ ] All requested accounts have parameter files
- [ ] Unused account folders removed
- [ ] Account names match folder names
- [ ] CIDRs match Step 100 allocation spreadsheet
- [ ] Primary/secondary CIDRs assigned correctly (West/East)
- [ ] Non-routable CIDR applied per request requirements
- [ ] Services accounts follow "Internal" rule
- [ ] Email addresses validated in directory
- [ ] Application sys_ids verified in CMDB
- [ ] YAML syntax valid (no tabs, proper indentation)
- [ ] All files saved

### Common Mistakes to Avoid
❌ Adding non-routable CIDR to services accounts by default  
❌ Using tabs instead of spaces for indentation  
❌ Mismatching primary/secondary CIDRs between regions  
❌ Leaving placeholder values in files  
❌ Using invalid email formats  
❌ Forgetting to remove unused account folders  

## Troubleshooting

### YAML Parse Errors
**Symptom:** VM fails with YAML syntax error

**Solutions:**
- Use YAML linter/validator
- Check for tabs (must use spaces)
- Verify list syntax for multi-value fields
- Check quote matching for strings

### CIDR Not Found
**Symptom:** VM can't find CIDR for account

**Solutions:**
- Verify CIDR exists in Step 100 allocation
- Check primary/secondary match region
- Ensure CIDR format is valid (x.x.x.x/xx)
- Confirm CIDR matches spreadsheet exactly

### Invalid Email Address
**Symptom:** Validation fails on systemowner or assignedto

**Solutions:**
- Look up user in directory
- Verify email format is valid
- Check for typos
- Use official corporate email

### Application CI Not Found
**Symptom:** VM can't locate application sys_id

**Solutions:**
- Verify sys_id in CMDB
- Check for leading/trailing spaces
- Confirm application is registered
- Use correct sys_id format

## Next Steps
Once all parameter files are complete and validated:
1. Commit changes to Git (see Step 400 main workflow)
2. Create pull request
3. Peer review
4. Merge to main
5. Proceed to VM execution

## Reference
- Full parameter file definition: See repository documentation
- CIDR allocations: Step 100 output spreadsheet
- Feature metadata: Project management system feature
- CMDB validation: ServiceNow configuration item database
