from flask import request

import dns.resolver
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import settings

EXCHANGE_CACHE = {}

def get_email_exchange(email_address):
    domain = email_address.rsplit('@', 1)[-1].lower()
    if domain in EXCHANGE_CACHE:
        return EXCHANGE_CACHE[domain]

    resolver = dns.resolver.Resolver()
    resolver.nameservers = settings.DNS_IPS

    try:
        answers = resolver.query(domain, 'MX')
    except Exception, e:
        return None

    for a in answers:
        exchange = str(a.exchange)
        EXCHANGE_CACHE[domain] = exchange
        return exchange
    assert False


def send_email(recipient, subject, html_message):
    host = request.host
    if ':' in host:
        host.split(':', 1)[0]
    me = "no-reply@%s" % (host,)
    you = recipient

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'Frippery <%s>' % (me,)
    msg['To'] = you

    part1 = MIMEText('', 'plain')
    part2 = MIMEText(html_message, 'html')

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP(get_email_exchange(recipient))
    s.sendmail(me, you, msg.as_string())
    s.quit()
