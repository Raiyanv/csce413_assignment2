# Honeypot Analysis

## Summary of Observed Attacks
- 20+ SSH connections were logged
- Attackers targeted the root and user accounts
- Network traffic came in bursts seeming to imply that it was an automated tooling


## Notable Patterns
- SSH on port 22
- SSH is a high value target and consistent with real-world scenarios
- Attempted the default credentials
- No lateral movement detected
- No brute forcing
## Recommendations
- Disable root SSH login (if not already)
- Enforce key based auth
- Implement rate limiting
- Alert on multiple failed attempts
