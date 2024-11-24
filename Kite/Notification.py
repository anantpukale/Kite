import datetime

import pywhatkit
class notification:
	def send_msg(self, msg):
		hour = datetime.datetime.now().hour
		minute = datetime.datetime.now().minute

		pywhatkit.sendwhatmsg("+919036639041",  msg, hour, minute+2, 15, True, 2)
