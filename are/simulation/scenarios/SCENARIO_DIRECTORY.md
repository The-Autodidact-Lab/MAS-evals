# SCENARIOS
## Single-step, single-turn
x12
### 1. Basic read tool call from one app
Held in `CUSTOM_scenario_ss1` -- looks for a specific phone number within a user DB (`/are/simulation/apps/db.py`)

### 2. Basic write tool call from one app
Held in `CUSTOM_scenario_ss2` -- looks to update a specific user's phone number within a user DB (`/are/simulation/apps/db.py`)

### 3. Read contact by name
Held in `CUSTOM_scenario_ss3` -- searches for a contact by name within a contacts app (`/are/simulation/apps/contacts.py`)

### 4. Read order details (Low similarity, clear delegation)
Held in `CUSTOM_scenario_ss4` -- retrieves order details by order ID within a shopping app (`/are/simulation/apps/shopping.py`). All 7 apps present; ShoppingApp is distinct with no similar functions, making routing straightforward.

### 5. Read calendar event (Medium similarity, moderate delegation challenge)
Held in `CUSTOM_scenario_ss5` -- retrieves calendar event details by event ID within a calendar app (`/are/simulation/apps/calendar.py`). All 7 apps present; CalendarApp shares time-based concepts with ReminderApp, requiring clear prompt parsing.

### 6. Read contact (High similarity, challenging delegation)
Held in `CUSTOM_scenario_ss6` -- retrieves contact information by contact ID within a contacts app (`/are/simulation/apps/contacts.py`). All 7 apps present; ContactsApp and DBApp both have get_* functions for contact-like data, creating ambiguity.

### 7. Read database entry (High similarity, very challenging delegation)
Held in `CUSTOM_scenario_ss7` -- retrieves database entry by entry ID within a database app (`/are/simulation/apps/db.py`). All 7 apps present; DBApp and ContactsApp have similar data structures and overlapping get functions, requiring subtle prompt interpretation.

### 8. Update contact email
Held in `CUSTOM_scenario_ss8` -- updates a contact's email address within a contacts app (`/are/simulation/apps/contacts.py`)

### 9. Add reminder (Low similarity, clear delegation)
Held in `CUSTOM_scenario_ss9` -- adds a reminder within a reminder app (`/are/simulation/apps/reminder.py`). All 7 apps present; ReminderApp is functionally distinct with unique add_reminder function, making routing unambiguous.

### 10. Add calendar event (Medium similarity, moderate delegation challenge)
Held in `CUSTOM_scenario_ss10` -- creates a new calendar event within a calendar app (`/are/simulation/apps/calendar.py`). All 7 apps present; CalendarApp and ReminderApp both handle scheduling but with different event types and APIs.

### 11. Send email (High similarity, challenging delegation)
Held in `CUSTOM_scenario_ss11` -- sends an email to recipients within an email client app (`/are/simulation/apps/email_client.py`). All 7 apps present; EmailClientApp and MessagingAppV2 both handle communication with send_* functions, creating ambiguity.

### 12. Update contact (High similarity, very challenging delegation)
Held in `CUSTOM_scenario_ss12` -- updates a contact's email address within a contacts app (`/are/simulation/apps/contacts.py`). All 7 apps present; ContactsApp and DBApp both support update/edit operations on similar data structures, requiring careful prompt interpretation.

## Multi-step, single-turn
x5
### 1. Basic information gathering + QA workflow within a single app

### 2. Basic information gathering + 1 write workflow within a single app

### 3. Interleaved read-writes and reasoning within a single app

### 4. Information gathering + QA across multiple apps

### 5. Information gathering + write workflow across multiple apps

## Single-step each, multi-turn
x5
### variations on read-ask for confirmation/read-respond/write

## Multi-step each, multi-turn
x3

24 Nov -- NEXT:
- finalise all single-single scenarios (diversity + reasonably evaluate delegations)
- fine-tune first ms template
- create mm and sm templates
- scale up scenario generation with LLMs
- create benchmarks suite

