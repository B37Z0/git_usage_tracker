from git_usage_tracking.git_usage_email import MAIL_MSG
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from string import Template
import requests
import schedule
import argparse
import json
import time
import util

# Config
recipients = []
# recipients.append('')

usage_endpoint = ...
db_endpoint = ...

# If script is not refreshed, token must be refreshed ***
TOKEN = ...

# Consider passing these as parameters / encapsulatin in a class ***
HEAD = {'Authorization': 'Bearer {}'.format(TOKEN)}
ORG_LIST = {...}
FILE_PATH = r'git_usage_tracking/git_usage_tracking.json' # use os.path for relative path ***

def get_args():
    '''
    Parse and return the arguments from the command line.
    '''
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='org')
    
    # Track and send email updates for a single org, or...
    single = subparsers.add_parser('single', help='track single orgid + 1 positional argument [orgid]')
    single.add_argument('orgid', help='single orgid (0 for total git usage)')

    # ...track all orgs and optionally send email updates for a single org
    all = subparsers.add_parser('all', help='track all orgids + 1 optional argument [--orgid]')
    all.add_argument('-o', '--orgid', help='optional single orgid for email updates')
    
    return parser.parse_args()


def request(session, endpoint):
    '''
    Given an open session, request a response from the endpoint.
    Return relevant data from the response.
    '''
    try:
        response = session.get(endpoint, headers=HEAD)
        response.raise_for_status()
        return response.json()[0], response.status_code
    except requests.exceptions.HTTPError as error:
        print(error)
        return (None, response.status_code)
    except Exception as error:
        print(error)
        return (None, None)

def log_endpoint(session, endpoint, local=False):
    '''
    Accept data from a request and verify it exists.
    If it exists, either store the data in the database, 
    or return the data for local storage.
    '''
    data, status = request(session, endpoint)
    if data is None:
        print(f"Failed to get data from endpoint: {endpoint} (status: {status})")
        return None

    # Replace any {None} usage values because the db_endpoint doesn't accept them.
    if not data['git_public_usage']:
        data['git_public_usage'] = '0'
    if not data['git_private_usage']:
        data['git_private_usage'] = '0'
    if not data['git_total_usage']:
        data['git_total_usage'] = '0'
    # Add org_id = 0 for total usage
    if not data.get('org_id'):
        data['org_id'] = 0

    if status == 200:   
        snapshot = {
            'org_id': data['org_id'],
            'git_public_usage': data['git_public_usage'],
            'git_private_usage': data['git_private_usage'],
            'git_total_usage': data['git_total_usage'],
            'git_scale': 'GB'
        }
        print(snapshot) # DEBUGGING

        if not local:
            response = session.post(db_endpoint, json=snapshot, headers=HEAD)

            if response.status_code == 200:
                print(f'Saved at {data['timestamp']} for orgid={data['org_id']}:  {data['git_total_usage']} GB') # DEBUGGING
            else:
                print(f'Failed to save at {data['timestamp']} for orgid={data['org_id']}.')
                print(response.json())
        else:
            snapshot['timestamp'] = data['timestamp']
            return snapshot
    else:
        print('Get request failed. Status code: {}'.format(status))     

def update_tracked(session, update=True):
    '''
    Update local usage values and return a list with organids that have had usage changes.
    Only total git usage is used to determine if a usage change has occured.
    A switch (update) has been added for debugging purposes.
    '''
    changed = []
    try:
        with open(FILE_PATH) as file:
            entries = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(error)
        return changed

    for orgid in ORG_LIST:
        endpoint = usage_endpoint + orgid
        new_entry = log_endpoint(session, endpoint, local=True)
        if not new_entry:
            print(f'No data returned for orgid={orgid}. Skipping.')
            continue
    
        if entries[orgid][1]["git_total_usage"] != new_entry["git_total_usage"]:
            changed.append(orgid)
        
        if update: # DEBUGGING
            entries[orgid] = [entries[orgid][1], new_entry]

    try:
        with open(FILE_PATH, 'w') as file:
            json.dump(entries, file, indent=4)
    except Exception as error:
        print(error)

    return changed    


def sendMail(email_message):
    template_msg = Template(MAIL_MSG)
    d = {
        'org': email_message['org'],
        'usage_i': email_message['usage_i'],
        'usage_i_time': email_message['usage_i_time'],
        'usage_f': email_message['usage_f'],
        'usage_f_time': email_message['usage_f_time'],
        'public_usage': email_message['public_usage'],
        'public_usage_x': email_message['public_usage_x'],
        'private_usage': email_message['private_usage'],
        'private_usage_x': email_message['private_usage_x'],
        'usage_change': email_message['usage_change'],
        'usage_change_x': email_message['usage_change_x']
    }
    msg = template_msg.substitute(d)
    message = MIMEText(msg, 'html', 'utf-8')

    message['From'] = ...
    message['To'] = ', '.join(recipients)

    subject = 'REPORT : Git Usage'
    message['Subject'] = Header(subject, 'utf-8')
    msg_str = message.as_string()
    if util.send_mail(recipients,msg_str): # returns None on success
        print('Email sending failed.')

def email_task(session, orgid):
    '''
    Log endpoint to stay up to date.
    Update tracked values with the usage from the previous and current day.
    Fill in an email template and send it to the listed emails.
    '''
    if orgid in update_tracked(session, update=False): # update=True outside of testing ***
        try:
            with open(FILE_PATH) as file:
                entries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as error:
            print(error)
            return

        org_name = ORG_LIST[orgid]
        usage_i = entries[orgid][0]['git_total_usage']
        usage_i_time = datetime.fromisoformat(entries[orgid][0]['timestamp']).strftime('%Y-%m-%d %H:%M [UTC]')
        usage_f = entries[orgid][1]['git_total_usage']
        usage_f_time = datetime.fromisoformat(entries[orgid][1]['timestamp']).strftime('%Y-%m-%d %H:%M [UTC]')
        public_usage = entries[orgid][1]['git_public_usage']
        private_usage = entries[orgid][1]['git_private_usage']
        public_usage_x = str(round(((float(public_usage)/float(usage_f))*100), 2))
        private_usage_x = str(round(((float(private_usage)/float(usage_f))*100), 2))
        usage_change = str(float(usage_f)-float(usage_i))
        usage_change_x = str((float(usage_change)/float(usage_i))*100)

        sendMail(
            {
                'org': org_name,
                'usage_i': usage_i,
                'usage_i_time': usage_i_time,
                'usage_f': usage_f,
                'usage_f_time': usage_f_time,
                'public_usage': public_usage,
                'public_usage_x': public_usage_x,
                'private_usage': private_usage,
                'private_usage_x': private_usage_x,
                'usage_change': usage_change,
                'usage_change_x': usage_change_x
            }
        )
    else:
        print('No usage change was detected for orgid={}. No email update sent.'.format(orgid))


def log(session, org_list):
    '''
    Intermediary function to track usage for a list of a single or all organizations.
    '''
    for orgid in org_list:
        endpoint = usage_endpoint + orgid
        log_endpoint(session, endpoint)

def email(session, yes, orgid):
    '''
    Intermediary function to create/send an email update for a single organization.
    '''
    if yes:
        email_task(session, orgid)
    else:
        print('Email updates not enabled. No email update sent.')


def main(org_list, update=True, e_orgid=None):
    if not set(org_list).issubset(ORG_LIST):
        print('Invalid orgid(s) provided.')
        return

    print('Starting session. [CTRL+C] to end.')
    s = requests.Session()

    schedule.every(15).minutes.do(log, session=s, org_list=org_list)
    schedule.every().day.at('08:00').do(email, session=s, yes=update, orgid=e_orgid) # system time

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        log(s, org_list)
        print('Program ended.')


if __name__ == '__main__':
    print(get_args())

    args = get_args()
    if args.org == 'single':
        print('Organization ID: ' + args.orgid)
        main([args.orgid], e_orgid=args.orgid)
    elif args.org == 'all':
        print('Tracking all organizations.')
        if args.orgid:
            main(ORG_LIST, e_orgid=args.orgid)
        else:
            main(ORG_LIST, update=False)