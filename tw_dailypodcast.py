'''Complete script that creates a podcast from the The Week UK's Daily Briefing.
Only the details for the sending address and recipients is required below.'''

import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import time
import schedule


def daily_briefing():
	#Scrape from the Daily Briefing page, and save as lists for the numbers and the corresponding passages. Saved separately to create a pause in the podcast file
	response = requests.get("https://www.theweek.co.uk/daily-briefing#1")
	soup = BeautifulSoup(response.text, "html.parser")
	titles = [title.get_text(strip=True) for title in soup.find_all(class_="polaris__heading polaris__single-slide--title -after-image")]
	contents = [content.get_text(strip=True) for content in soup.find_all(class_='polaris__single-slide--children')]

	#Write the MP3 file with speech included, in UK English. Matching lists up from previous step.
	with open('daily_briefing.mp3', 'wb') as f:
		for i in range(len(titles)):
			gTTS(str(i+1), lang = 'en', tld = 'co.uk').write_to_fp(f)
			gTTS(titles[i], lang = 'en', tld = 'co.uk').write_to_fp(f)
			gTTS(contents[i], lang = 'en', tld = 'co.uk').write_to_fp(f)

	#Defining function to make an email that allows attachments
	def send_mail(send_from, send_to, subject, text, file):
		assert isinstance(send_to, list)

		msg = MIMEMultipart()
		msg['From'] = send_from
		msg['To'] = COMMASPACE.join(send_to)
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = subject

		with open(file, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(file)
			)
		# After the file is closed
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
		msg.attach(part)
		msg.attach(MIMEText(text))
		return msg

	#Define what is in the email with the podcast attachment. Fill in relevant fields below.
	sent_from = '[Sender email address]'
	sent_password = '[Sender password]'
	send_to = ['[Enter recipient here]']
	subject = 'Daily Briefing'
	body = "Play the attached mp3 for today's Daily Briefing from The Week"
	podcast = "daily_briefing.mp3"

	#Send the email - gmail is used here given my familiarity with it. Others can be used in the 'smtp_server' variable.
	try:
		smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		smtp_server.ehlo()
		smtp_server.login(sent_from, sent_password)
		smtp_server.sendmail(sent_from, send_to, send_mail(sent_from, send_to, subject, body, podcast).as_string())
		smtp_server.close()
		print("Email sent successfully!")
	except Exception as ex:
		print("Something went wrong….",ex)


#Basic function defining when it is sent out - this needs making less archaic! Works bluntly for now.
schedule.every().day.at("08:00").do(daily_briefing)

while True:
	schedule.run_pending()
	time.sleep(60)