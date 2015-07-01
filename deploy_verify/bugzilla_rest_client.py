"""This module enables CRUD operations with Bugzilla 5.1 REST API

.. _Bugzilla REST API Docs:
   https://wiki.mozilla.org/Bugzilla:REST_API
   http://bugzilla.readthedocs.org/en/latest/api/index.html
"""

import sys
import json
import requests
from output_helper import OutputHelper

URL_BUGZILLA_PROD = 'https://bugzilla.mozilla.org'
URL_BUGZILLA_DEV = 'https://bugzilla-dev.allizom.org'
PRODUCT_PROD = 'Cloud Services'
PRODUCT_DEV = 'Mozilla Services'
COMPONENT_PROD = 'Operations: Deployment Requests'
COMPONENT_DEV = 'General'
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}


class InvalidCredentials(Exception):
    pass


class BugzillaRESTClient(object):
    """"Used for CRUD operations against Bugzilla REST API"""

    def __init__(self, host, bugzilla_username, bugzilla_password):

        self.output = OutputHelper()
        self.host = host
        self.username = bugzilla_username
        self.password = bugzilla_password
        self.token = self.get_token(host)

        # bugzilla-dev doesn't mirror the same components, 
        #so we'll populate these conditionally
        self.bugzilla_product = PRODUCT_DEV if 'dev' in host else PRODUCT_PROD
        self.bugzilla_component = COMPONENT_DEV if 'dev' in host else \
            COMPONENT_PROD

    def _get_json_create(self, release_num, application,
        environment, status, description, cc_mail=''):
        """Returns bugzilla JSON string to POST to REST API."""

        short_desc = '[deployment] {0} {1} - {2}'.format(
            application, release_num, environment)

        data = {
            'product': self.bugzilla_product,
            'component': self.bugzilla_component,
            'version': 'unspecified',
            'op_sys': 'All',
            'rep_platform': 'All',
            'short_desc': short_desc,
            'description': description, 
            'status': status
        }
        if cc_mail:
            data.update(
                {
                    'cc': [cc_mail]
                }
            )
        return data

    def _get_json_update(self, bug_id, comment):
        """Returns bugzilla JSON as string to PUT to REST API."""

        data = {
            'ids': [bug_id],
            'comment': comment
        }
        return data

    def _get_json_search(self, summary):
        """Returns bugzilla JSON as string to GET from REST API."""
        data = {
            'summary': summary,
            'product': self.bugzilla_product, 
            'component': self.bugzilla_component 
        }
        return data

    def get_token(self, host):
        """Fetch and return bugzilla token as string."""

        params = {
            'login': self.username,
            'password': self.password
        }
        url = '{0}/rest/login'.format(host)
        req = requests.get(url, params=params)
        decoded = json.loads(req.text)

        try:
            if 'token' not in decoded:
                raise InvalidCredentials
        except InvalidCredentials:
            err_header = self.output.get_header('BUGZILLA ERROR')

            err_msg = '{0}\n{1}\n{2}\n\n'.format(
                err_header,
                decoded['message'],
                decoded['documentation']
            )

            sys.exit(err_msg)
        else:
            return decoded['token']

    def bug_create(self, release_num, application, environment, 
        status, description, cc_mail=''):
        """Create bugzilla bug with description

        Note:
            On bugzilla-dev - available status:
            NEW, UNCONFIRMED, ASSIGNED, RESOLVED

            On bugzilla - available status:
            NEW, UNCONFIRMED, RESOLVED, REOPENED, VERIFIED
            FIXED, INVALID, WONTFIX, DUPLICATE, WORKSFORME, INCOMPLETE

        Returns:
            json string to POST to REST API
        """
        

        self.output.log('Creating new bug via bugzilla REST API...', True)
        url = '{0}/rest/bug?token={1}'.format(self.host, self.token)
        data = self._get_json_create(release_num, application,
            environment, status, description, cc_mail)

        self.output.log(data)

        req = requests.post(url, data=json.dumps(data), headers=HEADERS)
        try:
            new_bug_id = req.json()['id']
        except KeyError, e:
            print('\nERROR: {0}!\n'.format(req.text))
            exit()

        self.output.log('\nNew bug ID: {0}\nDONE!\n\n'.format(new_bug_id))
        return new_bug_id

    def bug_update(
            self, bug_id, comment):
        """Update bugzilla bug with new comment 

        Returns:
            json string to POST to REST API
        """

        self.output.log(
            'Updating bug #{0} via bugzilla REST API...'.format(bug_id), True)
        url = '{0}/rest/bug/{1}/comment?token={2}'.format(
            self.host, bug_id, self.token)

        data = self._get_json_update(bug_id, comment)
        self.output.log(data)

        req = requests.post(url, data=json.dumps(data), headers=HEADERS)
        new_comment_id = req.json()['id']

        if new_comment_id:
            self.output.log(
                '\nComment created! - new comment ID: {0}\n \
                DONE!\n\n'.format(new_comment_id))
        else:
            self.output.log(
                '\nERROR: Comment not created!\n\n'.format(new_comment_id))
           
        return new_comment_id

    def _parse_bug(self, bug_json):
        #bug = "bugs": [ { "id": 1234567 } ]
        return '1234567' 

    def _bug_latest_matching(self, json_bugs_matching):
        """Returns bug id from bug with latest time stamp from 
        json_search_results

        Returns:
            bug id as string 
        """


        self.output.log('Retrieve all matching bugs', True)

        bugs_unsorted = []
        bugs = json_bugs_matching["bugs"]

        for i in range(len(bugs)):
            id =  bugs[i]["id"]  
            creation_time =  bugs[i]["creation_time"]  
            bugs_unsorted.append([id, creation_time])

        self.output.log(bugs_unsorted)
        
        self.output.log('Sort bugs by creation_time', True)
        bugs_sorted = sorted(
            bugs_unsorted, key=lambda bugs_sorted: bugs_sorted[1])

        self.output.log(bugs_unsorted)
        self.output.log('DONE!')

        self.output.log('Get last bug from sorted list', True)
        bug_latest = bugs_sorted[-1]

        # return id only
        return bug_latest[0]

    def bug_search(self, summary):
        """Search for bugzilla bugs matching summary string 

        Returns:
            json string to GET from REST API
        """

        self.output.log('Searching bugs with summary: {0} \n \
            via bugzilla REST API...'.format(summary), True)
        url = '{0}/rest/bug'.format(self.host)
        
        data = self._get_json_search(summary)
        self.output.log(data)
       
        req = requests.get(url, params=data)
        return self._bug_latest_matching(req.json())


def main():

    bugzilla_username = 'johnnyquest@racebannon.com'
    bugzilla_password = 'hadji_is_a_geek'
    url_bugzilla = URL_BUGZILLA_DEV

    # Example: bug create
    bz = BugzillaRESTClient(url_bugzilla, bugzilla_username, bugzilla_password)

    bug_info = {
        'release_num': '1.2.3',
        'application': 'Loop-Client',
        'environment': 'STAGE',
        'status': 'NEW',
        'description': 'Lorem ipsum dolor sit amet, \
        ne dicat ancillae...'
    }
    print bz.bug_create(**bug_info)

    # Example: bug search 
    search_info = {
        'summary': 'Loop-Client'
    }
    print bz.bug_search(**search_info)


if __name__ == '__main__':

    main()
