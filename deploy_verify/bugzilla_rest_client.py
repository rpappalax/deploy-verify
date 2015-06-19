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

    def _component(self, host):
        """Return Bugzilla component as string

        Note:
            bugzilla-dev doesn't mirror the same components, so
            use 'General'
        """

        if 'dev' in host:
            return COMPONENT_DEV
        else:
            return COMPONENT_PROD

    def _get_json_create(
        self, release_num, product, environment, status, description, cc_mail=''):
        """Returns bugzilla JSON string to POST to REST API."""

        component = self._component(self.host)
        #short_desc = 'Please deploy {0} {1} to {2}'.format(
        short_desc = '[deployment] {0} {1} - {2}'.format(
            product, release_num, environment)

        data = {
            'product': 'Mozilla Services',
            'component': 'General',
            'component': component,
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

    def bug_create(
            self, release_num, product, environment, status, description, cc_mail=''):
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
        data = self._get_json_create(
            release_num, product, environment, status, description, cc_mail)

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

        self.output.log('Updating bug #{0} via bugzilla REST API...'.format(bug_id), True)
        url = '{0}/rest/bug/{1}/comment?token={2}'.format(self.host, bug_id, self.token)
        data = self._get_json_update(bug_id, comment)

        self.output.log(data)

        req = requests.post(url, data=json.dumps(data), headers=HEADERS)
        new_comment_id = req.json()['id']

        if new_comment_id:
            self.output.log('\nComment created! - new comment ID: {0}\nDONE!\n\n'.format(new_comment_id))
        else:
            self.output.log('\nERROR: Comment not created!\n\n'.format(new_comment_id))
           
        return new_comment_id


def main():

    bugzilla_username = 'johnnyquest@racebannon.com'
    bugzilla_password = 'hadji_is_a_geek'
    ticket = BugzillaRESTClient(
        URL_BUGZILLA_DEV, bugzilla_username, bugzilla_password)

    bug_info = {'release_num': '1.2.3',
                'product': 'demo-server',
                'environment': 'STAGE',
                'status': 'NEW',
                'description': 'Lorem ipsum dolor sit amet, \
                ne dicat ancillae...'}

    print ticket.bug_create(**bug_info)


if __name__ == '__main__':

    main()
