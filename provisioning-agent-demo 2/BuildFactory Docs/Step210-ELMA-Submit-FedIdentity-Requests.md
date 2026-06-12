# Pre-Build Step 210: ELMA - Submit FedIdentity Requests

## Overview
Grant primary GitLab owner access to the observability access request system so they can approve onboarding requests for their landing zone.

## Process

### 1. Verify Existing Access
Check if primary GitLab owner already has access to the observability access request portal.

### 2. Submit FedIdentity Request (if needed)

**Request Details:**
- **On Behalf Of**: Primary GitLab owner (from LZ metadata)
- **Access Group**: Observability Access Request - Production Application Assignment Group
- **Business Justification**: "Required access to approve observability onboarding requests for landing zone"

### 3. Follow Up
If request still pending after 2 business days, follow up with identity management team.

### 4. Validate Access
Once request completed, verify primary GitLab owner can:
- Access observability access request portal
- Navigate to "My Approvals" section
- See approval workflow options

## Quality Checks
- [ ] Primary GitLab owner identified correctly
- [ ] FedIdentity request submitted
- [ ] Request completed within SLA
- [ ] Portal access validated
- [ ] Approval workflow accessible

## Notes
- This access is required before QA step
- Enables GitLab owner to approve team member access to observability data
- Without this, observability onboarding is blocked
