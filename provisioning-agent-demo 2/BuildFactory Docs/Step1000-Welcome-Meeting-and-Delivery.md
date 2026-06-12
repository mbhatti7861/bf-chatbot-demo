# Post-Build Step 1000: Welcome Meeting Invite & Delivery

## Overview
Schedule welcome meeting with customer and internal stakeholders to officially deliver the landing zone. Close ServiceNow request and transition to customer ownership.

## Prerequisites

### Required Completions
- [ ] Step 800: Configure EPV completed successfully
- [ ] Step 900: Perform LZ QA completed successfully
- [ ] All critical defects resolved
- [ ] Welcome Kit generated (Step 500)
- [ ] Account page created (Step 510)

### PO Approval Required
If build has outstanding defects:
- Consult with Product Owner
- Determine if LZ can be delivered with open defects
- Document approval decision
- Plan for defect resolution post-delivery

## Welcome Meeting Setup

### Required Invitees

**Customer Contacts (from feature metadata):**
- Submitted By (from ServiceNow request)
- LZ Owner
- GitLab Primary Owner
- GitLab Secondary Owner
- Technical Contact
- Lead Architect
- Application Contact
- Cloud Technical Coordinator (CTC)
- Technology Services Manager (TSM)
- Business Dedicated Group Contact

**Internal Teams (Always Required):**
- Cloud services management team
- Cloud financial management team
- Customer engagement team
- Specific named stakeholder

**FRFS Landing Zones Only:**
- FRFS financial operations team

**CICD Landing Zones Only:**
- GitLab usage support team

**Optional Attendees:**
- Customer engagement specialists
- Additional stakeholders as needed

### Meeting Details

**Title:**  
`Landing Zone Welcome Meeting (<lz-name>)`

**Duration:** 30 minutes

**Timing:**
- Schedule at least a few days out
- Choose "middle of day" time (accommodate time zones)
- Check customer engagement team availability (they conduct meeting)
- Ensure majority of required customer contacts available

**Meeting Platform:**
- Add Teams meeting link
- Enable recording if permitted

### Required Attachments

1. **Welcome Kit (PDF)**  
   From Step 500 output

2. **Hybrid Welcome Meeting Presentation**  
   Standard deck covering onboarding process

### Meeting Invite Body

```
Welcome to the Hybrid Engagement Model in CFS 2.0. The attached Welcome 
Packet, access instructions, and community channel link will assist in 
getting started. Please keep these artifacts and links handy. 

We encourage you to register for the Hybrid and CICD Technical Overview 
training sessions as soon as your schedule permits. Training is typically 
offered Thursday afternoons.

The Welcome Packet provides the account numbers for your Landing Zone. 
These account numbers are required to request access. The access 
instructions will guide you through requesting access to your landing zone.

📚 Key Resources:
• Hybrid Onboarding Resources - Links to get started
• CICD Onboarding Resources - CICD-specific guidance  
• Landing Zone Learning Hub - Training and documentation
• National IT Contacts - Support team information
• Landing Zone Overview - Architecture and design
• Roles and Responsibilities - Team structure
• Release Management - Deployment processes
• Finance and Optimization - Cost management

🎯 Next Steps:
Please join our CFS Hybrid Customer Community Channel to connect with 
others throughout the System operating in the CFS Hybrid environment.

[Community Channel Link]
```

## Close ServiceNow Request

### Locate ServiceNow Request

**Method 1: From Feature**
1. Navigate to feature view in project system
2. Find ServiceNow request link at top
3. Click to open request

**Method 2: Direct Search**
1. Search ServiceNow for request number
2. Use LZ name as search term

### Update Quality Inspection Task

**Step 1: Note Build Prep Assignee**
- Locate tasks at end of ServiceNow request
- Find "Build Prep" task
- Note the "Assigned to" name

**Step 2: Open Quality Inspection Task**
- Locate "Quality Inspection" task
- Note: Assigned to and Actual end should be empty

**Step 3: Update Quality Inspection Task**

**Assigned to:**  
Use same name from Build Prep task

**State:**  
Change to "Closed"

**Actual End Date:**  
Auto-populated on close

**If No Welcome Meeting Required:**
- Input Welcome Packet shareable link (from Step 500 story)
- Select "Yes" to "Send Welcome Packet"
- ServiceNow will email Welcome Packet when task closed

**Action:**  
Click "Update" to save changes

### Verify Task Closure

**Confirmation:**
- Task status shows "Closed"
- Actual end date populated
- You receive ServiceNow email confirmation
- Welcome email sent (if no meeting option selected)

### ServiceNow Email Confirmation

You will receive email confirming:
- Task closed successfully
- Quality inspection complete
- LZ delivered
- Timestamp of closure

## Welcome Meeting Checklist

**Before Meeting:**
- [ ] All required attendees invited
- [ ] Customer engagement team confirmed attendance
- [ ] Welcome Kit attached
- [ ] Presentation deck attached
- [ ] Teams meeting link added
- [ ] Meeting scheduled 2-3 days out
- [ ] Time works for majority of required attendees

**Meeting Preparation:**
- [ ] Review Welcome Kit contents
- [ ] Understand any open defects
- [ ] Prepare to answer questions
- [ ] Have support contacts ready
- [ ] Know escalation paths

**During Meeting:**
- [ ] Customer engagement leads meeting
- [ ] Welcome Kit reviewed
- [ ] Access process explained
- [ ] Training opportunities shared
- [ ] Community channel promoted
- [ ] Questions answered
- [ ] Next steps clarified

**After Meeting:**
- [ ] Meeting notes captured
- [ ] Action items documented
- [ ] Follow-up scheduled if needed
- [ ] Customer onboarding begins

## Alternative: No Meeting Delivery

### When Appropriate
- Customer requests async delivery
- Scheduling conflicts
- Simple/repeat customer
- Time zone challenges

### Process
1. Complete ServiceNow Quality Inspection task
2. Select "Yes" to "Send Welcome Packet"
3. Add Welcome Packet shareable link
4. ServiceNow automatically sends email
5. Email includes Welcome Kit and resources

### Email Contents (Automated)
- Welcome message
- Welcome Kit attachment/link
- Access instructions
- Training resources
- Support contacts
- Community channel link

## Post-Delivery Activities

### Update Documentation
- Mark project story as complete
- Update LZ tracking spreadsheet
- Archive build artifacts
- Document lessons learned

### Transition to Support
- Remove Build Factory access
- Customer requests access via FedIdentity
- Support team monitoring begins
- Handoff to operational teams

### Monitor Initial Usage
- Check for access requests
- Verify customer able to log in
- Monitor for support tickets
- Proactive outreach if issues

## Troubleshooting

### Cannot Close Quality Inspection Task
**Solutions:**
- Verify you have ServiceNow permissions
- Check task dependencies
- Ensure previous tasks closed
- Contact ServiceNow admin

### Customer Contacts Missing
**Solutions:**
- Review feature metadata carefully
- Check ServiceNow request submission
- Contact requestor for clarification
- Add known contacts, follow up on others

### Can't Find Build Prep Assignee
**Solutions:**
- Check all tasks in ServiceNow request
- Look at request history
- Default to yourself if unclear
- Document assumption

### Welcome Meeting Scheduling Conflicts
**Solutions:**
- Prioritize customer contacts
- Check customer engagement team availability
- Consider alternative times/days
- May need multiple sessions for large teams

### ServiceNow Email Not Received
**Solutions:**
- Check spam/junk folder
- Verify email address in profile
- Wait 15-30 minutes for delivery
- Check task actually saved/closed

## Quality Checklist

**Meeting Invite:**
- [ ] All required customer contacts invited
- [ ] All required internal teams invited
- [ ] FRFS team included (if FRFS LZ)
- [ ] CICD team included (if CICD LZ)
- [ ] Title correct with LZ name
- [ ] Duration set to 30 minutes
- [ ] Teams meeting link added
- [ ] Welcome Kit PDF attached
- [ ] Welcome presentation attached
- [ ] Body text includes all resources
- [ ] Community channel link included
- [ ] Scheduled appropriately

**ServiceNow Closure:**
- [ ] ServiceNow request located
- [ ] Build Prep assignee noted
- [ ] Quality Inspection task opened
- [ ] Assigned to correct person
- [ ] State changed to Closed
- [ ] Welcome Packet link added (if no meeting)
- [ ] Send Welcome Packet selected (if no meeting)
- [ ] Task saved/updated
- [ ] Confirmation email received
- [ ] Task shows closed in request

**Post-Delivery:**
- [ ] Project story marked complete
- [ ] Build artifacts archived
- [ ] Access removed
- [ ] Handoff to support documented
- [ ] Lessons learned captured

## Timeline

**Meeting Scheduling:** 2-3 days notice  
**ServiceNow Closure:** 15 minutes  
**Customer Onboarding Begins:** Immediately after delivery  

## Important Notes

### This is Customer Handoff
- Formal transition from build to operations
- Customer takes ownership
- Support model begins
- Build Factory disengages (except for issues)

### ServiceNow Closure Triggers
Closing Quality Inspection task:
- Marks LZ as delivered
- Updates dashboards/metrics
- Triggers reporting
- Completes order fulfillment

### Customer Engagement Team Leads Meeting
- They are trained facilitators
- Know the onboarding process
- Have presentation materials
- Can answer customer questions
- Build Factory attends but doesn't lead

### Welcome Kit is Critical
- Contains all access information
- Required for customer to get started
- Reference document going forward
- Keep version with LZ artifacts

### Post-Delivery Support
- Customer requests own access
- Uses Welcome Kit for guidance
- Support team monitors
- Build Factory available for major issues only
