# Post-Build Step 520: Partner Notification

## ⚠️ PROCESS CHANGE NOTICE
This step has been **replaced by automated ServiceNow workflow**.  
See: ServiceNow Landing Zone Order - Fulfillment process documentation

## Historical Context (For Reference)

### Original Purpose
Partner Notice was sent to trigger work and onboarding with multiple operational teams. This was a **vital step** that initiated parallel onboarding activities.

### Recipients (Historical)
Email was sent from team mailbox to:
- Threat management team
- Security deployment team
- Cloud security management team
- Security operations team
- Cloud security posture management team
- Observability operations team

## Current Process

### ServiceNow Workflow Handles This Automatically
The landing zone order fulfillment workflow in ServiceNow now:
- Automatically notifies partner teams
- Tracks onboarding progress across teams
- Manages dependencies between steps
- Provides visibility into status

### When to Use Manual Process
Only use manual notification if:
- ServiceNow automation fails
- Emergency/exception scenario
- Explicitly requested by leadership
- System outage requires workaround

## Manual Process (Exception Cases Only)

### Prerequisites
- Step 400: VM execution complete (produces account numbers)
- Step 500: Welcome Kit generated
- Step 510: Confluence page created

### Timing
- Send after Welcome Kit and Confluence pages are created
- For multiple LZs in same sprint, batch into one email to reduce notifications

### Email Template Structure

**From:** Team mailbox

**To:** All partner team distribution lists (see historical recipients above)

**Subject:** Notification of incoming cloud workloads

**Body Structure:**
```
This is a notification of incoming [cloud version] workloads.

The following landing zones have completed build and are currently 
going through the post build process.

We anticipate delivering these landing zones to the customers in 
the next few weeks.

Please contact [team mailbox] for any questions.

[TABLE - See below]
```

### Required Table Format

**Headers:**
- Project Feature Link
- VMS Group
- Security Group  
- Account Page Link

**Content Per LZ:**
- Feature: Link to project management feature
- VMS Group: From feature metadata
- Security Group: Security posture group name
- Account Page: Link to Confluence page from Step 510

**Example Row:**
| Feature | VMS Group | Security Group | Account Page |
|---------|-----------|----------------|--------------|
| FEATURE-123 | example-vms-group | All-Accounts | [Link to Confluence] |

### How to Populate Table

**Feature Link:**
- Find LZ in project management system
- Copy link to feature

**VMS Group:**
- Found in feature metadata
- Listed as VMS support group

**Security Group:**
- Typically "All-Accounts" for standard LZ
- Verify in security tooling configuration

**Account Page Link:**
- Copy URL from Step 510 (Confluence page)
- Verify link is accessible before sending

## Validation Checklist

Before sending manual notification:
- [ ] Step 400 complete (all accounts created)
- [ ] Step 500 complete (Welcome Kit generated)
- [ ] Step 510 complete (Confluence page created)
- [ ] All links in email are functional
- [ ] Table data is accurate for each LZ
- [ ] Email sent from team mailbox (not personal)
- [ ] All partner teams included in TO field
- [ ] Team distribution list in CC
- [ ] Spelling and grammar checked

## After Sending

### Track Responses
- Monitor team mailbox for questions
- Respond to partner team inquiries
- Track onboarding progress manually
- Follow up with teams as needed

### Document in ServiceNow
- Update LZ order ticket with email timestamp
- Note that manual process was used
- Include reason for exception
- Attach email for audit trail

## Troubleshooting

### ServiceNow Automation Not Working
**When to escalate:**
- Multiple LZ orders affected
- Automation has been broken >24 hours
- Partner teams reporting missed notifications

**Temporary workaround:**
- Use manual email process above
- Document each manual notification
- Report automation issue to platform team

### Partner Teams Not Receiving Notifications
**Check:**
- Distribution lists are current
- Email not blocked/quarantined
- Team mailbox has send permissions
- Links in email are accessible

**Resolution:**
- Verify recipient addresses
- Resend from team mailbox
- Contact recipients directly if urgent

### Missing Information for Table
**Feature link missing:**
- Verify feature created in Step 10
- Check project management system

**VMS group missing:**
- Review feature metadata
- Contact requestor if not documented

**Account page link missing:**
- Ensure Step 510 completed
- Recreate Confluence page if needed

## Quality Notes

### Why This Was Critical (Historical)
- **Triggered parallel work**: Multiple teams began onboarding simultaneously
- **Prevented delays**: Teams waited for this notification to start work
- **Compliance requirement**: Documented handoff to operational teams
- **Coordination point**: Single notification synchronized multiple teams

### Why ServiceNow Is Better
- **Automated**: No manual email required
- **Trackable**: Progress visible to all stakeholders
- **Reliable**: No risk of forgotten notifications
- **Integrated**: Tied to overall LZ order workflow
- **Auditable**: Full history in ServiceNow

## Next Steps

### If Using ServiceNow (Normal Process)
1. Verify ServiceNow triggered partner notifications
2. Monitor tasks in partner team queues
3. Proceed to Step 600 (CICD Onboarding)

### If Using Manual Process (Exception)
1. Send partner notice email
2. Document in ServiceNow ticket
3. Monitor team mailbox for responses
4. Proceed to Step 600 (CICD Onboarding)

## Reference
- ServiceNow LZ Order Fulfillment: See ServiceNow documentation
- Historical email examples: Check team SharePoint archives
- Partner team contacts: See team contact list in knowledge base
