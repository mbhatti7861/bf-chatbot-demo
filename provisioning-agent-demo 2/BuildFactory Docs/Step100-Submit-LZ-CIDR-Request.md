# Pre-Build Step 100: Submit LZ CIDR Request

## Overview
Allocate CIDR ranges for new landing zones or accounts by calling automation platform APIs. Generated CIDRs are used to create parameter files for the infrastructure build step.

## Prerequisites
- Cloud engineer role access (5 accounts: 2 legacy build, 2 app hosting, 1 base services)
- LZ Build Prep repository cloned
- Python virtual environment configured
- Meta YAML file from Step 10

## Environment Setup
```bash
# Clone repository
git clone <lz-build-prep-repo-url>

# Create virtual environment
python -m venv .bfvenv

# Activate (Windows PowerShell)
.bfvenv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Authenticate
.\auth.ps1
```

## Process Summary

### 1. Start Application
```bash
python src/main.py
```

### 2. Import Metadata File
- Download meta YAML file from project management feature (created in Step 10)
- Click "Import" button in application
- Select the `<lz_name>_meta.yml` file
- Filter by LZ name to verify import

### 3. Generate CIDR Ranges
- Locate your LZ in the list
- Expand "Action" dropdown for the LZ row
- Click "Build" option
- Build dialog appears showing account sections
- Click "Generate CIDRs" button

**Important Notes:**
- Services accounts (prod/non-prod) always assigned 'Internal' location even for 'External' landing zones
- Full LZ CIDR generation can take up to 20 minutes
- Re-authenticate before starting to avoid timeout issues
- Monitor terminal output during generation

### 4. Verify Completion
- Watch terminal for progress
- Completion dialog appears: "CIDR generation is complete"
- Form refreshes showing generated CIDRs at top
- Automated emails sent for each CIDR range generated

## Troubleshooting

### Generation Stops Without Dialog
Check the following:
1. Review log and call stack in terminal
2. Query database to see which CIDR records were inserted
3. Review automated emails to identify completed CIDRs
4. Identify which accounts failed

### Common Issues

**Timeout During Generation**
- Re-authenticate before starting
- Ensure stable network connection
- Contact automation platform team if API issues suspected

**Missing CIDRs**
- Check database for partial completion
- Review automated emails for successfully created ranges
- May need to retry failed accounts

**IP Overlap Issues**
- Contact cloud network team
- Request IPAM reports showing used vs available IPs

## Integration Points

**Database**: Pulls data from LZ metadata table
**Metadata File**: Uses meta YAML from Step 10
**Automation Platform**: Calls APIs for CIDR allocation
**Email System**: Auto-generates notification emails

## Support Contacts

**Tooling Issues**: Build Factory team (LZ Build Prep application errors)
**Automation Platform Issues**: Network operations team
**IP Overlap/IPAM**: Cloud network team
**IP Availability Monitoring**: Cloud network team

## Quality Checks
- [ ] Authenticated before starting (to avoid timeout)
- [ ] Metadata file imported successfully
- [ ] All accounts show in build dialog
- [ ] Generation completed without errors
- [ ] CIDRs visible in application UI
- [ ] Automated emails received for all ranges
- [ ] Database records created for all accounts
