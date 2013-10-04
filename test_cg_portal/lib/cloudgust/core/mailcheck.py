import imaplib

username = "rohit@cloudgust.com"
password = ""


imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
imap_server.login(username, password)

imap_server.select('INBOX')
status, response = imap_server.search(None,"ALL")
print status
print response
unreadcount = int(response[0].split()[2].strip(').,]'))
print unreadcount