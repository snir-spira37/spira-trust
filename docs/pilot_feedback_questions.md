# Pilot Feedback Questions

Use these questions after a reviewer runs SPIRA Trust on a real wheel or local
wheelhouse.

## Core Questions

```text
1. Did SPIRA change a decision you would have made?
2. Did it reduce uncertainty before installation?
3. Was the terminal verdict enough, or did you need the JSON?
4. Which finding was useful?
5. Which finding was noisy, confusing, or irrelevant?
```

## Workflow Questions

```text
1. Would you run `spira-trust trust` manually before installing an unknown wheel?
2. Would you run `spira-trust graph` in CI against a wheelhouse?
3. Would baseline drift be useful for your team?
4. Which output would you preserve as evidence?
5. What would stop you from using this weekly?
```

## Boundary Questions

```text
1. Did you expect CVE or malware detection?
2. Was it clear that SPIRA does not resolve or download dependencies?
3. Was it clear that SPIRA does not execute package code?
4. Was `TRUST_OK_WITH_NOTES` understandable?
5. Did the not-claimed boundaries increase or reduce trust?
```

## Final Prompt

Ask:

```text
If you could change one thing before using SPIRA Trust again, what would it be?
```
