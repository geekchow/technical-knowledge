---
Source-AI: ChatGPT
Category: Technical
Time-Context: Coding Session
Topics: [CloudKit, SwiftData, iOS Development, iCloud, Schema Management]
tags:
  - ai-distilled
---

# CloudKit Schema Deploy UI

## Summary
Phil couldn't find the "Deploy Schema to Production" button in CloudKit Console while setting up CloudKit sync for 会意典. The button has moved in the current UI — deploy now lives under Schema → History, not Schema → Record Types.  iCloud Developer Console https://icloud.developer.apple.com/ 

## Key Takeaway
Apple relocated the CloudKit deployment action: it is no longer a button on the Record Types page. In the current CloudKit Console, deploy lives at **Schema → History → Deploy to Production** (framed as promoting a schema version, not a direct one-shot action).

## Key Insights
- The deploy button only appears in the **Development** environment — switching to Production hides it entirely.
- SwiftData + CloudKit schema is **lazy-created and device-triggered**: schema is only generated after running on a real device (not simulator) with iCloud signed in. If `CD_*` record types are absent from the dashboard, the issue is runtime, not dashboard navigation.
- CloudKit Console only shows a deployable diff when Development ≠ Production. If both match (or schema was never created), no deploy option appears.
- SwiftData uses the **Private Database** — ensure the sidebar is scoped to Private Database → Schema, not Public or Shared.
- If History shows nothing despite schema existing in Development, a workaround is to make a small model change, re-run on device, and refresh the Console.

## Action Items
- [ ] Deploy schema via Schema → History → Deploy to Production for `iCloud.geekchow.aipowerdict`

## Technical Details

### CloudKit Console Deploy — Correct Navigation (current UI)

```
Schema → History → "Deploy to Production" / "Promote Changes"
```

**NOT:** Schema → Record Types (old location — button no longer there)

### Fast Diagnostic Checklist (if deploy button is missing)

| Check | Pass condition |
|---|---|
| Real device run completed | App launched on iPhone, not simulator |
| iCloud logged in on device | Signed in with Apple ID |
| Correct container | `iCloud.geekchow.aipowerdict` |
| Environment selector | Set to **Development** |
| Database scope | **Private Database** → Schema |
| Schema populated | `CD_*` types visible in Record Types |

### SwiftData Schema Init Requirements

SwiftData + CloudKit only creates the `CD_*` record types when **all** of the following are true:
- Running on a **real device** (not simulator)
- iCloud account signed in
- CloudKit entitlement enabled
- Container identifier matches exactly

If `CD_*` types are absent → problem is in runtime init, not the dashboard.

---

## Related Questions
- What is the safe schema evolution strategy to avoid breaking existing Production users after the initial deploy?
- When does SwiftData require a re-deploy vs. handling schema changes transparently at runtime?

## Related Topics
CloudKit Schema Management
SwiftData CloudKit Integration
iCloud Private Database
iOS App Schema Migration
CloudKit Console Navigation
