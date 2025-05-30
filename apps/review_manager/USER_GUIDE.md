# Review Manager User Guide

**Version:** 1.0.0  
**Audience:** Researchers, Literature Review Specialists  
**Platform:** Web-based (Desktop & Mobile)  

## Table of Contents

- [Getting Started](#getting-started)
- [Understanding Session Workflow](#understanding-session-workflow)
- [Creating Your First Session](#creating-your-first-session)
- [Managing Sessions](#managing-sessions)
- [Dashboard Overview](#dashboard-overview)
- [Session Details](#session-details)
- [Advanced Features](#advanced-features)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)
- [Keyboard Shortcuts](#keyboard-shortcuts)

## Getting Started

### What is Review Manager?

Review Manager is a powerful tool for conducting systematic literature reviews following PRISMA guidelines. It helps you organize, track, and manage your research process from initial planning through final reporting.

### Key Benefits

- **Organized Workflow**: 9-stage process guides you through each step
- **Complete Audit Trail**: Every action is tracked for compliance
- **Real-time Progress**: Live updates on search execution and processing
- **Collaborative Ready**: Built for team research (Phase 2)
- **Export Friendly**: Generate reports in multiple formats

### System Requirements

- **Web Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Internet Connection**: Required for real-time features
- **Screen Resolution**: 1024x768 minimum (responsive design)
- **JavaScript**: Must be enabled

## Understanding Session Workflow

Each literature review follows a structured 9-stage workflow:

### 1. 📝 Draft
**What it means**: Initial session creation  
**What you can do**: Edit title, description, delete session  
**Next step**: Define your search strategy  

### 2. 🎯 Strategy Ready
**What it means**: Search strategy has been defined  
**What you can do**: Review strategy, modify if needed  
**Next step**: Execute searches across databases  

### 3. ⚡ Executing
**What it means**: Automated searches are running  
**What you can do**: Monitor progress, view real-time updates  
**Duration**: Typically 10-30 minutes depending on scope  

### 4. 🔄 Processing
**What it means**: Search results are being processed and deduplicated  
**What you can do**: Wait for completion, review preliminary statistics  
**Duration**: Typically 5-15 minutes  

### 5. 📋 Ready for Review
**What it means**: Results are prepared for manual review  
**What you can do**: Start reviewing individual papers  
**Next step**: Begin the systematic review process  

### 6. 🔍 In Review
**What it means**: Active manual review is in progress  
**What you can do**: Continue reviewing, add comments, make decisions  
**Duration**: Days to weeks depending on result volume  

### 7. ✅ Completed
**What it means**: Review process is finished  
**What you can do**: Generate reports, export data, archive session  
**Available**: Final PRISMA-compliant reports  

### 8. ❌ Failed
**What it means**: An error occurred in the process  
**What you can do**: View error details, attempt recovery  
**Recovery options**: Retry, reset to previous stage, contact support  

### 9. 📦 Archived
**What it means**: Session is stored for long-term access  
**What you can do**: View reports, unarchive if needed  
**Storage**: Permanent retention with metadata  

## Creating Your First Session

### Step 1: Access the Dashboard

1. Navigate to the Review Manager section
2. You'll see your dashboard with any existing sessions
3. Click **"Create New Session"** button (top-right)

### Step 2: Basic Information

![Create Session Form](images/create-session-form.png)

1. **Session Title** (required)
   - Be descriptive: "Diabetes Management in Elderly Patients 2020-2024"
   - Maximum 200 characters
   - Will appear in reports and exports

2. **Description** (optional)
   - Add research objectives, inclusion criteria, notes
   - Maximum 1000 characters
   - Useful for team members and future reference

### Step 3: Confirmation

1. Review your information
2. Click **"Create Session"**
3. You'll be redirected to the session detail page
4. Status will be "Draft" - ready for next steps

### Step 4: What Happens Next?

- Session appears on your dashboard
- Activity log starts tracking all changes
- You're ready to define your search strategy (next app)

## Managing Sessions

### Dashboard Actions

Each session on your dashboard shows:
- **Title and description**
- **Current status** with color-coded badge
- **Last updated** timestamp
- **Quick action buttons**

#### Available Actions by Status:

| Status | Available Actions |
|--------|------------------|
| Draft | Edit, Delete, Duplicate |
| Strategy Ready | Edit, Duplicate |
| Executing | View Progress, Cancel |
| Processing | Monitor Status |
| Ready for Review | Start Review |
| In Review | Continue Review, Export |
| Completed | View Report, Archive, Export |
| Failed | View Errors, Retry, Reset |
| Archived | View Report, Unarchive |

### Editing Sessions

**Who can edit**: Session creator only  
**What can be edited**: Title and description  
**When editing is allowed**: Draft and Strategy Ready status only  

1. Click **"Edit"** on session card or detail page
2. Modify title and/or description
3. Click **"Save Changes"**
4. Changes are automatically logged

⚠️ **Note**: Once searches begin executing, title and description become read-only for data integrity.

### Deleting Sessions

**Security note**: Only sessions in "Draft" status can be deleted.

1. Click **"Delete"** on session card
2. Confirm deletion in the popup dialog
3. Session is permanently removed
4. All associated data is deleted

⚠️ **Warning**: Deletion cannot be undone. Consider archiving instead.

### Duplicating Sessions

Create a copy of an existing session:

1. Click **"Duplicate"** on any session
2. New session created with same title + "(Copy)" suffix
3. Status reset to "Draft"
4. All original metadata preserved

**Use cases**:
- Run similar searches with different parameters
- Create templates for repeated research types
- Test different strategies on same topic

## Dashboard Overview

### Header Statistics

![Dashboard Header](images/dashboard-header.png)

- **Total Sessions**: All sessions you've created
- **Active Sessions**: Currently in progress (not completed/archived)
- **Completed Sessions**: Successfully finished reviews
- **Completion Rate**: Percentage of sessions reaching completion

### Filtering Options

#### By Status
- **All**: Show all sessions
- **Active**: In-progress sessions only
- **Draft**: Newly created sessions
- **Completed**: Finished sessions
- **Archived**: Long-term storage
- **Failed**: Sessions with errors

#### By Date Range
- **All Time**: No date filtering
- **Today**: Created today
- **This Week**: Created in last 7 days
- **This Month**: Created in last 30 days
- **This Year**: Created in last 365 days

#### By Search
- Enter keywords to search in titles and descriptions
- Search is case-insensitive
- Searches both title and description fields
- Results update as you type

### Sorting Options

- **Status Priority** (default): Most urgent tasks first
- **Recently Created**: Newest sessions first
- **Recently Updated**: Most recently modified first
- **Alphabetical**: Sorted by title A-Z

### Pagination

- **12 sessions per page** for optimal performance
- Navigation controls at bottom
- Page numbers with previous/next buttons
- Total count displayed

## Session Details

### Overview Section

**Session Information**:
- Title and description
- Current status with explanation
- Created and last updated timestamps
- Session ID (for support requests)

**Progress Indicators**:
- Visual progress bar for current stage
- Estimated completion time (for automated stages)
- Real-time status updates

### Activity Timeline

![Activity Timeline](images/activity-timeline.png)

**What's tracked**:
- Session creation and modifications
- Status changes with reasons
- User actions and system events
- Error occurrences and recoveries

**Timeline features**:
- Chronological order (newest first)
- Filter by activity type
- Date range filtering
- Detailed descriptions with context

### Status History

**Transition tracking**:
- Every status change logged
- Duration in each status
- User who made the change
- Automatic vs manual transitions

**Performance analytics**:
- Time spent in each stage
- Bottleneck identification
- Efficiency comparisons

### Quick Actions Panel

**Context-sensitive actions**:
- Different options based on current status
- Primary action highlighted
- Secondary actions in dropdown
- Help text for each action

## Advanced Features

### Real-time Status Monitoring

**Automatic updates**:
- Status changes without page refresh
- Progress bars during long operations
- Visual indicators for active sessions
- Sound notifications (optional)

**How it works**:
- Page checks for updates every 30-60 seconds
- Only active sessions are monitored
- Pauses when page not visible (battery saving)
- Reconnects automatically if connection lost

### Export and Reporting

**Available formats**:
- JSON (complete data export)
- CSV (tabular data)
- PDF (formatted reports)
- PRISMA flow diagrams

**What's included**:
- Session metadata
- Complete activity history
- Search strategy details
- Results summary
- Statistical analysis

### Archive Management

**Archiving benefits**:
- Reduces dashboard clutter
- Preserves all data
- Maintains access to reports
- Frees up active session limits

**Archive operations**:
- Individual session archiving
- Bulk archive selection
- Automatic archiving (configurable)
- Easy unarchiving when needed

### Productivity Analytics

![Analytics Dashboard](images/analytics-dashboard.png)

**Metrics tracked**:
- Sessions completed per month
- Average time per review stage
- Productivity trends over time
- Personal efficiency scores

**Visualization**:
- Interactive charts and graphs
- Drill-down capabilities
- Comparison with previous periods
- Achievement badges and goals

## Tips & Best Practices

### Planning Your Review

1. **Choose descriptive titles**
   - Include topic, time period, population
   - Example: "COVID-19 Mental Health Impact 2020-2023"

2. **Write detailed descriptions**
   - Include research questions
   - Note inclusion/exclusion criteria
   - Add team member information

3. **Plan your workflow**
   - Allocate time for each stage
   - Consider parallel processing where possible
   - Plan for review iterations

### Optimizing Performance

1. **Use filtering effectively**
   - Filter by status to focus on actionable items
   - Use date ranges for recent work
   - Search by keywords for quick access

2. **Monitor system status**
   - Check progress indicators regularly
   - Don't interrupt executing searches
   - Use recovery options if errors occur

3. **Manage session lifecycle**
   - Archive completed sessions
   - Delete draft sessions you won't use
   - Duplicate sessions for similar research

### Collaboration Best Practices

1. **Naming conventions**
   - Use consistent naming patterns
   - Include project codes if applicable
   - Add team member initials for personal sessions

2. **Documentation**
   - Use description field for important notes
   - Document decision rationale in activity comments
   - Export data regularly for backup

3. **Communication**
   - Share session IDs for support requests
   - Use activity timeline for progress updates
   - Export reports for team meetings

### Security Considerations

1. **Access control**
   - Only you can see your sessions
   - Log out when using shared computers
   - Report suspicious activity immediately

2. **Data protection**
   - All actions are logged for audit
   - Sessions cannot be deleted once in progress
   - Export data regularly for backup

3. **Privacy compliance**
   - Follow institutional data policies
   - Consider anonymization for sensitive topics
   - Use secure networks when possible

## Troubleshooting

### Common Issues

#### "Session not found" error
**Cause**: Trying to access a session you don't own  
**Solution**: Check URL, verify session ID, contact session owner  

#### Session stuck in "Executing" status
**Cause**: Long-running search or system issue  
**Solution**: Wait 30+ minutes, check system status, contact support  

#### Can't edit session title
**Cause**: Session has progressed beyond "Strategy Ready" status  
**Solution**: This is by design for data integrity - create new session if needed  

#### Real-time updates not working
**Cause**: JavaScript disabled or network connectivity issues  
**Solution**: Enable JavaScript, check internet connection, refresh page  

#### Export download fails
**Cause**: Large dataset or temporary server issue  
**Solution**: Try again in a few minutes, contact support for large exports  

### Error Recovery

#### Failed Sessions
1. **View error details**: Click on failed session
2. **Check suggested solutions**: Review recovery options
3. **Try automatic recovery**: Use "Retry" button if available
4. **Reset if needed**: Return to previous working status
5. **Contact support**: If recovery options don't work

#### Data Recovery
1. **Check activity timeline**: See what actions were completed
2. **Export available data**: Download partial results if possible
3. **Review backups**: Check for exported data
4. **Restart process**: Create new session if necessary

### Getting Help

#### Self-Service Resources
1. **This user guide**: Comprehensive how-to information
2. **Activity timeline**: Shows exactly what happened
3. **Error messages**: Often include specific recovery steps
4. **System status page**: Check for known issues

#### Contact Support
**When to contact**:
- Errors persist after following recovery steps
- Data appears to be lost or corrupted
- System performance is significantly degraded
- Security concerns or suspicious activity

**Information to provide**:
- Session ID(s) affected
- Exact error messages
- Steps you were taking when error occurred
- Screenshots if helpful
- Your username and contact information

## Keyboard Shortcuts

### Navigation
- `Ctrl/Cmd + Home`: Return to dashboard
- `Ctrl/Cmd + N`: Create new session
- `Ctrl/Cmd + F`: Focus search box
- `Escape`: Close modals/popups

### Dashboard
- `Arrow Keys`: Navigate session cards
- `Enter`: Open selected session
- `Delete`: Delete selected session (if draft)
- `Ctrl/Cmd + D`: Duplicate selected session

### Session Detail
- `Ctrl/Cmd + E`: Edit session (if allowed)
- `Ctrl/Cmd + A`: View activity timeline
- `Ctrl/Cmd + S`: View status history
- `Ctrl/Cmd + X`: Export session data

### Accessibility
- `Tab`: Navigate interactive elements
- `Shift + Tab`: Navigate backwards
- `Space`: Activate buttons
- `Enter`: Submit forms

## Frequently Asked Questions

**Q: How many sessions can I create?**
A: Default limit is 100 active sessions per user. Archived sessions don't count toward this limit.

**Q: Can I change the session workflow?**
A: No, the 9-stage workflow is designed for PRISMA compliance and cannot be customized.

**Q: What happens if I close my browser during execution?**
A: Searches continue running in the background. You can return anytime to check progress.

**Q: Can I restore a deleted session?**
A: No, deletion is permanent. Only draft sessions can be deleted, so important work is protected.

**Q: How long are sessions retained?**
A: Active and completed sessions are retained indefinitely. Archived sessions are kept for 7 years minimum.

**Q: Can I share sessions with colleagues?**
A: Not in Phase 1. Team collaboration features are planned for Phase 2.

**Q: What browsers are supported?**
A: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+. Internet Explorer is not supported.

**Q: Is my data backed up?**
A: Yes, all data is automatically backed up. Export your data regularly for additional security.

---

**User Guide Version:** 1.0.0  
**Last Updated:** 2025-05-30  
**Support Contact:** [Your support contact information]  
**Status:** ✅ Complete