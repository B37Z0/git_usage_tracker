# Git Usage Tracking

Script to track Git storage usage for one or more organizations. Periodically fetches usage data from a usage endpoint, stores snapshots in a database, and optionally sends email alerts when usage changes.
Intended to be run as a scheduled service; uses local JSON file to keep a temporary record of previous usage snapshots for comparison.
Added code is nonfunctional and intended for display purposes only.

## Features
- Poll Git usage for >= 1 organizations at regular intervals
- Store usage snapshots in a remote database endpoint
- Track day-to-day changes in usage
- Generate and send email reports when usage changes
- CLI for tracking a single org or all orgs

## Command Line Usage
Track single org + email updates:
`python script.py single <orgid>`

Track all orgs:
`python script.py all`

Track all orgs + enable email updates for one:
`python script.py all --orgid <orgid>`
