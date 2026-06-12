# Post-Build Step 720: Dynatrace Onboarding

## Overview
Onboard landing zone to application performance monitoring platform (Dynatrace) for monitoring OneAgent metrics. Uses SAML AD authentication for access.

## Prerequisites

### Before Starting
- [ ] Order details complete in project feature
- [ ] Project owner updated feature with latest information
- [ ] Complete early to allow time for subsequent onboarding steps
- [ ] AD group created in Step 220 (Pre-Build)

### Exclusions
❌ **Do NOT include:** Proving Ground accounts

## Background

Dynatrace is hosted in secure Tier M environment and provides monitoring for:
- On-Premises systems
- Cloud 1.0 environments
- Cloud 2.0 environments (CFS 2.0)

**Access Requirements:**
- Tier M SSL VPN access (customer responsibility)
- AD group membership (customer responsibility)
- Management zone configuration (Build Factory)

## Process Overview

### Customer Responsibilities (Steps 1-2)
1. Request Tier M SSL VPN Gateway access
2. Request AD group membership (add/remove users)

### Build Factory Responsibility (Step 3)
Submit Dynatrace onboarding request with landing zone account information.

## Step 1: SSL VPN Gateway Access (Customer)

**Note:** If customer already has access to Tier M monitoring SSL VPN group, skip to Step 2.

**Customer Action:**
- Submit SSL VPN access request
- Request Tier M monitoring VPN access
- Wait for approval and provisioning

**Build Factory:** No action required. Inform customer if needed.

## Step 2: AD Group Membership (Customer)

**Prerequisite:** AD group created in Pre-Build Step 220

**Customer Action:**
- Request to be added to monitoring AD group
- AD group name found in feature metadata
- Format: `FRITG-DEM-<LOB>-USERS`

**Build Factory:** Provide AD group name to customer if needed.

## Step 3: Submit Dynatrace Onboarding Request

### Access Portal

Navigate to: Dynatrace Onboarding - IT Service Portal

### Complete Request Form

**Requested for:**  
Build engineer processing this request

**Do you know your Dynatrace AD Group:**  
Yes

**AD Group Name:**  
From meta file in feature metadata  
Example: `FRITG-DEM-NIT-APPNAME-V3-USERS`

**Environment:**  
Prod

**Does your team have a Management Zone:**  
No (for new landing zones)

**What would you like to name your new Management Zone?**  
Format: `<OU>-<BU>-<app_name>`  
Example: `NIT-ISN-P1-APPNAME`

**Host Names to add to the new Management Zone:**  
Landing zone name: `<lz-name>`

**Request Summary:**  
Landing Zone Information table with accounts

### Request Summary Table Format

```
Landing Zone Information:

Account Purpose | AWS Account ID | AWS Account Alias
----------------|----------------|------------------
dev             | <dev-id>       | cfs-base01-gov-<lz>-dev
test            | <test-id>      | cfs-base01-gov-<lz>-test
uat             | <uat-id>       | cfs-base01-gov-<lz>-uat
staging         | <staging-id>   | cfs-base01-gov-<lz>-staging
prod            | <prod-id>      | cfs-base01-gov-<lz>-prod
services-nonprod| <svc-np-id>    | cfs-base01-gov-<lz>-services-nonprod
services-prod   | <svc-p-id>     | cfs-base01-gov-<lz>-services-prod
```

**Important:** 
- Exclude Proving Ground from table
- Include only accounts that exist for this LZ

**Additional Comments:**  
"This request is from the Build Factory Onboarding team"

### Submit Request

Review all fields and submit form.

## Post-Submission

### Track Request
- Capture request ticket number
- Update project story with ticket number
- Monitor for completion

### Customer Notification
Inform customer that:
- Dynatrace onboarding request submitted
- They need SSL VPN and AD group access to use Dynatrace
- Provide Dynatrace access instructions (see below)

## Using Dynatrace (Customer Reference)

### Access Prerequisites
Before logging into Dynatrace, ensure:
- [ ] Access to environment requested and actioned
- [ ] NRAS token connected to device
- [ ] Pulse VPN connection established
- [ ] SafeNet MFA authentication configured

### Environment URLs
- **Development:** `https://demdev.frb.org`
- **QA:** `https://demqa.frb.org`
- **Production:** `https://dem.frb.org`

## Support & Issues

### DEM Enablement Help
Contact Dynatrace team via monitoring enablement help chat channel.

**Team Members:**
- Monitoring enablement specialists
- Infrastructure monitoring team

**Common Issues:**
- Access problems
- Management zone configuration
- Agent installation
- Metric collection

## Troubleshooting

### AD Group Name Not Found
**Solutions:**
- Verify Step 220 completed
- Check feature metadata for AD group name
- Ensure format: `FRITG-DEM-<LOB>-USERS`
- Contact customer if name missing

### Account IDs Missing
**Solutions:**
- Verify Step 400 VM execution completed
- Check Step 510 account page
- Get account IDs from knowledge base page
- Exclude Proving Ground

### Customer Can't Access Dynatrace
**Common Issues:**
- SSL VPN not connected
- AD group membership not provisioned
- MFA not configured
- Wrong environment URL

**Customer Actions:**
- Verify VPN connection
- Confirm AD group membership
- Set up MFA
- Use correct environment URL

### Management Zone Not Created
**Solutions:**
- Verify request submitted successfully
- Check request ticket status
- Follow up with Dynatrace team
- Provide additional information if requested

## Validation

### Verify Onboarding Complete
- [ ] Request submitted successfully
- [ ] Ticket number captured
- [ ] Dynatrace team confirmed completion
- [ ] Management zone created
- [ ] Customer has VPN access
- [ ] Customer has AD group membership
- [ ] Customer can log into Dynatrace
- [ ] Hosts visible in management zone

## Quality Checklist

**Pre-Submission:**
- [ ] Step 220 AD group created
- [ ] AD group name from feature metadata
- [ ] Account IDs from Step 510 page
- [ ] Proving Ground excluded
- [ ] Management zone name follows format
- [ ] Request summary table complete

**Submission:**
- [ ] All required fields populated
- [ ] AD group name correct
- [ ] Account information accurate
- [ ] Management zone name valid
- [ ] Request submitted successfully
- [ ] Ticket number recorded

**Post-Submission:**
- [ ] Project story updated
- [ ] Customer notified of requirements
- [ ] Dynatrace team confirmed completion
- [ ] Customer access validated
- [ ] Management zone visible

## Timeline

**Build Factory Submission:** 1 day  
**Dynatrace Team Processing:** 3-5 business days  
**Customer VPN/AD Setup:** Variable (customer-dependent)  
**Total Time:** 1-2 weeks

## Next Steps

After Dynatrace onboarding completes:
1. Update project story with completion status
2. Verify customer can access Dynatrace
3. Proceed to Step 800 (Configure EPV)
4. Include Dynatrace validation in QA (Step 900)

## Important Notes

### Customer Dependencies
This step has significant customer dependencies:
- SSL VPN access request
- AD group membership request
- MFA configuration

Plan accordingly for customer-dependent delays.

### Early Submission
Submit this request as early as possible to allow time for:
- Customer VPN setup
- AD group provisioning
- Dynatrace team processing
- Testing before QA step

### Management Zone Naming
Follow organizational naming convention:
- Format: `<OU>-<BU>-<app_name>`
- Use from feature metadata
- Ensures consistency across monitoring platform

### Proving Ground Exclusion
Never include Proving Ground in Dynatrace onboarding:
- Temporary testing environment
- Not for production monitoring
- Would clutter management zone
