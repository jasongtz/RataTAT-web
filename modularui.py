#! /usr/bin/python

# RataTAT!
# Search &&& for bugs or new features

#	Modules imported and starting global variables
import Tkinter as tk
import time
import datetime as dt
#from fractions import Fraction
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

apptitle = "RataTAT v0.3 - DEMO"

#	EMAIL REPORT FUNCTION
def sendemail(subject, message):
	# Reads txt file to pull recipient and login info
	with open("sensitive/emaildata.txt", "r") as file:
		data = file.readlines()
	if "Feedback" in subject:	
		recip = data[0].strip("\n")
	elif "Report" in subject:
		recip = data[1].strip("\n")
	email = data[2].strip("\n")
	password = data[3].strip("\n")

	# Generates the message
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = email
	msg['To'] = recip
	msg.preamble = None

	# Attaches the daily report
	if "Report" in subject:
		msg.attach(MIMEText("\n" + handover() + "\n\n"))
		file = "%s.csv" % str(dt.date.today())
		fp = open(file, "rb")
		to_attach = MIMEText(fp.read())
		fp.close()
		to_attach.add_header("Content-Disposition", "attachment", \
			 filename = "%s.csv" % str(dt.date.today()))
		msg.attach(to_attach)
	
	# Attaches the daily, hourly, and current log files to a feedback submission
	if "Feedback" in subject:
		msg.attach(MIMEText(message))
		file1 = "dailydata.csv"
		fp1 = open(file1, "rb")
		to_attach1 = MIMEText(fp1.read())
		fp1.close()
		to_attach1.add_header("Content-Disposition", "attachment", filename = file1)
		file2 = "log.csv"
		fp2 = open(file2, "rb")
		to_attach2 = MIMEText(fp2.read())
		fp2.close()
		to_attach2.add_header("Content-Disposition", "attachment", filename = file2)
		msg.attach(to_attach1) 
		msg.attach(to_attach2)
	
	smtpserver = smtplib.SMTP('smtp.mail.me.com', 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo
	smtpserver.login(email, password)
	smtpserver.sendmail(email, recip, msg.as_string())
	smtpserver.quit()

#	DAILYDATA CSV FUNCTIONS 

# Creates the blank template of the current status log - only needed for debugging
def create_log():
	with open("log.csv", "w+") as blank:
		topline = [str(dt.date.today()), 1]
		header = ["Batteries", "Displays", "Calibrating", "Calibration Failures"]
		startvalues = [0, 0, 0, 0]
		writer = csv.writer(blank, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(topline)
		writer.writerow(header)
		writer.writerow(startvalues)
		writer.writerow(startvalues)

def csvhourlyupdate():
	# Shows (time minus 1 hour) to current time. Eg "10:00 - 11:00"
	times = str(int(time.strftime("%H")) - 1) + ":" + time.strftime("%M") + " - " + \
		time.strftime("%H:%M")
	with open("dailydata.csv", "a") as f:
		writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow([times, readgenius(), gethourlylog()[0], \
			gethourlylog()[2], gethourlylog()[3]])
	# Writes the hourly values back to 0
	writehourlylog([0, 0, 0, 0])

# csv_autolog() imports csvhourlyupdate() from above and runs it once per hour.
# This function is imported and ran by an exterior Python file, csvonly.py.

def csv_autolog():
	while True:
		now = dt.datetime.now()

		if now.hour == 23:
			report()
			time.sleep(3600)
		
		elif 7 < now.hour < 23:
			if now.minute == "00":
				csvhourlyupdate()
				time.sleep(60)
			else:
				time.sleep(60)
		else:
			time.sleep(60)

def handover():
	with open("dailydata.csv", "rb") as f:
		wholedaydata = [row for row in csv.reader(f)]	
	batteries = 0
	displays = 0
	fails = 0
	
	for x in range(2, len(wholedaydata)):
		try:
			batteries += int(wholedaydata[x][2])
		except:
			pass
		try:
			displays += int(wholedaydata[x][3])
		except:
			pass
		try:
			fails += int(wholedaydata[x][4])
		except:
			pass

	# Appends the dailydata.csv with daily totals
	with open("dailydata.csv", "a") as f:
		writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(["", "", "", "", ""])
		writer.writerow(["DAILY TOTALS", "", batteries, displays, fails])

	# Saves the dailydata.csv as a file with the date as the filename
	with open("dailydata.csv", "rb") as file:
		report = [row for row in csv.reader(file)]
		with open("previous daily logs/%s.csv" % str(dt.date.today()), "w") as write:
			writer = csv.writer(write, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
			for x in range(len(report)):
				writer.writerow(report[x])
	
	# Resets the dailydata.csv file to default
	with open("dailydata.csv", "w") as blank:
		writer = csv.writer(blank, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow([str(dt.date.today() + dt.timedelta(days=1))])
		writer.writerow(["Time", "Geniuses", "Batteries", \
			"Displays", "Calibration Failures"])

	# Changes the current log file's date
	status = readlogfile()
	status[0][0] = str(datetime.date.today() + datetime.timedelta(days=1))
	with open("log.csv", "wb") as file:
		for num in range(4):
			csv.writer(file, delimiter=",").writerow(status[num])
			
	return "Daily totals:\nBatteries: %d\n Displays: %d \nTOTAL: %d\n\n" \
		"To hand over for the morning: \n%d batteries, %d display to repair, " \
		"%d in the calibration machines." % (batteries, displays, (batteries+displays), \
		getcurrentstatus()[0], getcurrentstatus()[1], getcurrentstatus()[2])
		

#	COUNTER LOG/QUOTING FUNCTIONS
	
class Repairs(object):
	"""Different types of repairs are given an index indicating at which column their
	count is found in the log.csv file, and an exit message which is displayed when
	one is removed from the count in log.csv.
	"""
	def __init__(self, index, exitmessage):
			self.index = index
			self.exitmessage = exitmessage
			
	def add(self):
		"""Adds a new repair to the log, returns the quoted estimated time.
		
		Retrieves the current status and number of Geniuses doing repairs, 
		then adds 1 to the queue for repair type given by self.index.
		Writes the new values to the log file. Then runs the quoting functions, 
		passing in integers for arguments representing the current status.
		"""
		current_status = getcurrentstatus()
		genius = readgenius()	
		current_status[self.index] += 1
		writestatus(current_status)
		if self.index == 0:
			return quote_battery(current_status[0], current_status[1], genius)
		elif self.index == 1:
			return quote_display(current_status[0], current_status[1], \
				   current_status[2], current_status[3], genius)
		elif self.index == 3:
			hourlylog = gethourlylog()
			hourlylog[self.index] += 1
			writehourlylog(hourlylog)
			return "Display failed."

	def remove(self):
		"""Removes a completed repair from the log, or removes it from one repair type
		in order for it to be added to another.
		
		Retrieves the current status and number of Geniuses doing repairs, 
		then subtracts 1 from the queue for repair type given by self.index.
		Writes the new values to the log file, as in the add(self) function above.
		"""
		current_status = getcurrentstatus()
		if current_status[self.index] > 0:
			current_status[self.index] -= 1
		else:
			return "\nError!"

		if self.index == 2:
				if current_status[3] > 0:
					current_status[3] -= 1
			
		writestatus(current_status)
		# Writes to the hourly log for battery, calibration (display rfp), and failures
		if self.index != 1:
			hourlylog = gethourlylog()
			hourlylog[self.index] += 1
			writehourlylog(hourlylog)
		return self.exitmessage
			
# Instantiation of all repair/movement types
battery = Repairs(0, "\nBattery complete.")
display = Repairs(1, "\nDisplay awaiting calibration.")
calib = Repairs(2, "\nDisplay complete.")
fail = Repairs(3, None) # Failure counts get removed invisibly, thus no self.exitmessage

def quote_battery(bq, dq, genius):
	"""Takes the current repair queues in arguments, returns a turnaround time."""
	num = float((bq + dq)/genius * 0.25 + 0.5)
	# Checks if the repair can be completed same-day.
	if check_sameday(num):
		return "\n Quote %s" % round_tat(num)
	else:
		return "\nNEXT DAY"
	
def quote_display(bq, dq, dc, df, genius):
	"""As with quote_battery, but includes display-related status integers."""
	num = float((bq + dq + dc + df) / genius * 0.25 + 0.75)
	if check_sameday(num):
		return "\n Quote %s" % round_tat(num)
	else:
		return "\nNEXT DAY"

def check_sameday(num):
	"""Returns False if the estimated repair completion 
	time is after the store's closing hours.
	"""
	num_minutes = int(num%1*60)
	now = dt.datetime.now()
	carry_the_hour = ((now.minute + num_minutes) / 60)
	# Adds the repair time to the current time to estimate a completion time
	endtime = dt.time((now.hour + int(num) + carry_the_hour), \
					  (now.minute + num_minutes)%60)	
	if now.weekday() == 6:
		if endtime > dt.time(17, 50):
			return False
		else:
			return True
	else:
		if endtime > dt.time(19, 50):
			return False
		else:
			return True

def readlogfile():
	"""Opens the log file, returns a list where each line of the csv is a list."""
	with open("log.csv", "rb") as file:
		return [row for row in csv.reader(file)]  # List comprehension

def readgenius():
	"""Reads the cell of log.csv where the current number of Geniuses is stored."""
	return int(readlogfile()[0][1])

def getcurrentstatus():
	"""Converts the 2nd line of the status file into integers, returns as a list."""
	return [int(numbers) for numbers in readlogfile()[2]]

def writestatus(values):
	"""Takes the current status file, changes the values line, writes it back."""
	status = readlogfile()
	status[2] = values
	with open("log.csv", "wb") as file:
		for num in range(4):
			csv.writer(file, delimiter=",").writerow(status[num])

def gethourlylog():
	return [int(numbers) for numbers in readlogfile()[3]]
	
def writehourlylog(values):
	status = readlogfile()
	status[3] = values
	with open("log.csv", "wb") as file:
		for num in range(4):
			csv.writer(file, delimiter=",").writerow(status[num])

def round_tat(num):
	"""Changes the turnaround time from a float into natural language hours + minutes."""
	remain = num%1
	if num.is_integer():
		if int(num) == 1:
			return str(int(num)) + " hour."
		else:
			return str(int(num)) + " hours."
	else:
		if num < 1:
			return str(int(remain*60)) + " minutes."
		elif num-remain == 1:
			return str(int(num-remain)) + " hour and " + \
					str(int(remain*60)) + " minutes."
		else:
			return str(int(num-remain)) + " hours and " + \
					str(int(remain*60)) + " minutes."


# Used to refresh the status message
def get_status():
	current_status = getcurrentstatus()
	hourlylog = gethourlylog()
	return "%d displays, %d batteries/other awaiting repair." \
		"<br>There are %d phones in or awaiting calibration/testing.<br>" \
		"%d repairs completed so far this hour." % \
		(current_status[1], current_status[0], current_status[2], \
		(hourlylog[0] + hourlylog[2]))


def setgenius(genius):
	status = readlogfile()
	status[0][1] = genius
	with open("log.csv", "wb") as file:
		for number in range(4):
			csv.writer(file, delimiter=",").writerow(status[number])
	return declaregenius(genius)
	
def declaregenius(genius):	
	if genius == 1:
		return str(genius) + " Genius currently."
	else:
		return str(genius) + " Geniuses currently."


def displaymessage():
	with open("message.txt", "r") as file:
		message = file.readline()
		return "\n" + message

# Need to build these buttons in
def setmessage(message):
	with open("message.txt", "w") as file:
		file.write(message)
	refresh()
def defaultmessage():
	with open("message.txt", "w") as file:
		file.write("All clear. Choose a button above.")
	refresh()

def report():
	sendemail("Modular Report for %s" % str(dt.date.today()), \
		"Report attached.")
def sendfeedback(message):	
	sendemail("RataTAT Feedback", message)
