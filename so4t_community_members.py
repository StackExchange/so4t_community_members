import argparse
import csv
import time

from so4t_api_v3 import V3Client


def get_args():

    parser = argparse.ArgumentParser(
        prog='so4t_community_members.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Uses the Stack Internal API to export a CSV of community members '
                    'with email addresses.',
        epilog='Example for Stack Internal (Business): \n'
               'python3 so4t_community_members.py --url '
               '"https://stackoverflowteams.com/c/TEAM-NAME" '
               '--token "YOUR_TOKEN" --community-name "My Community" \n\n'
               'Example for Stack Internal (Enterprise): \n'
               'python3 so4t_community_members.py --url '
               '"https://SUBDOMAIN.stackenterprise.co" '
               '--token "YOUR_TOKEN" --community-name "My Community"\n\n')

    parser.add_argument('--url',
                        type=str,
                        required=True,
                        help='[REQUIRED] Base URL for your Stack Internal instance.')
    parser.add_argument('--token',
                        type=str,
                        required=True,
                        help='[REQUIRED] API access token for your Stack Internal instance.')
    parser.add_argument('--community-name',
                        type=str,
                        nargs='+',
                        help='Name(s) of the community to export members from. '
                        'Separate multiple names with commas. '
                        'If not provided, lists all available communities.')
    parser.add_argument('--community-id',
                        type=int,
                        nargs='+',
                        help='ID(s) of the community to export members from. '
                        'Use instead of --community-name if you know the IDs.')
    parser.add_argument('--all',
                        action='store_true',
                        help='Export members from all communities.')

    return parser.parse_args()


def main():

    args = get_args()
    v3client = V3Client(args.url, args.token)

    # Get all communities
    print("Fetching communities...")
    communities = v3client.get_all_communities()

    if not communities:
        print("No communities found on this instance. "
              "Communities may not be enabled for your plan.")
        raise SystemExit

    # If no community specified, list available communities and exit
    if not args.community_name and not args.community_id and not args.all:
        print(f"\nFound {len(communities)} communities:\n")
        for c in communities:
            print(f"  ID: {c['id']}  |  Name: {c['name']}  |  Members: {c['memberCount']}")
        print("\nRe-run with --community-name, --community-id, or --all to export members.")
        raise SystemExit

    # Resolve which community IDs to export
    target_ids = []

    if args.all:
        target_ids = [c['id'] for c in communities]
        print(f"Exporting all {len(target_ids)} communities...")

    elif args.community_id:
        target_ids = args.community_id

    elif args.community_name:
        # Join and re-split on commas to handle both "A, B" and "A" "B"
        raw_names = ' '.join(args.community_name)
        names = [n.strip() for n in raw_names.split(',') if n.strip()]
        for name in names:
            match = [c for c in communities
                     if c['name'].lower() == name.lower()]
            if not match:
                print(f"Community '{name}' not found. Available communities:")
                for c in communities:
                    print(f"  ID: {c['id']}  |  Name: {c['name']}")
                raise SystemExit
            target_ids.append(match[0]['id'])

    # Get all users once for email lookup
    print("Fetching users (for email lookup)...")
    users = v3client.get_all_users()
    user_lookup = {u['id']: u for u in users}

    # Process each community
    for community_id in target_ids:
        print(f"\nFetching community (ID: {community_id})...")
        community = v3client.get_community(community_id)
        members = community.get('members', [])
        community_name = community['name']

        if not members:
            print(f"Community '{community_name}' has no members. Skipping.")
            continue

        print(f"Found {len(members)} members in '{community_name}'")

        # Build report rows
        report = []
        for member in members:
            user = user_lookup.get(member['id'], {})
            report.append({
                'Name': member.get('name', ''),
                'Email': user.get('email', ''),
                'Member Since': member.get('memberSince', ''),
                'Is SME': member.get('isSme', False),
                'Job Title': user.get('jobTitle', ''),
                'Department': user.get('department', ''),
            })

        # Sort by name
        report.sort(key=lambda r: r['Name'].lower())

        # Print to console
        print(f"\n{'Name':<25} {'Email':<35} {'Member Since':<22} {'SME':<6} {'Job Title'}")
        print("-" * 110)
        for row in report:
            since = row['Member Since'][:10] if row['Member Since'] else ''
            title = row['Job Title'] or ''
            print(f"{row['Name']:<25} {row['Email']:<35} {since:<22} "
                  f"{str(row['Is SME']):<6} {title}")

        # Export to CSV
        safe_name = community_name.replace(' ', '_').replace('/', '_')
        date = time.strftime("%Y-%m-%d")
        file_name = f"{date}_community_members_{safe_name}.csv"

        with open(file_name, 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=report[0].keys())
            writer.writeheader()
            writer.writerows(report)

        print(f"\nCSV file created: {file_name}")
        print(f"Exported {len(report)} members from '{community_name}'")


if __name__ == '__main__':
    main()
