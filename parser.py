
import urllib2, re, sys
from optparse import OptionParser
from bs4 import BeautifulSoup

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

rowToSeek ="ivalo"
#colors to look for
LOW = "Low"
RAISED = "Raised"
MEDIUM = "Medium"
HIGH = "High"
VHIGH = "Very high"

COLORS = [
    ["#00FF00", LOW],
    ["#FFFF00", RAISED],
    ["#FFA500", MEDIUM],
    ["#FF0000", HIGH],
    ["#800000", VHIGH]
]
url = "http://aurora.fmi.fi/public_service/magforecast_fi.html"
sendTo =
demo = False

def sendMail(recipient=, message=""):
    me = 
    you = recipient

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "AURORA ALERT"
    msg['From'] = me
    msg['To'] = you
    text = message
    part1 = MIMEText(text, 'plain', _charset="UTF-8")
    msg.attach(part1)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()

    mail.sendmail(me, you, msg.as_string())
    mail.quit()

def parsePage(url, location="ivalo", recipient="tapio.vihanta@gmail.com"):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page, 'lxml')

    try:
        td =  soup.find(text=re.compile(r'%s' %location, re.IGNORECASE))
        if(td is None):
            raise Exception("no valid location found")
        tr = td.find_parent("tr")
        # go to next hour-column
        nextHourLow = tr.select("td:nth-of-type(3)")
        nextHourHigh = tr.select("td:nth-of-type(4)")

        textLow = [col[1] for col in COLORS if col[0] == nextHourLow[0]["bgcolor"]][0]
        textHigh = [col[1] for col in COLORS if col[0] == nextHourHigh[0]["bgcolor"]][0]
        valueLow = nextHourLow[0].text
        valueHigh = nextHourHigh[0].text


        if ((textLow == HIGH or textLow == VHIGH) and \
           (textHigh == HIGH or textHigh == VHIGH)) or demo is True:
            message = u"AURORA forecast for: %s for the next hour\
 is %s - %s (%s - %s)" %(location, textLow, textHigh, valueLow , valueHigh)
            sendMail(recipient, message )

    except Exception as e:
        print "%s" %e

parser = OptionParser()
parser.add_option("-l", "--location", dest="location",
                  help="set location to look info for", metavar="LOC")
parser.add_option("-t", "--to", dest="to",
                  help="set email address where to send", metavar="EMAIL")
#get the current forecast anyway
parser.add_option("-d", "--demo", dest="demo", action="store_true",
                  help="test", metavar="TEST")
(options, args) = parser.parse_args()

if options.location:
    rowToSeek = options.location.decode(sys.getfilesystemencoding())
if options.to:
    sendTo = options.to.decode(sys.getfilesystemencoding())
if options.demo:
    demo = True

parsePage(url, rowToSeek, sendTo)
