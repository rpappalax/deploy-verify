################################
deploy-verify
################################

.. image:: https://travis-ci.org/rpappalax/deploy-verify.svg?branch=dev
    :target: https://travis-ci.org/rpappalax/deploy-verify


.. contents::


*******************************
Description
*******************************

**Summary**

Python scripts to handle verification and testing of Cloud Services deployments.

- `Bugzilla Ticket Handler`_ 
- `Stack Check`_
- `End-2-End (e2e) Test`_ 
- `Loadtest`_ 


**Supported projects**

- loop-client
- loop-server
- msisdn-gateway
- shavar
- autopush 
- readinglist


Bugzilla Ticket Handler 
===============================


Pre-requisites
--------------------------
You must set the following environment variables

- BASTION_HOST
- BASTION_PORT
- BASTION_USERNAME
- GITHUB_ACCESS_TOKEN

You will need either an account to:
- bugzilla.mozilla.org
- bugzilla-dev.allizom.org
For creating and updating deployment tickets in bugzilla.


Usage
--------------------------
Bugzilla deployment ticket handler. Use to create / update 
bugzilla deployment tickets .

.. parsed-literal::

 (venv)$ ticket -h

 positional arguments:
  {NEW,UPDATE}          Ticket action
    NEW                 Create a NEW deployment ticket.
    UPDATE              UPDATE an existing deployment ticket

  -u BUGZILLA_USERNAME, --bugzilla-username BUGZILLA_USERNAME
  -p BUGZILLA_PASSWORD, --bugzilla-password BUGZILLA_PASSWORD
  -r REPO, --repo REPO  Example: loop-server (default: None)
  -B, --bugzilla-mozilla
                        Add this option, and you'll post to
                        bugzilla.mozilla.org (not bugzilla-dev.allizom.or)
                        (default: False)

 (venv)$ ticket NEW -h

  -o REPO_OWNER, --repo-owner REPO_OWNER
                        Example: mozilla-services
  -e ENVIRONMENT, --environment ENVIRONMENT
                        Enter: STAGE, PROD
  -m CC_MAIL, --cc-mail CC_MAIL
                        Example: xyz-services-dev@mozilla.com NOTE: must be a
                        registered username!


 (venv)$ ticket UPDATE -h

  -h, --help            show this help message and exit
  -i BUG_ID, --bug-id BUG_ID
                        Example: 1234567
  -c COMMENT, --comment COMMENT
                        Enter: <your bug comment>



Usage - Example
--------------------------

Post to bugzilla-dev.allizom.org

.. parsed-literal::

  # Create a new ticket
  $ ticket -u johnny@quest.com -p password123 NEW -o mozilla-services -r loop-server -e STAGE 

  # Update an existing ticket with Bug ID = 1234567
  $ ticket -u johnny@quest.com -p password123 -r loop-server UPDATE -i 1234567 -u "New comment here" 

  # Update an the latest deployment ticket for <loop-server> (no Bug ID specified)
  $ ticket -u johnny@quest.com -p password123 -r loop-server UPDATE -u "New comment here" 


Post to bugzilla.mozilla.org (-B option) 

.. parsed-literal::

  # Create a new ticket
  $ ticket -u johnny@quest.com -p password123 NEW -o mozilla-services -r loop-server -e STAGE -m realuser@bugmail.com -B

  # Update an existing ticket with Bug ID = 1234567
  $ ticket -u johnny@quest.com -p password123 UPDATE -i 1234567 -u "New comment here" -B


New Ticket - Example
--------------------------

Release notes will be generated and posted into a new bugzilla deployment ticket.


.. parsed-literal::

 -------------------
 RELEASE NOTES
 -------------------

 `<https://github.com/mozilla/loop-client/releases>`_


 COMPARISONS

 `<https://github.com/mozilla/loop-client/compare/0.13.4...0.13.5>`_
 `<https://github.com/mozilla/loop-client/compare/0.13.5...0.14.0>`_
 `<https://github.com/mozilla/loop-client/compare/0.14.0...0.15.0>`_


 TAGS

 `<https://github.com/mozilla/loop-client/releases/tag/0.15.0>`_
 `<https://github.com/mozilla/loop-client/commit/d706753dbcacfe17081d8c04b54652dbee36302f>`_


 CHANGELOG
 0.15.0 (2015-03-09)
 -------------------

  \- `Bug 1047040 <https://bugzilla.mozilla.org/show_bug.cgi?id=1047040>`_ - Add browser-specific graphic of GUM prompt to the media-wait message
  \- `Bug 1131550 <https://bugzilla.mozilla.org/show_bug.cgi?id=1131550>`_ - Loop-client extraction script should preserve locale information when importing m-c changes
  \- `Bug 1135133 <https://bugzilla.mozilla.org/show_bug.cgi?id=1135133>`_ - Loop-client extraction script should support pulling from different repositories/branches
  \- `Bug 1137469 <https://bugzilla.mozilla.org/show_bug.cgi?id=1137469>`_ - If an uncaught exception occurs whilst processing an action, the dispatcher can fail, rendering parts of Loop inactive
  \- `Bug 1131568 <https://bugzilla.mozilla.org/show_bug.cgi?id=1131568>`_ - Update the OpenTok SDK to version 2.5.0



*******************************
Setup
*******************************

Github Access Token
===============================

deploy-verify will make multiple calls to github API.
You're allowed up to 60 calls / hour without authentication, but you'll soon
run out!

Instead, create an access token from your github home page.  Go to:
#. Settings > Applications > Generate New Token
#. Create an environment variable 'ACCESS_TOKEN' or enter it into the config.py:

.. parsed-literal::

  $ export ACCESS_TOKEN=<your_access_token_here>

Build
===============================

.. parsed-literal::

 $ make build
 $ source ./venv/bin/activate


*******************************
Stack Check
*******************************


Stack-Check
===============================


Pre-requisites
--------------------------
You will need either an account to:
- bugzilla.mozilla.org
- bugzilla-dev.allizom.org
for updating stack-check results to deployment ticket in bugzilla.

You will need an AWS instance profile to run boto scripts



Usage
--------------------------
Bugzilla deployment ticket handler. Use to create / update 
bugzilla deployment tickets .

.. parsed-literal::


 $ stack-check -h
 usage: stack-check [-h] -a APPLICATION -r REGION [-t TAG_NUM] [-e ENVIRONMENT]
                    [-i DEPLOYMENT_TICKET_ID] -u BUGZILLA_USERNAME -p
                    BUGZILLA_PASSWORD [-B]
 
 Sanity check for basic stack deployment verification
 
 optional arguments:
   -h, --help            show this help message and exit
   -a APPLICATION, --application APPLICATION
                         Enter: loop-server, loop-client, etc. (default: loop-
                         server)
   -r REGION, --region REGION
                         Enter: eu-west-1, us-east-1 (default: eu-west-1)
   -t TAG_NUM, --tag-num TAG_NUM
                         Enter: 0.17.2 (default: None)
   -e ENVIRONMENT, --environment ENVIRONMENT
                         Enter: STAGE, PRODUCTION (default: STAGE)
   -i DEPLOYMENT_TICKET_ID, --deployment-ticket-id DEPLOYMENT_TICKET_ID
                         Enter: 1234567 (default: None)
   -u BUGZILLA_USERNAME, --bugzilla-username BUGZILLA_USERNAME
   -p BUGZILLA_PASSWORD, --bugzilla-password BUGZILLA_PASSWORD
   -B, --bugzilla-mozilla
                         Set this switch to post directly to
                         bugzilla.mozilla.org (without switch posts to:
                         bugzilla-dev.allizom.org) (default: False)



*******************************
End-2-End (e2e) Test 
*******************************
<TBD>


*******************************
Loadtest
*******************************
<TBD>








