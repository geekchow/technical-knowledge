---
title: "CloudKit multi-device synchronization"
author:
published:
created: 2026-04-16
description: "Claude conversation with 3 messages"
tags:
  - "clippings"
---

# CloudKit multi-device synchronization

**You**

how does cloudkit works, what's the typical usage case, and especially for multiple devices sync

---

**Claude**

## CloudKit — How It Works & Multi-Device Sync

## The Core Architecture

CloudKit is Apple's backend-as-a-service framework that lets apps store data in iCloud and sync it across devices. It's essentially a structured database hosted by Apple, with no server-side code required from you.

**Three database types per app container:**

| Database | Who can read/write | Use case |
| --- | --- | --- |
| **Private** | Only the signed-in iCloud user | Personal user data |
| **Public** | Anyone (write requires auth) | Shared/community content |
| **Shared** | A specific set of participants | Collaborative features |

For a dictionary/vocabulary app like yours, **Private Database** is almost always the right choice — each user's word book, flashcard progress, and settings live in their own private iCloud container.

---

## Key Concepts

**Container** → your app's top-level iCloud namespace (`iCloud.com.yourcompany.appname`)

**Record Zone** → a partition inside a database. The default zone exists automatically; custom zones are required for change tracking and sync.

**Record** → a single data object, like a CoreData entity. Has a `recordType` (like a table name) and key-value fields.

**CKRecord** → the Swift class representing a record. Fields can be `String`, `Int`, `Double`, `Date`, `Data`, `CKAsset` (binary files), and `CKRecord.Reference` (foreign keys).

---

## Two APIs to Know

### 1\. CloudKit API (manual)

You manage saves and fetches yourself via `CKContainer`, `CKDatabase`, `CKQuery`.

```swift
let record = CKRecord(recordType: "WordBookEntry")
record["word"] = "ephemeral"
record["addedAt"] = Date()

CKContainer.default().privateCloudDatabase.save(record) { record, error in
    // handle result
}
```

### 2\. NSPersistentCloudKitContainer (recommended)

If you already use **Core Data**, this is a drop-in replacement for `NSPersistentContainer`. It automatically mirrors your Core Data store to CloudKit with **zero manual sync code**.

```swift
// Just change one word in your Core Data stack:
let container = NSPersistentCloudKitContainer(name: "AIPowerDict")
// That's it — sync is automatic
```

---

## Multi-Device Sync — How It Actually Works

This is the most important part. CloudKit uses a **push + pull** model with **change tokens**.

### The Sync Flow

```
Device A saves a record
        ↓
CloudKit stores it + increments server change token
        ↓
Apple Push Notification (silent) sent to Device B
        ↓
Device B wakes, fetches changes since its last token
        ↓
Device B applies changes locally
        ↓
Device B saves the new change token
```

### Change Tokens (CKServerChangeToken)

- A token represents "everything up to this point"
- On first launch: fetch everything, save the token
- On subsequent syncs: fetch only **what changed since the token**
- This makes incremental sync efficient — no full re-downloads

### CKFetchRecordZoneChangesOperation

The workhorse for sync:

```swift
let config = CKFetchRecordZoneChangesOperation.ZoneConfiguration()
config.previousServerChangeToken = savedToken  // nil on first sync

let op = CKFetchRecordZoneChangesOperation(
    recordZoneIDs: [zoneID],
    configurationsByRecordZoneID: [zoneID: config]
)

op.recordWasChangedBlock = { recordID, result in
    // apply new/updated record locally
}
op.recordWithIDWasDeletedBlock = { recordID, recordType in
    // delete locally
}
op.recordZoneChangeTokensUpdatedBlock = { zoneID, newToken, _ in
    // SAVE this token to UserDefaults or Core Data
    saveToken(newToken)
}
```

### Conflict Resolution

When two devices edit the same record offline and then sync:

- CloudKit uses **last-write-wins** by default
- You can implement custom merge logic using `CKRecord` 's `modificationDate`
- For `NSPersistentCloudKitContainer`, Apple handles this automatically

---

## Typical Usage Patterns for a Vocab App

| Feature | CloudKit Approach |
| --- | --- |
| Word book entries | `CKRecord` per entry in Private DB, custom zone |
| SM-2 flashcard state | Fields on the same record (`nextReview`, `easeFactor`, `interval`) |
| Settings / preferences | Single `CKRecord` of type `UserSettings` |
| Streak data | Field on UserSettings record |
| Offline support | Cache locally (Core Data / SwiftData), sync when online |

---

## Setup Checklist

1. **Enable iCloud capability** in Xcode → Signing & Capabilities → iCloud → check CloudKit
2. **Add container** (`iCloud.com.yourcompany.aidict` or similar)
3. Use `NSPersistentCloudKitContainer` if you have Core Data, otherwise use `CKDatabase` directly
4. **Custom zone** is required for change tracking (default zone doesn't support `CKFetchRecordZoneChangesOperation`)
5. **Subscribe to push notifications** so devices wake up when remote changes arrive — `CKDatabaseSubscription` handles this

---

## NSPersistentCloudKitContainer vs Manual CloudKit

|  | `NSPersistentCloudKitContainer` | Manual CloudKit |
| --- | --- | --- |
| Setup effort | Minimal (one line change) | Significant |
| Conflict handling | Automatic | Manual |
| Offline support | Built-in | You build it |
| Query flexibility | Limited (CoreData predicates) | Full CKQuery |
| Best for | Existing CoreData apps | Custom sync logic |

**For 会意典**, if you're using Core Data already, `NSPersistentCloudKitContainer` is by far the fastest path to iCloud sync — word book, flashcard progress, and settings would all sync across devices automatically with almost no additional code.

---

**Claude**

mobile application development
