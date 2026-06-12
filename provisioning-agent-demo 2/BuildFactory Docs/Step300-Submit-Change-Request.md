# Pre-Build Step 300: Submit Change Request for LZ Build

## Overview
Create a change request to authorize the landing zone build. Standard changes are pre-approved and only require assignment and scheduling.

## Standard Change Types

### Option 1: Create New Landing Zone
**Template**: Build new Landing Zone  
**Use For**: Net-new landing zone with all accounts

### Option 2: Add Account to Existing LZ
**Template**: Add Additional Accounts to an Existing Landing Zone  
**Use For**: Adding Dev, Test, or Prod accounts to existing LZ

### Option 3: Modify Existing LZ
**Template**: Make changes to an existing landing zone  
**Use For**:
- Add non-routable IP addresses
- App density requests (add application CIs to existing accounts)
- Add or remove CMDB data
- Other configuration changes

## Process

### 1. Navigate to Standard Changes
Access change management system and locate standard change templates.

### 2. Select Appropriate Template
Choose the template that matches your LZ work type (see above).

### 3. Complete Change Fields

**Assignment Tab:**
- **Assigned To**: Person running the infrastructure automation (usually you)
- **Assignment Group**: Build Factory team

**Schedule Tab:**
- **Planned Start Date**: Can be immediate (no 24hr lead time required)
- **Planned End Date**: Typically 1 week from start
- **Duration**: Should not exceed 1 week

**Important Prerequisites:**
⚠️ Ensure CIDR blocks are created (Step 100) before implementation start date

### 4. Submit Change
Click Submit to create the change.  
**Status**: Change moves to "New" (draft state)

### 5. Schedule Change
Once change created:
1. Open the change request
2. Click "Schedule" button
3. No additional approvals needed
4. **Status**: Change moves to "Scheduled" (ready for implementation)

**Note**: Change must be assigned to a person before it can be scheduled.

## During Implementation

### Update Status to Implement
1. Open change request
2. Change status from "Scheduled" to "Implement"
3. Begin actual infrastructure work

### Document Activities
In the Notes tab, document:
- Start time
- Steps completed
- Any issues encountered
- Resolution steps
- Completion time

## Post Implementation

### 1. Update Schedule Tab
- **Actual Start Date**: When work actually began
- **Actual End Date**: When work actually completed

### 2. Complete Closure Information
- **Close Code**: Select appropriate closure reason (usually "Successful")
- **Close Notes**: Summary of work completed and any relevant details

### 3. Close Change
Change status to "Closed" in the upper right.

## Best Practices

### Timing
- Standard changes can start immediately
- Plan for realistic timeframe (typically 3-5 days)
- Don't schedule beyond 1 week duration

### Documentation
- Document all significant steps in Notes tab
- Include timestamps for major milestones
- Note any deviations from plan
- Record any issues and resolutions

### Prerequisites
Before scheduling:
- [ ] CIDR generation complete (Step 100)
- [ ] Non-Okta roles submitted (Step 200)
- [ ] Observability access submitted (Step 210)
- [ ] Monitoring AD group submitted (Step 220)
- [ ] All pre-build steps complete

## Change Lifecycle

```
New (draft)
    ↓
Scheduled (approved & ready)
    ↓
Implement (work in progress)
    ↓
Review (validate completion)
    ↓
Closed (complete)
```

## Quality Checks
- [ ] Correct standard change template selected
- [ ] Assigned to correct person
- [ ] Schedule dates reasonable (not > 1 week)
- [ ] CIDR blocks created before start date
- [ ] Change successfully scheduled
- [ ] Change ticket number captured for reference
- [ ] Activities documented during implementation
- [ ] Actual dates recorded
- [ ] Change properly closed with notes

## Troubleshooting

### Cannot Schedule Change
- Verify change is assigned to a person
- Check that Planned Start Date is set
- Ensure Planned End Date is after Start Date

### Schedule Dates in Past
- Update to current/future dates
- Submit change again if needed

### Missing Prerequisites
- Don't schedule until all pre-build steps complete
- Especially ensure CIDR blocks are generated

## Next Steps
Once change is scheduled:
- Proceed to Build Phase
- Execute infrastructure automation
- Document progress in change Notes tab
- Close change upon completion
