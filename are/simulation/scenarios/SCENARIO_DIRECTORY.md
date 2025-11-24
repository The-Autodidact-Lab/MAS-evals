# SCENARIOS
## Single-step, single-turn
x12
### 1. Basic read tool call from one app
Held in `CUSTOM_scenario_ss1` -- looks for a specific phone number within a user DB (`/are/simulation/apps/db.py`)

### 2. Basic write tool call from one app
Held in `CUSTOM_scenario_ss2` -- looks to update a specific user's phone number within a user DB (`/are/simulation/apps/db.py`)

### 3. Read contact by name
Held in `CUSTOM_scenario_ss3` -- searches for a contact by name within a contacts app (`/are/simulation/apps/contacts.py`)

### 4. Read email by ID
Held in `CUSTOM_scenario_ss4` -- retrieves email content by email ID within an email client app (`/are/simulation/apps/email_client.py`)

### 5. Read calendar event by ID
Held in `CUSTOM_scenario_ss5` -- retrieves calendar event details by event ID within a calendar app (`/are/simulation/apps/calendar.py`)

### 6. Read conversation messages
Held in `CUSTOM_scenario_ss6` -- reads conversation messages by conversation ID within a messaging app (`/are/simulation/apps/messaging_v2.py`)

### 7. Read order details
Held in `CUSTOM_scenario_ss7` -- retrieves order details by order ID within a shopping app (`/are/simulation/apps/shopping.py`)

### 8. Update contact email
Held in `CUSTOM_scenario_ss8` -- updates a contact's email address within a contacts app (`/are/simulation/apps/contacts.py`)

### 9. Send email
Held in `CUSTOM_scenario_ss9` -- sends an email to recipients within an email client app (`/are/simulation/apps/email_client.py`)

### 10. Add calendar event
Held in `CUSTOM_scenario_ss10` -- creates a new calendar event within a calendar app (`/are/simulation/apps/calendar.py`)

### 11. Send message
Held in `CUSTOM_scenario_ss11` -- sends a message to a user within a messaging app (`/are/simulation/apps/messaging_v2.py`)

### 12. Add item to cart
Held in `CUSTOM_scenario_ss12` -- adds an item to shopping cart within a shopping app (`/are/simulation/apps/shopping.py`)

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

