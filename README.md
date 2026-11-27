# Network Monitoring and Alert Triage Lab

I was curious how a security analyst tells a bad login from someone just forgetting their password. I started with two accounts that look about the same at first. I wanted to see which extra piece of evidence would make me treat them differently. All events and tickets are synthetic and all IPs are documentation addresses. The script reads a local CSV; it does not monitor or contact any network.

## Run it yourself

Requires Python 3.9+ and no extra packages. From the extracted folder:

```sh
python3 triage.py
python3 -m unittest -v
```

1. Run the script. It flags three or more failures followed by success within five minutes for the same account and source. A later admin grant within ten minutes raises the priority.
2. Read `data/events.csv` and use `data/context.csv` to decide what to close and what to escalate. Write down the timestamp that changed your mind in each case before checking `review-guide.md`.
3. Run both commands below on the same sample file. Only the time allowed between sign-in and the admin grant changes.

## What changed when I shortened the window?

I wanted to know whether the shorter window would hide the whole alert or just stop it from being escalated. Here are both terminal runs:

**10 minutes (default):**

```text
$ python3 triage.py --grant-minutes 10
Review login | casey | 192.0.2.14 | 3 failed attempts before success at 2026-11-25T18:01:40+00:00
Escalate for verification | robin | 198.51.100.8 | 3 failed attempts before success at 2026-11-25T19:41:41+00:00
  Admin grant followed at 2026-11-25T19:43:22+00:00
```

**1 minute:**

```text
$ python3 triage.py --grant-minutes 1
Review login | casey | 192.0.2.14 | 3 failed attempts before success at 2026-11-25T18:01:40+00:00
Review login | robin | 198.51.100.8 | 3 failed attempts before success at 2026-11-25T19:41:41+00:00
```

Robin's admin grant came 1 minute 41 seconds after sign-in. With the 10-minute window, the script connects the two events and escalates the alert. With the 1-minute window, the login still gets flagged, but the grant is too late to raise its priority. Casey's alert stays the same in both runs.

I wouldn't close Robin's case just because the second run didn't escalate it. The change calendar still has no matching approval. Casey's support ticket, on the other hand, explains the failed attempts.

These time windows are practice settings, not universal rules. The script handles only these event types and cannot establish who controlled an account. An expected action can still trip a rule, and a real incident can fall outside it.

## Optional home lab extension

Keep the first live version on a device or VM you own. Export just sign-in and account-change event metadata from a test account, then map the fields to the sample CSV. Don't capture household traffic or collect passwords, cookies, packet contents, or other users' activity. Keep live exports private; publish only the synthetic fixtures, code, and your sanitized write-up.

## What I’d check next

The project only compares logins and grants when the account and source match. A real grant can be performed by another account or system, so I’d want the actor and affected account as separate fields before using this rule on real exports. The script also can’t tell whether a ticket really matches the event. That’s still an analyst’s job.
