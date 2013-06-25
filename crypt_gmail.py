import gnupg
from email.parser import HeaderParser
import smtplib
from email.mime.text import MIMEText
import getpass
import imaplib

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'
print "Gmail user"
recipient = raw_input()
password = getpass.getpass("Gmail password:")
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(recipient,password)
session = smtplib.SMTP('smtp.gmail.com',587)
session.ehlo()
session.starttls()
session.login(recipient,password)

def encrypt(data):
  encrypted = gpg.encrypt(data,recipient,always_trust=True)
  return str(encrypted)

def all_folders():
  for folder in mail.list()[1]:
    yield folder.split("/")[1].split('"')[2]

def all_mail():
  for folder in all_folders():
    mail.select(folder)
    result, data = mail.search(None,'(NOT BODY "BEGIN PGP MESSAGE")')
    ids = data[0]
    id_list = ids.split()
    for imap_id in id_list:
      b_r,b_d = mail.fetch(imap_id,'(RFC822)')    
      h_r,h_d = mail.fetch(imap_id,'(BODY[HEADER.FIELDS (SUBJECT FROM)])')
      mail.store(imap_id, '+FLAGS', '\\Deleted')
      mail.expunge()
      parser = HeaderParser()
      msg = parser.parsestr(h_d[0][1])
      yield (dict(msg),b_d)

def send_mail(data,send_from,rcpt_to,subject):
  msg = MIMEText(data)
   
  msg['Subject'] = subject
  msg['From'] = send_from
  msg['To'] = rcpt_to

  session.sendmail(send_from,rcpt_to,msg.as_string())
  
for header,mail_body in all_mail():
  encrypted_body = encrypt(mail_body[0][1])
  send_mail(encrypted_body,header['From'],recipient,header['Subject'])
  print "Encrypted %s from %s" % (header['Subject'],header['From'])
