
import imaplib
import email
import mimetypes
import re
import os
import argparse
import sys

# CONFIGURATION
BASE_PATH = '~/homeworks'
HOST = 'imap.gmail.com'
USERNAME = 'username'
PASSWORD = 'password'
MAILBOX = 'INBOX'
GMAIL_SEARCH = ""
SUBJECT_REGEX = "(.*)"
BODY_REGEX = "(.*)"
START_IND = 1
OUT = 'list.txt'

# ignore mimes that contain any of the followings
EXT_IGNORE_LIST = ['exe','iso']

class BeautifulArgParser(argparse.ArgumentParser):
     def error(self, message):
         sys.stderr.write('error: %s\n' % message)
         self.print_help()
         sys.exit(2)

# if input argument, override the configuration
parser = BeautifulArgParser(description='Batch downloader of emails with attachment')
parser.add_argument('base', metavar='BASE_PATH', help='set base directory')
parser.add_argument('--host', help='set IMAP server (default: Gmail server)')
parser.add_argument('--user', help='set username')
parser.add_argument('--pass', metavar='PASS', dest='passw', help='set password')
parser.add_argument('--search', metavar='CRITERIA', help='set gmail search criteria')
parser.add_argument('--mailbox', help='set mailbox (default: inbox)')
parser.add_argument('--subject', metavar='REGEX', help='set subject regex')
parser.add_argument('--body', metavar='REGEX', help='set body regex')
parser.add_argument('--out', metavar='REGEX', help='set output file')

args = parser.parse_args()

BASE_PATH = args.base

if args.host is not None:
	HOST = args.host
if args.user is not None:
	USERNAME = args.user
if args.passw is not None:
	PASSWORD = args.passw
if args.search is not None:
	GMAIL_SEARCH = args.search
if args.mailbox is not None:
	MAILBOX = args.mailbox
if args.subject is not None:
	SUBJECT_REGEX = args.subject
if args.body is not None:
	BODY_REGEX = args.body
if args.out is not None:
	OUT = args.out


# the path should be / terminated
if not BASE_PATH.endswith('/'):
	BASE_PATH+='/'

if not os.path.exists(BASE_PATH):
	os.makedirs(BASE_PATH)

server = imaplib.IMAP4_SSL(HOST)
server.login(USERNAME, PASSWORD)

print 'Logged in as %s successfully.' % USERNAME

server.select(MAILBOX)
print 'Selected %s' % MAILBOX

status, email_ids = server.uid('search',None,'X-GM-RAW',GMAIL_SEARCH)

if status != 'OK':
	raise Exception("Error running imap fetch: "
					"%s" % status)

msg_ids = email_ids[0].split()

print 'Search returned: %s results' % len(msg_ids)

print 'Peeking subject...'

fp = open(BASE_PATH+'/'+OUT,'wb')
fp.write('Total items: '+str(len(msg_ids))+'\n')
for i in range(len(msg_ids)):
	print 'Peeking subject %s out of %s' % (i+1,len(msg_ids))
	resp,data = server.fetch(msg_ids[i],'(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM)])')
	print 'Peeking done'
	for response_part in data:
		if isinstance(response_part, tuple):
			msg = email.message_from_string(response_part[1])
			print 'Processing \'%s\' from %s...' % (msg['Subject'],msg['From'])
			
			# create a directory for each email
			# based on the regex found in the Subject
			subj = msg['Subject'];
			if subj is None:
				subj = ''
			match = re.search(SUBJECT_REGEX,subj)
			if match is None:
				sender = msg['Subject']
			else:
				sender = match.group(1)
			fp.write(sender+'\n')

fp.close()
	

