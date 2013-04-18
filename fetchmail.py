
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
parser.add_argument('--start', metavar='IND', help='set start index (1 based)')
parser.add_argument('--ignore-exts', metavar='EXT',nargs='*', help='ignore any of the provided extensions')

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
if args.start is not None:
	START_IND = int(args.start)
if args.ignore_exts is not None:
	EXT_IGNORE_LIST = args.ignore_exts


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

print 'Fetching content...'
for i in range(len(msg_ids))[START_IND-1:]:
	print 'Fetching %s out of %s' % (i+1,len(msg_ids))
	resp,data = server.fetch(msg_ids[i],'RFC822')
	print 'Fetching done'
	for response_part in data:
		if isinstance(response_part, tuple):
			msg = email.message_from_string(response_part[1])
			print 'Processing \'%s\' from %s...' % (msg['Subject'],msg['From'])
			
			# create a directory for each email
			# based on the regex found in the Subject
			subj = msg['Subject'];
			if subj is None:
				subj = ''
			directorym = re.search(SUBJECT_REGEX,subj)
			if directorym is not None:
				directory = directorym.group(1)
			else:
				directory = ''
			
			if len(directory) is not 0:
				if not os.path.exists(BASE_PATH+directory):
					os.makedirs(BASE_PATH+directory)
		
			empty = True
			counter = 1
			for part in msg.walk():
				empty = False
				if part.get_content_maintype() == 'multipart':
					continue
				elif part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
					if len(part.get_payload(decode=True).strip())==0:
						print 'Empty body part, continuing...'
						continue
					print 'Parsing body...'
					# if the subject had not enough data, try to use content
					if len(directory) is 0:
						payload = part.get_payload(decode=True)
						if payload is None:
							payload = ''
						dsch = re.search(BODY_REGEX,payload)
						if dsch is not None:
							directory = dsch.group(1)
						else:
							directory = ''
							
						# at the end: concat the sender with subject and a trail of mail body
						if len(directory) is 0:
							directory = payload
							directory = "".join([c for c in msg['From'][:msg['From'].find('<')]+'-'+subj+'-'+directory[0:10] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
						if not os.path.exists(BASE_PATH+directory):
							os.makedirs(BASE_PATH+directory)
					
					fp = open(BASE_PATH+directory+'/notes.txt','wb')
					fp.write('Date: '+msg['Date']+'\n\n')
					fp.write('From: '+msg['From']+'\n\n')
					fp.write(part.get_payload(decode=True))
					fp.close()
				else:
					print 'Downloading Attachment with type \'%s\'' % part.get_content_type()
					filename = part.get_filename()
					if not filename:
						ext = mimetypes.guess_extension(part.get_content_type())
						if not ext:
							# Use a generic bag-of-bits extension
							ext = '.bin'
						filename = 'part-%03d%s' % (counter, ext)
					# check extension
					file_ext = filename[filename.rfind('.')+1:]
					if any(s in file_ext for s in EXT_IGNORE_LIST):
						print 'Ignoring extension \'%s\'' % part.get_content_type()
						continue
					counter +=1
					
					fp = open(BASE_PATH+directory+'/'+filename, 'wb')
					print 'Writing %s' % filename
					fp.write(part.get_payload(decode=True))
					print 'Writing done'
					fp.close()
				
			
			if empty is True:
				print '[EMPTY EMAIL]'
				fp = open(BASE_PATH+directory+'/notes.txt','wb')
				fp.write('Date: '+msg['Date']+'\n\n')
				fp.close()
	

