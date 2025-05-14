import re
import smtplib
import dns.resolver


def check_email(mail):
    # Address used for SMTP MAIL FROM command
    fromAddress = 'corn@bt.com'

    # Simple Regex for syntax checking

    # Email address to verify
    inputAddress = mail
    addressToVerify = str(inputAddress)

    # Syntax check

    # Get domain for DNS lookup
    splitAddress = addressToVerify.split('@')
    domain = str(splitAddress[1])

    # MX record lookup
    records = dns.resolver.resolve(domain, 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP()
    server.set_debuglevel(0)

    # SMTP Conversation
    server.connect(mxRecord)
    server.helo(server.local_hostname)  ### server.local_hostname(Get local server hostname)
    server.mail(fromAddress)
    code, message = server.rcpt(str(addressToVerify))
    server.quit()

    # Assume SMTP response 250 is success
    if code == 250:
        return True
    else:
        return False
