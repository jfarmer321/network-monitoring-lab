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
3. Try `python3 triage.py --grant-minutes 1`. Robin's admin grant came 101 seconds after sign-in, so the stricter window removes the escalation but leaves the login alert. I wouldn't close the case just because the rule no longer matches: the missing approval still needs checking.

These time windows are practice settings, not universal rules. The script handles only these event types and cannot establish who controlled an account. An expected action can still trip a rule, and a real incident can fall outside it.

## Optional home lab extension

Keep the first live version on a device or VM you own. Export just sign-in and account-change event metadata from a test account, then map the fields to the sample CSV. Don't capture household traffic or collect passwords, cookies, packet contents, or other users' activity. Keep live exports private; publish only the synthetic fixtures, code, and your sanitized write-up.

## What I’d check next

The project only compares logins and grants when the account and source match. A real grant can be performed by another account or system, so I’d want the actor and affected account as separate fields before using this rule on real exports. The script also can’t tell whether a ticket really matches the event. That’s still an analyst’s job.
