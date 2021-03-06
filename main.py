import os
import time
import datetime
import random
import pygame
import io
import sys
import builtins
import traceback
import subprocess
import configparser
from subprocess import check_output, call
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config

from lib import constants
from lib import utils

os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')


class DigitalClock(FloatLayout):
	secs_to_next_minute = int(0)
	display_time = StringProperty("00 : 00")
	clock_view = NumericProperty(1)  # Variable to enable view of the Clock Time
	settings_view = NumericProperty(0)  # Variable to enable view of the Settings & Alarm Time
	settings_pic = StringProperty("./Images/Buttons/Settings_Normal.png")
	am_pm_alarm = NumericProperty(0)  # Variable to view AM/PM button in settings when 12hr clock is selected
	is_alarming = NumericProperty(0)  # Track when Alarm is Active
	is_snoozing = NumericProperty(0)  # Track when in Snooze mode
	alarm_time_hour = NumericProperty(0)
	alarm_time_minute = NumericProperty(0)
	alarm_time = StringProperty('0')
	set_sunday = StringProperty('0')
	set_monday = StringProperty('0')
	set_tuesday = StringProperty('0')
	set_wednesday = StringProperty('0')
	set_thursday = StringProperty('0')
	set_friday = StringProperty('0')
	set_saturday = StringProperty('0')
	alarm_switch = NumericProperty(0)
	switch_text = StringProperty('OFF')
	hr_setting = NumericProperty(0)
	hr_text = StringProperty('24HR')
	am_pm_clock = NumericProperty(0)
	am_pm_clock_text = StringProperty('AM')
	am_pm_setting = NumericProperty('0')
	am_pm_text = StringProperty('AM')
	nfc_cap = str('3e')
	nfc_cap2 = str('4>')
	nfc_hulk = str('48')
	nfc_hulk2 = str('4H')
	nfc_locked = False
	colour = NumericProperty(0)
	curr_time = int
	curr_day_name = StringProperty('')
	button_state = StringProperty('normal')
	alarm_event = ()
	nfc_checking = int(0)
	section = int(0)  # Section of audio files to use 1=1-7, 2=8-14, 3=15-21
	audio_path = str('')
	audio = int(0)
	curr_vol = NumericProperty(50)
	label_vol = StringProperty('0%')
	pygame.init()

	def startup(self):
		config_mod = False

		if not os.path.exists(os.path.join(constants.FILES, 'config.ini')):
			utils.create_default_config_file()

		config = configparser.ConfigParser()
		self.load_config_file(config)

		os.system("amixer sset 'Speaker' " + str(self.curr_vol) + "%")
		# subprocess.Popen(['gmediarender', '--gstout-audiosink=alsasink'])
		self.update()

	def load_config_file(self, config):
		config.read(os.path.join(constants.FILES, 'config.ini'))
		self.alarm_time_hour = int(config['Alarm Time']['alarm_time_hour'])
		self.alarm_time_minute = int(config['Alarm Time']['alarm_time_minute'])
		now = datetime.datetime.now()
		self.alarm_time = now.replace(hour=self.alarm_time_hour, minute=self.alarm_time_minute).strftime('%H : %M')
		# self.alarm_time = (str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2))

		print('sunday')
		print(self.set_sunday)
		self.set_sunday = config['Alarm Days']['set_sunday']
		print(type(self.set_sunday))
		self.set_monday = config['Alarm Days']['set_monday']
		print(self.set_monday)
		self.set_tuesday = config['Alarm Days']['set_tuesday']
		print(self.set_tuesday)
		self.set_wednesday = config['Alarm Days']['set_wednesday']
		print(self.set_wednesday)
		self.set_thursday = config['Alarm Days']['set_thursday']
		print(self.set_thursday)
		self.set_friday = config['Alarm Days']['set_friday']
		print(self.set_friday)
		self.set_saturday = config['Alarm Days']['set_saturday']
		print(self.set_saturday)

		self.alarm_switch = config['Miscellaneous']['alarm_switch']
		self.switch_text = config['Miscellaneous']['switch_text']
		self.hr_setting = config['Miscellaneous']['hr_setting']
		self.hr_text = config['Miscellaneous']['hr_text']
		self.am_pm_clock = config['Miscellaneous']['am_pm_clock']
		self.am_pm_clock_text = config['Miscellaneous']['am_pm_clock_text']
		self.am_pm_setting = config['Miscellaneous']['am_pm_setting']
		self.am_pm_text = config['Miscellaneous']['am_pm_text']

		self.nfc_cap = config['Character IDs']['nfc_cap']
		self.nfc_cap2 = config['Character IDs']['nfc_cap2']
		self.nfc_hulk = config['Character IDs']['nfc_hulk']
		self.nfc_hulk2 = config['Character IDs']['nfc_hulk2']

	def update(self, dt=0):
		Clock.unschedule(self.update)  # attempt to fix memory leak - Attempt Successful :)
		if self.hr_setting == 0:
			self.display_time = time.strftime("%H : %M")
		else:
			if self.hr_setting == 12:
				self.display_time = time.strftime("%I : %M")
		self.schedule_update()

	def schedule_update(self, dt=0):
		self.am_pm_clock_text = time.strftime("%p")
		current_time = time.localtime()
		seconds = current_time[5]
		self.curr_time = datetime.datetime.now()
		# self.curr_day_name = self.curr_time.strftime("%A") + " - " + self.curr_time.strftime("%B") + " " + self.curr_time.strftime("%-d")
		self.curr_day_name = self.curr_time.strftime("%A")
		if ((self.display_time == self.alarm_time)  # If alarm time is equal to current time
				and (self.alarm_switch == 1)  # and alarm switch is ON
				and (self.is_alarming == 0)):  # and system is currently not in alarm
			if (str(
					datetime.datetime.today().isoweekday()) == "1" and self.set_monday == '1'  # checking current day of week against if it's enabled below
					or str(datetime.datetime.today().isoweekday()) == "2" and self.set_tuesday == '1'
					or str(datetime.datetime.today().isoweekday()) == "3" and self.set_wednesday == '1'
					or str(datetime.datetime.today().isoweekday()) == "4" and self.set_thursday == '1'
					or str(datetime.datetime.today().isoweekday()) == "5" and self.set_friday == '1'
					or str(datetime.datetime.today().isoweekday()) == "6" and self.set_saturday == '1'
					or str(datetime.datetime.today().isoweekday()) == "7" and self.set_sunday == '1'):
				if ((self.hr_setting == 12)
						and (self.am_pm_text == self.am_pm_clock_text)):
					self.alarm_start()
				else:
					if (self.hr_setting == 0):
						self.alarm_start()
		else:
			self.secs_to_next_minute = (60 - seconds)
			Clock.schedule_once(self.update, self.secs_to_next_minute)  # Update again in 1 minute

	def alarm_start(self, *args):
		self.is_alarming = 1  # put system in alarm mode, this is probably reduntant by this point with as many unschedules and kills I have in the script
		self.settings_pic = "./Images/Buttons/Settings_Normal.png"
		self.settings_view = 0
		self.clock_view = 1
		self.button_state = "normal"
		print("setting volume")
		os.system("amixer sset 'Speaker' 100%")
		print("volume set")
		Clock.schedule_once(self.update, self.secs_to_next_minute)  # update again in 1 minute
		self.alarm_loop()

	def alarm_loop(self, *args):
		Clock.unschedule(self.alarm_event)  # unschedule the 1 second loop that runs self.alarm_loop
		self.alarm_event = Clock.schedule_interval(self.alarm_loop,
		                                           1)  # Reschedule for one second. Doing Clock.schduled_once in 1 second intervals had bad results.
		play_num = int(0)
		file_type = str('')
		nfc_read = str()
		self.settings_view = 0
		self.is_snoozing = 0
		self.am_pm_alarm = 0
		if self.nfc_locked == False:
			if (self.nfc_checking == 0):  # Allows only one instance of running the NFC check.
				self.nfc_checking = 1
				self.nfc_read = ''
				"""Grab the entire output of the NFC mobule from the I2C channel."""
				try:  # Run the nfc-poll command and get its output
					self.nfc_read = check_output('nfc-poll',
					                             universal_newlines=True)  # universal_newlines just makes it easier to read if you decide to Print
				except:
					pass  # If there's an error, just move along and try again.
				self.nfc_checking = 0
				if (self.nfc_cap in str(self.nfc_read)  # Determine audio file path based on NFC read
						or self.nfc_cap2 in str(self.nfc_read)):
					self.audio_path = "/home/pi/Desktop/PyClock/Sounds/01-CaptainAmerica/"
					self.nfc_locked = True
				else:
					if (self.nfc_hulk in str(self.nfc_read)  # Determine audio file path based on NFC read
							or self.nfc_hulk2 in str(self.nfc_read)):
						self.audio_path = "/home/pi/Desktop/PyClock/Sounds/02-Hulk/"
						self.nfc_locked = True
					else:
						self.audio_path = "/home/pi/Desktop/PyClock/Sounds/"  # Default alarm sounds if no NFC tag is found that matches above
						self.nfc_locked = True
		if self.is_alarming == 1 and (self.alarm_switch == 1):
			if self.colour == 0:
				self.colour = 1
			else:
				self.colour = 0
			if pygame.mixer.get_busy() == False:  # Check that audio currently isn't running
				rando = NumericProperty(0)
				if self.audio_path == "/home/pi/Desktop/PyClock/Sounds/":
					self.rando = random.randint(1, 2)
					file_type = '.wav'
					self.section = 0
				else:
					self.rando = random.randint(1, 7)  # Random number between 1 and 7, inclusive
					file_type = '.ogg'
					if self.section == 0:  # Increment to next section every round
						self.section = 7
					else:
						if self.section == 7:
							self.section = 14
						else:
							self.section = 0
				play_num = (self.rando) + (
					self.section)  # My files are split into 3 sections, 1-7, 8-14, 15-21 based on natural progression of intensity
				sound_file = pygame.mixer.Sound(
					str(self.audio_path + str(play_num) + file_type))  # Load sound file into Pygame
				alarm = pygame.mixer.Sound(sound_file)  # Play sound file
				alarm.set_volume(1.0)
				# volume = alarm.get_volume()
				alarm.play()
		else:
			self.is_alarming = 0  # Shouldn't need this, but doesn't hurt. Some redundant stuff from def switch_state
			Clock.unschedule(self.alarm_event)

	def snooze_func(self, *args):
		if ((self.is_alarming == 1)
				and (self.is_snoozing == 0)):
			self.is_snoozing = 1
			Clock.unschedule(self.alarm_event)  # unschedule the 1 second loop that runs self.alarm_loop
			self.section = 0
			self.alarm_event = Clock.schedule_once(self.alarm_loop, 300)  # schedule new 5-minute Snooze timer
			self.colour = 0  # Set background color to Black
			self.nfc_locked = False  # Reset NFC to try again for tag
			if pygame.mixer.get_busy() == True:  # If sounds is currently playing
				pygame.mixer.stop()  # Stop currently playing sound

	def cancel_func(self, *args):
		if self.is_alarming == 1:
			self.is_snoozing = 0
			self.is_alarming = 0
			Clock.unschedule(self.alarm_event)  # unschedule the 1 second loop that runs self.alarm_loop
			self.section = 0
			self.colour = 0  # Set background color to Black
			self.nfc_locked = False  # Reset NFC to try again for tag
			os.system("amixer sset 'Speaker' " + str(self.curr_vol) + "%")
			if pygame.mixer.get_busy() == True:  # If sounds is currently playing
				pygame.mixer.stop()  # Stop currently playing sound

	def switch_state(self, *args):  # Arm/disarm alarm
		if self.settings_view == 1:
			if self.alarm_switch == 0:
				self.alarm_switch = 1
				self.switch_text = "ALARM ON"
			else:
				self.alarm_switch = 0  # Toggle switch mode to "Off"
				self.switch_text = "ALARM OFF"
				if self.is_alarming == 1:
					self.cancel_func()  # Call function to stop alarming
			self.save_config()

	def click_settings(self, *args):
		if self.settings_view == 0:
			self.settings_pic = "./Images/Buttons/Settings_Pushed.png"
			self.settings_view = 1  # See digitalclock.kv for buttons using this variable
			self.clock_view = 0  # See digitalclock.kv for buttons using this variable
			self.am_pm_clock = 0
			if self.hr_setting == 12:
				self.am_pm_alarm = 1
			else:
				self.am_pm_alarm = 0
		else:
			self.settings_pic = "./Images/Buttons/Settings_Normal.png"
			self.settings_view = 0
			self.clock_view = 1
			self.am_pm_alarm = 0
			if self.hr_setting == 12:
				self.am_pm_clock = 1
			else:
				self.am_pm_clock = 0
			self.save_config()

	def click_12hr(self, *args):
		if self.settings_view == 1:
			if self.hr_setting == 0:
				self.hr_setting = 12
				self.display_time = time.strftime("%I : %M")
				self.am_pm_clock_text = time.strftime("%p")
				self.hr_text = "12HR"
				self.am_pm_alarm = 1
				if self.alarm_time_hour > 12:
					self.alarm_time_hour = self.alarm_time_hour - 12
					self.am_pm_setting = 1
					self.am_pm_text = "PM"
				if self.alarm_time_hour == 0:
					self.alarm_time_hour = self.alarm_time_hour + 12
					self.am_pm_setting = 0
					self.am_pm_text = "AM"
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(
					2)  # zfill used for padding single digits numbers with a zero
				self.save_config()
			else:
				self.hr_setting = 0
				self.display_time = time.strftime("%H : %M")
				self.hr_text = "24HR"
				self.am_pm_alarm = 0
				self.save_config()

	def alarm_am_pm(self, *args):
		if self.am_pm_setting == 0:
			self.am_pm_setting = 1
			self.am_pm_text = "PM"
		else:
			self.am_pm_setting = 0
			self.am_pm_text = "AM"

	def save_config(self):
		config_file = configparser.ConfigParser()
		config_file['Alarm Time'] = {'alarm_time_hour': str(self.alarm_time_hour),
		                             'alarm_time_minute': str(self.alarm_time_minute),
		                             }
		config_file['Alarm Days'] = {'set_sunday': str(self.set_sunday),
		                             'set_monday': str(self.set_monday),
		                             'set_tuesday': str(self.set_tuesday),
		                             'set_wednesday': str(self.set_wednesday),
		                             'set_thursday': str(self.set_thursday),
		                             'set_friday': str(self.set_friday),
		                             'set_saturday': str(self.set_saturday),
		                             }
		config_file['Miscellaneous'] = {'alarm_switch': str(self.alarm_switch),
		                                'switch_text': str(self.switch_text),
		                                'hr_setting': str(self.hr_setting),
		                                'hr_text': str(self.hr_text),
		                                'am_pm_clock': str(self.am_pm_clock),
		                                'am_pm_clock_text': str(self.am_pm_clock_text),
		                                'am_pm_setting': str(self.am_pm_setting),
		                                'am_pm_text': str(self.am_pm_text),
		                                }
		config_file['Character IDs'] = {'nfc_cap': str(self.nfc_cap),
		                                'nfc_cap2': str(self.nfc_cap2),
		                                'nfc_hulk': str(self.nfc_hulk),
		                                'nfc_hulk2': str(self.nfc_hulk2)}
		with open('config.ini', 'w') as configfile:
			config_file.write(configfile)

	def hour10_up(self):

		if self.settings_view == 1:

			# # Might not be the best way to do this, with the "now()".
			# # Seems like overkill to get a filled out datetime object
			# datetime.datetime.now().replace(hour=, minute=)

			if self.hr_setting == 0:
				if self.alarm_time_hour <= 14:
					self.alarm_time_hour = self.alarm_time_hour + 10
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(
						2)  # zfill used for padding single digits numbers with a zero
			else:
				if self.alarm_time_hour <= 2:
					self.alarm_time_hour = self.alarm_time_hour + 10
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(
						2)  # zfill used for padding single digits numbers with a zero

	def hour1_up(self):
		if self.settings_view == 1:
			# Convert string time into datetime object
			alarm_time = datetime.datetime.strptime(self.alarm_time, '%H : %M')
			# Add one hour to the datetime object
			hour = (alarm_time + datetime.timedelta(hours=1)).hour
			# Return the datetime object as a "HH : MM" formatted string
			self.alarm_time = alarm_time.replace(hour=hour).strftime('%H : %M')

	def min10_up(self):
		if self.settings_view == 1:
			if self.alarm_time_minute <= (49):
				self.alarm_time_minute = self.alarm_time_minute + 10
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				self.alarm_time_minute = self.alarm_time_minute - 50
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def min1_up(self):
		if self.settings_view == 1:
			if self.alarm_time_minute <= (58):
				self.alarm_time_minute = self.alarm_time_minute + 1
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				self.alarm_time_minute = 0
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def hour10_dn(self):
		if self.settings_view == 1:
			if self.hr_setting == 0:
				if self.alarm_time_hour >= (10):
					self.alarm_time_hour = self.alarm_time_hour - 10
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				if self.alarm_time_hour >= (11):
					self.alarm_time_hour = self.alarm_time_hour - 10
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def hour1_dn(self):
		if self.settings_view == 1:
			if self.hr_setting == 0:
				if self.alarm_time_hour >= (1):
					self.alarm_time_hour = self.alarm_time_hour - 1
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
				else:
					self.alarm_time_hour = 23
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				if self.alarm_time_hour >= (2):
					self.alarm_time_hour = self.alarm_time_hour - 1
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
				else:
					self.alarm_time_hour = 12
					self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def min10_dn(self):
		if self.settings_view == 1:
			if self.alarm_time_minute > (9):
				self.alarm_time_minute = self.alarm_time_minute - 10
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				self.alarm_time_minute = self.alarm_time_minute + 50
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def min1_dn(self):
		if self.settings_view == 1:
			if self.alarm_time_minute >= (1):
				self.alarm_time_minute = self.alarm_time_minute - 1
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
			else:
				self.alarm_time_minute = 59
				self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

	def press_sunday(self, *args):
		if self.set_sunday == '0' and self.settings_view == 1:
			self.set_sunday = '1'
		else:
			if self.set_sunday == '1' and self.settings_view == 1:
				self.set_sunday = '0'

	def press_monday(self, *args):
		if self.set_monday == '0' and self.settings_view == 1:
			self.set_monday = '1'
		else:
			if self.set_monday == '1' and self.settings_view == 1:
				self.set_monday = '0'

	def press_tuesday(self, *args):
		if self.set_tuesday == '0' and self.settings_view == 1:
			self.set_tuesday = '1'
		else:
			if self.set_tuesday == '1' and self.settings_view == 1:
				self.set_tuesday = '0'

	def press_wednesday(self, *args):
		if self.set_wednesday == '0' and self.settings_view == 1:
			self.set_wednesday = '1'
		else:
			if self.set_wednesday == '1' and self.settings_view == 1:
				self.set_wednesday = '0'

	def press_thursday(self, *args):
		if self.set_thursday == '0' and self.settings_view == 1:
			self.set_thursday = '1'
		else:
			if self.set_thursday == '1' and self.settings_view == 1:
				self.set_thursday = '0'

	def press_friday(self, *args):
		if self.set_friday == '0' and self.settings_view == 1:
			self.set_friday = '1'
		else:
			if self.set_friday == '1' and self.settings_view == 1:
				self.set_friday = '0'

	def press_saturday(self, *args):
		if self.set_saturday == '0' and self.settings_view == 1:
			self.set_saturday = '1'
		else:
			if self.set_saturday == '1' and self.settings_view == 1:
				self.set_saturday = '0'

	def vol_change(self, value):
		self.curr_vol = value
		os.system("amixer sset 'Speaker' " + str(self.curr_vol) + "%")


class DigitalClockApp(App):
	def build(self):
		dc = DigitalClock()
		dc.startup()

		return dc


if __name__ == '__main__':
	DigitalClockApp().run()
