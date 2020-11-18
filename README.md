# Punjar Bot: Taxing Party Members for Making Bad Jokes

The goal of this bot is to make it possible for any server member to track their pun usage. Ideally, a user will only need to send the message `!punjar deposit`, or perhaps even just `!pd`, to return something like:
```
Hshipper made a bad joke! They've put $16 in the pun jar.
```
Members should also be able to see how many puns others have made. `!punjar {member}` should produce a message like
```
{member} has made 25 cringe-inducing 'jokes' since we started keeping track.
```

Additional features may include a leaderboard, date sorting, and potentially even quotes.

The current plan is to host the bot using GCP Free Tier services:
- 1 f1-micro VM on Compute Engine
- 1 GB free document storage in Firebase
