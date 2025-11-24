# Multi-App Information Gathering Scenario (ms1)

This scenario evaluates an agent's ability to gather information across multiple applications, compare data across different sources, and reason before drawing a conclusion. The agent must read from 5 different applications while avoiding 3 distractor applications that are not relevant to the task.

## Task Overview

The agent is asked to determine if **Sarah Johnson** is available for a meeting next Tuesday afternoon (around 2 PM). To complete this task, the agent must:

1. **Read from ContactsApp**: Find Sarah Johnson's contact information
2. **Read from CalendarApp**: Check her calendar for next Tuesday afternoon events
3. **Read from EmailClientApp**: Review relevant emails about meetings
4. **Read from MessagingApp**: Check recent messages with Sarah
5. **Read from DBApp**: Look up any relevant database entries

After gathering information from all sources, the agent must:
- Compare the data across different apps
- Reason about any conflicts or availability
- Provide a comprehensive analysis

## Applications

### Relevant Apps (Must be Queried)
1. **ContactsApp**: Contains Sarah Johnson's contact details (email, phone, job title)
2. **CalendarApp**: Contains calendar events showing Sarah has meetings scheduled next Tuesday afternoon
3. **EmailClientApp**: Contains emails about meeting requests and scheduling conflicts
4. **MessagingApp**: Contains recent chat messages discussing availability
5. **DBApp**: Contains additional database entries with context about Sarah

### Distractor Apps (Should NOT be Queried)
1. **ApartmentListingApp**: Contains apartment listings (not relevant to availability)
2. **CabApp**: Contains ride history (not relevant to availability)
3. **ReminderApp**: Contains personal reminders (not relevant to availability)

## Desired Workflow

The agent should follow this workflow:

1. **Initial Query**: Start by searching for "Sarah Johnson" in ContactsApp to get her contact ID and information
2. **Calendar Check**: Query CalendarApp for events on next Tuesday afternoon to see scheduled meetings
3. **Email Review**: Search EmailClientApp for emails from/to Sarah about meetings or scheduling
4. **Message History**: Check MessagingApp for recent conversations with Sarah about availability
5. **Database Lookup**: Query DBApp for any entries related to Sarah or meeting information
6. **Cross-App Comparison**: Compare information from all sources:
   - Calendar shows meetings at 2 PM and 3:30 PM
   - Email mentions a conflict and rescheduling request
   - Messages indicate uncertainty about availability
   - Database provides additional context
7. **Reasoning**: Synthesize findings:
   - Sarah has back-to-back meetings (Team Standup 2-3 PM, Project Review 3:30-4 PM)
   - Email and messages suggest she's aware of a conflict
   - Conclusion: Sarah is NOT available for a 2 PM meeting next Tuesday
8. **Final Answer**: Provide a comprehensive analysis explaining the availability status with evidence from all sources

## Validation

The scenario validates that:
- ✅ All 5 relevant apps were accessed (contacts, calendar, email, messaging, db)
- ✅ None of the 3 distractor apps were accessed (apartments, cab, reminders)
- ✅ The correct database entry was queried
- ✅ The agent performed cross-app information gathering and reasoning

## Usage

To run the scenario:
```bash
python -m are.simulation.scenarios.CUSTOM_scenario_ms1.scenario
```
