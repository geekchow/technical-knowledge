# Cron

The `--schedule="*/5 * * * *"` follows standard **Unix cron syntax** with 5 fields:

```
*/5  *  *  *  *
 │   │  │  │  └── Day of week  (0-7, Sun=0 or 7)
 │   │  │  └───── Month        (1-12)
 │   │  └──────── Day of month (1-31)
 │   └─────────── Hour         (0-23)
 └─────────────── Minute       (0-59)
```

So `*/5 * * * *` means **"every 5 minutes, every hour, every day"**.

The `*/5` uses the **step operator** `/` — meaning "every Nth unit within the full range". It's equivalent to `0,5,10,15,20,25,30,35,40,45,50,55`.

A few more examples for comparison:

| Expression | Meaning |
|---|---|
| `*/5 * * * *` | Every 5 minutes |
| `0 9 * * 1-5` | 9:00 AM, Mon–Fri |
| `0 0 1 * *` | Midnight on the 1st of every month |
| `30 8 * * 1` | 8:30 AM every Monday |

> **Note:** Kubernetes CronJob also supports a `@` shorthand like `@hourly`, `@daily`, `@weekly` — but those aren't usable via `--schedule` in `kubectl` directly.