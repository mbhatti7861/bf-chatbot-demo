# Pre-Build Step 220: Dynatrace - Submit AD Info

## Overview
Create Active Directory group for monitoring platform access to enable application performance monitoring for the landing zone.

## Prerequisites
- LZ Owner name (from metadata)
- GitLab Primary and Secondary owner login IDs (from feature metadata)
- Monitoring platform AD group name (from feature metadata)
- Cost Center Work Unit (CCWU) information

## Process

### 1. Access Service Request System
Navigate to Active Directory group management in service request platform.

### 2. Submit AD Group Creation Request

**Required Fields:**

**Basic Information:**
- **Requested For**: LZ Owner name
- **Request Type**: Create AD/ED Group
- **Environment**: Active Directory
- **Ownership**: National IT (not district)
- **Domain**: Enterprise domain identifier

**Group Configuration:**
- **Proposed Group Name**: Use naming from feature metadata
  - Format: `FRITG-DEM-{LOB}-USERS` (MUST start with FRITG-DEM)
- **Access Type**: Provide
- **Access Level**: Read-only user
- **Environment Type**: Production
- **Application Name**: Dynatrace application
- **Application Description**: "Automatically detect performance anomalies in your applications, services, and infrastructure"

**Additional Details:**
- **Additional Info**: "For the {landing_zone_name} landing zone. Dynatrace access to Dev and QA will also be needed."
- **Owning Cost Center Work Unit (CCWU)**: See lookup instructions below
- **Privileged Entitlement**: No
- **Add to Group**: User Logon ID
- **User Logon IDs**: Semicolon-separated list of GitLab owners (Primary;Secondary)

**Business Justification:**
"This request is from the Build Factory. We are helping a customer onboard to Dynatrace."

### 3. Find Cost Center Work Unit (CCWU)

**Steps:**
1. Navigate to organizational reporting system
2. Search for application or team
3. Locate CCWU code
4. CCWU Name auto-generates from code selection

### 4. Submit Request
Review all fields and submit the AD group creation request.

## Important Notes

### Naming Convention
⚠️ **CRITICAL**: Group name MUST begin with `FRITG-DEM`

Example: `FRITG-DEM-MARKETS-USERS`

### User IDs
- Primary GitLab owner (required)
- Secondary GitLab owner (required)
- Both found in feature metadata YAML file

### Access Scope
Request should note that Dev and QA access will also be needed (in addition to Production).

## Troubleshooting

### Cannot Find CCWU
- Contact LZ owner or application team
- Check application registration system
- Use organizational hierarchy lookup tool

### Invalid Group Name
- Verify starts with `FRITG-DEM`
- Check for special characters
- Ensure follows naming standards

### User IDs Not Found
- Verify user IDs in feature metadata
- Check FedIdentity for correct format
- Confirm users exist in directory

## Quality Checks
- [ ] LZ owner identified correctly
- [ ] AD group name follows FRITG-DEM-* convention
- [ ] Both GitLab owners included
- [ ] CCWU located and entered
- [ ] Business justification included
- [ ] Request submitted successfully
- [ ] Request ticket number captured

## Next Steps
After AD group creation:
- Group will be used for monitoring platform onboarding
- Users can access performance monitoring data
- Additional team members can be added to group later
