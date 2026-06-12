# Post-Build Step 800: Configure EPV (Enterprise Password Vault)

## Overview
Configure administrator passwords and MFA for GovCloud accounts, then upload secrets to Enterprise Password Vault (EPV) for privileged access management.

## Prerequisites

### Required Before Starting
- [ ] Step 400: VM execution complete
- [ ] Step 510: Account page created (for account numbers)
- [ ] AWS account numbers available

### Required Roles
Request via FedIdentity (all are privileged, time-bound roles):

**GovCloud Access:**
- PayerAdmin role - Password reset and MFA enable in GovCloud
- Set start/end dates to duration required
- Role expires at midnight on end date

**Commercial Cloud Access (if needed):**
- AdminAccess role - Password reset and MFA enable in Commercial
- Set start/end dates to duration required
- Role expires at midnight on end date

**EPV Portal Access:**
- Breakglass Admins group - Upload passwords/MFA to EPV portal
- Submit when ready to upload
- Set start/end dates to duration required
- Role expires at midnight on end date

## Purpose

Enterprise Password Vault (EPV) provides:
- Secrets management
- Privileged access management (PAM)
- Secure storage of admin credentials
- MFA seed management

**Important:** Only GovCloud accounts uploaded to EPV. Commercial accounts now use PayerAdmin role for access.

## Automated Process (Recommended)

### 1. Clone EPV Generation Script

```bash
git clone <epv-bulk-upload-repo-url>
cd epv-bulk-upload
```

### 2. Setup Environment

Follow instructions in repository's README:
- Python virtual environment
- Install dependencies
- Configure AWS credentials

### 3. Run Script

Script automatically:
1. Connects to AWS accounts
2. Configures administrator password
3. Enables and configures MFA
4. Generates EPV upload spreadsheet

### 4. Locate Output

Find generated Excel file in: `output/` directory

### 5. Validate Spreadsheet

**Check:**
- [ ] Only GovCloud accounts present (no Commercial)
- [ ] All expected accounts included
- [ ] Passwords populated
- [ ] MFA seeds populated
- [ ] Account IDs correct
- [ ] No blank rows

### 6. Set Classification Label

**Important Security Step:**
- Change document classification to: **Restricted FR**
- Enable editing
- This protects sensitive credential data

### 7. Export as CSV

**Required Format:**
- Export spreadsheet as CSV (not XLSX)
- CSV format required for EPV bulk upload
- Name: `EPV-BULK-UPLOAD-<YYYY-MM-DD>.csv`

## Upload to EPV

### 1. Access EPV Portal

Navigate to EPV portal (Enterprise Password Vault).

### 2. Follow Bulk Upload Process

Reference: "How To Do Bulk Upload in v10.pdf"

**Key Steps:**
- Verify CSV format correct
- Select appropriate safe/folder
- Upload CSV file
- Confirm upload initiated
- Wait for processing

### 3. Verify Upload Success

**After upload completes:**
1. Search for account numbers in EPV
2. Verify each account appears in results
3. Check password and MFA entries exist
4. Confirm all GovCloud accounts present

## Manual Process (Not Recommended)

If automation fails, manual process involves:
1. Log into each GovCloud account individually
2. Configure administrator password manually
3. Enable and save MFA seed manually
4. Manually populate EPV spreadsheet template
5. Export and upload CSV

**Note:** Manual process is time-consuming and error-prone. Use automation whenever possible.

## Troubleshooting

### Script Fails to Connect to AWS
**Solutions:**
- Verify AWS credentials valid
- Check PayerAdmin role access granted
- Ensure role start/end dates include today
- Re-authenticate to AWS

### Script Fails on Specific Account
**Solutions:**
- Note which account failed
- Check account exists and is accessible
- Verify account ID is correct
- May need manual intervention for that account
- Continue with other accounts

### Cannot Access EPV Portal
**Solutions:**
- Verify Breakglass Admins access granted
- Check role start/end dates include today
- Ensure VPN/network access configured
- Clear browser cache and retry

### CSV Upload Fails
**Solutions:**
- Verify file is CSV format (not XLSX)
- Check file size not too large
- Ensure no special characters in data
- Verify column headers match template
- Try uploading smaller batches

### Accounts Not Appearing in EPV
**Solutions:**
- Wait 5-10 minutes for processing
- Refresh EPV search
- Check upload logs for errors
- Verify safe/folder location correct
- May need to re-upload

### Commercial Accounts in Spreadsheet
**Solutions:**
- Remove Commercial accounts before upload
- Only GovCloud accounts should be included
- Commercial uses PayerAdmin role (no EPV needed)

## Security Considerations

### Handling Sensitive Data

**During Process:**
- Keep credentials secure at all times
- Don't save files to shared drives
- Delete local copies after upload
- Use encrypted channels only

**Classification:**
- Always mark spreadsheet as Restricted FR
- This is highest classification level
- Required for password/MFA data
- Must be maintained throughout process

**Access Control:**
- Only use time-bound privileged roles
- Request minimum duration needed
- Roles auto-expire at midnight
- Request access only when ready to work

### Best Practices

- Don't share EPV credentials
- Delete local CSV after successful upload
- Verify upload success before deleting
- Document completion in project story
- Remove privileged access after completion

## Validation Checklist

**Spreadsheet Generation:**
- [ ] Script ran successfully
- [ ] Output file created
- [ ] Only GovCloud accounts present
- [ ] All accounts included
- [ ] Passwords generated for all accounts
- [ ] MFA seeds configured for all accounts
- [ ] Account IDs verified correct
- [ ] Classification set to Restricted FR
- [ ] Exported as CSV format

**EPV Upload:**
- [ ] Breakglass access granted
- [ ] CSV file uploaded successfully
- [ ] Upload completed without errors
- [ ] All accounts searchable in EPV
- [ ] Passwords retrievable
- [ ] MFA seeds present
- [ ] Local copies securely deleted

**Post-Upload:**
- [ ] Project story updated
- [ ] Privileged access removed
- [ ] Local files deleted
- [ ] Validation documented

## Timeline

**Script Execution:** 10-30 minutes (depends on number of accounts)  
**EPV Upload:** 5-10 minutes  
**Upload Processing:** 5-15 minutes  
**Validation:** 10-15 minutes  
**Total Time:** 30-70 minutes

## Next Steps

After EPV configuration completes:
1. Verify all accounts in EPV
2. Securely delete local files
3. Remove privileged access (roles expire automatically)
4. Update project story with completion status
5. Proceed to Step 900 (Perform LZ QA)

## Important Notes

### GovCloud Only
- Only GovCloud accounts go into EPV
- Commercial accounts excluded (use PayerAdmin instead)
- Script should filter automatically
- Double-check before upload

### Time-Bound Access
All privileged roles expire at midnight:
- Plan work accordingly
- Request access day-of if possible
- Don't request days in advance
- Roles cannot be extended once expired

### Automation Benefits
- Faster than manual process
- Fewer errors
- Consistent formatting
- Automated password generation
- MFA seed configuration
- Direct upload to spreadsheet

### Why This Matters
EPV enables:
- Emergency access to accounts
- Password rotation
- Audit trails
- Privileged access management
- Compliance requirements
- Break-glass scenarios

Without EPV:
- No emergency access capability
- Cannot recover from credential loss
- Compliance gaps
- Security vulnerabilities
