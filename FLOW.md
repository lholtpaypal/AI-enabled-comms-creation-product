# Push Notification Enrollment Workflow

**Layout:** Vertical, worked through step by step.

## 1. Declared Intent

The user starts with an intent box, e.g.:

> "Hey! I need to create a push notification to get eligible users to enroll in the PayPal Debit Card"

This declared intent kicks off the entire workflow. The model is called and returns the copy for the push notification.

## 2. Editable Copy

- The returned copy is displayed in a long, editable text box.
- Below the text box is a **"Regenerate copy text"** button.
  - On click, it reuses the declared intent, calls the model again, and returns a different set of copy in the box.
  - This behavior repeats each time the user presses **"Regenerate copy text"**.

## 3. Audience (RPS Search Agent)

Below the copy section, the RPS Search agent forms the API call and returns an audience, presented as two boxes:

- **RPS Segment ID box** — editable. Users can paste in their own Dynamic Segment ID.
- **RPS Details box** — shows all metrics from the RPS segment.

If a user pastes in another segment ID, the details automatically update accordingly.

## 4. Suggested Audience Options

- The user is also presented with the next **2 suggested dynamic audience options**, in case they'd prefer one of those instead.
- If a suggestion is clicked:
  - The **RPS Segment ID box** updates with the chosen segment's ID.
  - The **RPS Details box** updates accordingly.

## 5. Generate Content Variants for A/B Experimentation

- The user is presented with a button that says, 'Create content variations for A/B testing?' with a Yes or No button
- If the user clicks 'yes'; 2 additional variants are generated and presented.
    - The only thing that should be additionally generated is the Title and Body copy for the notification. 
- At this point in the flow, the user should see all three push notification mock-ups, the push notification only, not presented in the iPhone UI – just at the bottom, in 1 row.

---

**Make these changes.**