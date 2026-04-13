# so4t_community_members

Exports Stack Internal Community members to CSV, including email addresses. Requires Site Admin access.

## Setup

```bash
pip3 install -r requirements.txt
```

You'll need an API Access Token:
- **Enterprise**: Go to `https://SUBDOMAIN.stackenterprise.co/api/v3`, click Authorize, copy the Bearer token
- **Business**: Generate a PAT from your account settings

## Usage

```bash
# List all communities
python3 so4t_community_members.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN"

# Export one community
python3 so4t_community_members.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN" --community-name "My Community"

# Export multiple communities
python3 so4t_community_members.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN" --community-name "Community A, Community B"

# Export all communities
python3 so4t_community_members.py --url "https://SUBDOMAIN.stackenterprise.co" --token "YOUR_TOKEN" --all
```

You can also use `--community-id` instead of `--community-name`.

## Output

Generates a timestamped CSV per community (e.g. `2026-04-13_community_members_My_Community.csv`) with: Name, Email, Member Since, Is SME, Job Title, Department. Results are also printed to the console.
