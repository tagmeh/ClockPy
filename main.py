#!/bin/python

import os
os.putenv('SDL_AUDIODRIVER', 'alsa')
os.putenv('SDL_AUDIODEV', '/dev/audio')
import time
import datetime
import random
import pygame   # Needs Pygame installed
import io
import sys
import builtins
import traceback
import subprocess
from subprocess import check_output
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config

class DigitalClock(FloatLayout):
    secs_to_next_minute = int(0)
    display_time = StringProperty("00 : 00")
    clock_view = NumericProperty(1)        # Variable to enable view of the Clock Time
    settings_view = NumericProperty(0)     # Variable to enable view of the Settings & Alarm Time
    settings_pic = StringProperty("./Images/Buttons/Settings_Normal.png")
    am_pm_alarm = NumericProperty(0)       # Variable to view AM/PM button in settings when 12hr clock is selected
    is_alarming = NumericProperty(0)       # Track when Alarm is Active
    is_snoozing = NumericProperty(0)       # Track when in Snooze mode
    alarm_saved = open('config.txt', 'r')
    doc_text = alarm_saved.read()
    config_text = str(doc_text.splitlines())
    config_text = str(config_text.replace("'", ""))
    alarm_time_hour = str(config_text.split(",")[0])
    alarm_time_hour = int(alarm_time_hour.split(": ")[1])
    alarm_time_minute = str(config_text.split(",")[1])
    alarm_time_minute = int(alarm_time_minute.split(": ")[1])
    alarm_time = StringProperty(str(alarm_time_hour).zfill(2) + " : " + str(alarm_time_minute).zfill(2))
    set_sunday = str(config_text.split(",")[2])
    set_sunday = StringProperty(set_sunday.split(": ")[1])
    set_monday = str(config_text.split(",")[3])
    set_monday = StringProperty(set_monday.split(": ")[1])
    set_tuesday = str(config_text.split(",")[4])
    set_tuesday = StringProperty(set_tuesday.split(": ")[1])
    set_wednesday = str(config_text.split(",")[5])
    set_wednesday = StringProperty(set_wednesday.split(": ")[1])
    set_thursday = str(config_text.split(",")[6])
    set_thursday = StringProperty(set_thursday.split(": ")[1])
    set_friday = str(config_text.split(",")[7])
    set_friday = StringProperty(set_friday.split(": ")[1])
    set_saturday = str(config_text.split(",")[8])
    set_saturday = StringProperty(set_saturday.split(": ")[1])
    alarm_switch = str(config_text.split(",")[9])# Alarm On/Off Switch
    alarm_switch = NumericProperty(alarm_switch.split(": ")[1])
    hr_setting = str(config_text.split(",")[10])
    hr_setting = NumericProperty(hr_setting.split(": ")[1])
    hr_text = str(config_text.split(",")[11])
    hr_text = StringProperty(hr_text.split(": ")[1])
    am_pm_clock = str(config_text.split(",")[12])        # Enable view for Clock AM/PM label
    am_pm_clock = NumericProperty(am_pm_clock.split(": ")[1])
    am_pm_clock_text = str(config_text.split(",")[13])   # Text for Clock AM/PM label
    am_pm_clock_text = StringProperty(am_pm_clock_text.split(": ")[1])
    am_pm_setting = str(config_text.split(",")[14])   # Switch Alarm between AM/PM when in 12hr Mode
    am_pm_setting = NumericProperty(am_pm_setting.split(": ")[1])
    am_pm_text = str(config_text.split(",")[15])   # Text for Alarm AM/PM Button
    am_pm_text = StringProperty(am_pm_text.split(": ")[1])
    nfc_cap = str(config_text.split(",")[16]) #returned ID Significant Byte for my Captain America figure
    nfc_cap = StringProperty(nfc_cap.split(": ")[1])
    nfc_cap2 = str(config_text.split(",")[17]) #returned ID Significant Byte for my Captain America figure's sticker
    nfc_cap2 = StringProperty(nfc_cap2.split(": ")[1])
    nfc_hulk = str(config_text.split(",")[18]) #returned ID Significant Byte for my Hulk figure
    nfc_hulk = StringProperty(nfc_hulk.split(": ")[1])
    nfc_hulk2 = str(config_text.split(",")[19]) #returned ID Significant Byte for my Hulk figure's sticker
    nfc_hulk2 = StringProperty(nfc_hulk2.split(": ")[1])
    switch_text = str(config_text.split(",")[20])
    switch_text = StringProperty(switch_text.split(": ")[1])
    nfc_read = ''   #Starting empty string for NFC tags
    nfc_checking = 0
    file_played = False
    rando = NumericProperty(0)
    section = NumericProperty(1)            # Section of audio files to use 1=1-7, 2=8-14, 3=15-21
    play_num = NumericProperty(0)
    audio_path = StringProperty("")
    audio_file = StringProperty("")
    colour = NumericProperty(0)
    curr_time = int
    curr_day_name = StringProperty('')
    button_state = StringProperty('normal')
    alarm_event = ()
    pygame.init()


    def update(self, dt=0):
        Clock.unschedule(self.update)    # attempt to fix memory leak - Attempt Successful :)
        if self.hr_setting == 0:
            self.display_time = time.strftime("%H : %M")
        else:
            if self.hr_setting == 12:
                self.display_time = time.strftime("%I : %M")
        self.schedule_update()
        #print('Scheduling Update ', self.schedule_update())

    def schedule_update(self, dt=0):
        self.am_pm_clock_text = time.strftime("%p")
        current_time = time.localtime()
        seconds = current_time[5]
        self.secs_to_next_minute = (60 - seconds)
        self.curr_time = datetime.datetime.now()
        self.curr_day_name = self.curr_time.strftime("%A")
        if ((self.display_time == self.alarm_time) #If alarm time is equal to current time
        and (self.alarm_switch == 1) # and alarm switch is ON
        and (self.is_alarming == 0)):  # and system is currently not in alarm
            if (str(datetime.datetime.today().isoweekday()) == "1" and self.set_monday == '1' #checking current day of week against if it's enabled below
            or  str(datetime.datetime.today().isoweekday()) == "2" and self.set_tuesday == '1'
            or  str(datetime.datetime.today().isoweekday()) == "3" and self.set_wednesday == '1'
            or  str(datetime.datetime.today().isoweekday()) == "4" and self.set_thursday == '1'
            or  str(datetime.datetime.today().isoweekday()) == "5" and self.set_friday == '1'
            or  str(datetime.datetime.today().isoweekday()) == "6" and self.set_saturday == '1'
            or  str(datetime.datetime.today().isoweekday()) == "7" and self.set_sunday == '1'):
                if ((self.hr_setting == 12)
                and (self.am_pm_text == self.am_pm_clock_text)):
                    self.alarm_start()
                else:
                    if (self.hr_setting == 0):
                        self.alarm_start()
        else:
            Clock.schedule_once(self.update, self.secs_to_next_minute) #Update again in 1 minute

    def alarm_start(self, *args):
        self.is_alarming = 1 #put system in alarm mode, this is probably reduntant by this point with as many unschedules and kills I have in the script
        self.settings_pic = "./Images/Buttons/Settings_Normal.png"
        self.settings_view = 0
        self.clock_view = 1
        self.button_state = "normal"
        Clock.schedule_once(self.update, self.secs_to_next_minute) #update again in 1 minute
        self.alarm_loop()

    def alarm_loop(self, *args):
        Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
        self.alarm_event = Clock.schedule_interval(self.alarm_loop, 1) #Reschedule for one second. Doing Clock.schduled_once in 1 second intervals had bad results.
        #print('alarm_loop running')
        self.is_snoozing = 0
        self.am_pm_alarm = 0
        if self.file_played == False:
            self.nfc_list() #Check for NFC tag on alarm.
        if self.is_alarming == 1 and (self.alarm_switch == 1):
            if self.colour == 0:
                self.colour = 1
            else:
                self.colour = 0
            if pygame.mixer.get_busy() == False:  # Check that audio currently isn't running
                self.rando = random.randint(1, 7)   # Random number between 1 and 7, inclusive
                self.play_num = (self.rando) + (self.section) # My files are split into 3 sections, 1-7, 8-14, 15-21 based on natural progression of intensity
                if self.section == 0:   # Increment to next section every round
                    self.section = 7
                else:
                    if self.section == 7:
                        self.section = 14
                    else:
                        self.section = 0
                if (self.nfc_cap in str(self.nfc_read)  # Determine audio file path based on NFC read
                or self.nfc_cap2 in str(self.nfc_read)):  # Determine audio file path based on NFC read
                    self.audio_path = "/home/pi/Desktop/PyClock/Sounds/01-CaptainAmerica/"
                    self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                    #print("Audio File: Cap - " + str(self.audio_file))
                    sound_file = pygame.mixer.Sound(str(self.audio_file)) #Load sound file into Pygame
                    #print(pygame.mixer.Sound)
                    self.file_played = True
                    pygame.mixer.Sound.play(sound_file) # Play sound file
                else:
                    if (self.nfc_hulk in str(self.nfc_read) # Determine audio file path based on NFC read
                    or self.nfc_hulk2 in str(self.nfc_read)):# Determine audio file path based on NFC read
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/02-Hulk/"
                        self.audio_file = (self.audio_path + str(self.play_num) + ".ogg")
                        #print("Audio File: HULK - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        #print(pygame.mixer.Sound)
                        self.file_played = True
                        pygame.mixer.Sound.play(sound_file)
                    else:
                        self.rando = random.randint(1, 2) # Default alarm sounds if no NFC tag is found that matches above
                        self.audio_path = "/home/pi/Desktop/PyClock/Sounds/"
                        self.audio_file = (self.audio_path + str(self.rando) + ".wav")
                        #print("Audio File: Default - " + str(self.audio_file))
                        sound_file = pygame.mixer.Sound(str(self.audio_file))
                        #print(pygame.mixer.Sound)
                        self.file_played = True
                        pygame.mixer.Sound.play(sound_file)
        else:
            self.is_alarming = 0 # Shouldn't need this, but doesn't hurt. Some redundant stuff from def switch_state
            Clock.unschedule(self.alarm_event)

    def snooze_func(self, *args):
        if ((self.is_alarming == 1)
        and (self.is_snoozing == 0)):
            #print('snooze button pressed')
            self.is_snoozing = 1
            Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
            self.alarm_event = Clock.schedule_once(self.alarm_loop, 300) # schedule new 5-minute Snooze timer
            self.colour = 0                         # Set background color to Black
            self.file_played = False                # Reset NFC to try again for tag
            if pygame.mixer.get_busy() == True:     # If sounds is currently playing
                pygame.mixer.stop()                 # Stop currently playing sound

    def cancel_func(self, *args):
        if (self.is_alarming == 1):
            self.is_snoozing = 0
            self.is_alarming = 0
            Clock.unschedule(self.alarm_event)      # unschedule the 1 second loop that runs self.alarm_loop
            self.colour = 0                         # Set background color to Black
            self.file_played = False                # Reset NFC to try again for tag
            if pygame.mixer.get_busy() == True:     # If sounds is currently playing
                pygame.mixer.stop()                 # Stop currently playing sound

    def switch_state(self, *args): # Arm/disarm alarm
        if self.alarm_switch == 0:
            self.alarm_switch = 1
            self.switch_text = "ON"
        else:
            self.alarm_switch = 0            # Toggle switch mode to "Off"
            self.switch_text = "OFF"
            self.cancel_func()                      # Call function to stop alarming
        self.save_config()

    def click_settings(self, *args):
        if self.settings_view == 0:
            self.settings_pic = "./Images/Buttons/Settings_Pushed.png"
            self.settings_view = 1 # See digitalclock.kv for buttons using this variable
            self.clock_view = 0   # See digitalclock.kv for buttons using this variable
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
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2) #zfill used for padding single digits numbers with a zero
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
        config_file = open("config.txt", "w") # Open config.txt file in "Write" mode
        config_file.writelines(
        "0-Alarm Hour: %s\n\
        1-Alarm Minute: %s\n\
        2-Sunday: %s\n\
        3-Monday: %s\n\
        4-Tuesday: %s\n\
        5-Wednesday: %s\n\
        6-Thursday: %s\n\
        7-Friday: %s\n\
        8-Saturday: %s\n\
        9-Alarm Switch: %s\n\
        10-Clock Mode: %s\n\
        11-12hr/24hr Text: %s\n\
        12-View AM/PM Clock Label: %s\n\
        13-Clock AM/PM Label Text: %s\n\
        14-am_pm_setting: %s\n\
        15-am_pm_text: %s\n\
        16-Cap ID: %s\n\
        17-Cap ID2: %s\n\
        18-Hulk ID: %s\n\
        19-Hulk ID2: %s\n\
        20-switch_text: %s\n\
        End Config\n"\
        % (str(self.alarm_time_hour),\
        str(self.alarm_time_minute), \
        str(self.set_sunday), \
        str(self.set_monday), \
        str(self.set_tuesday), \
        str(self.set_wednesday), \
        str(self.set_thursday), \
        str(self.set_friday), \
        str(self.set_saturday), \
        str(self.alarm_switch), \
        str(self.hr_setting), \
        str(self.hr_text), \
        str(self.am_pm_clock), \
        str(self.am_pm_clock_text), \
        str(self.am_pm_setting), \
        str(self.am_pm_text), \
        str(self.nfc_cap), \
        str(self.nfc_cap2), \
        str(self.nfc_hulk), \
        str(self.nfc_hulk2), \
        str(self.switch_text)))    # Write the current alarm time into the file. This can be read later after the app or system reboots.
        config_file.close()

    def hour10_up(self):
        if self.settings_view == 1:
            if self.hr_setting == 0:
                if self.alarm_time_hour <= (14):
                    self.alarm_time_hour = self.alarm_time_hour + 10
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2) #zfill used for padding single digits numbers with a zero
            else:
                if self.alarm_time_hour <= (2):
                    self.alarm_time_hour = self.alarm_time_hour + 10
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2) #zfill used for padding single digits numbers with a zero

    def hour1_up(self):
        if self.settings_view == 1:
            if self.hr_setting == 0:
                if self.alarm_time_hour <= (22):
                    self.alarm_time_hour = self.alarm_time_hour + 1
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
                else:
                    self.alarm_time_hour = 0
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                if self.alarm_time_hour < (12):
                    self.alarm_time_hour = self.alarm_time_hour + 1
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
                else:
                    self.alarm_time_hour = 1
                    self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)

    def min10_up(self):
        if self.settings_view == 1:
            if self.alarm_time_minute <= (49):
                self.alarm_time_minute = self.alarm_time_minute + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_minute = self.alarm_time_minute - 50

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


    def nfc_list(self):
        if ((self.nfc_checking == 0) #Allows only one instance of running the NFC check.
        and (self.file_played == False)):
            self.nfc_checking = 1
            self.nfc_read = ''
            """Grab the entire output of the NFC mobule from the I2C channel."""
            try:    # Run the nfc-poll command and get its output
                self.nfc_read = check_output('nfc-poll', universal_newlines=True) #universal_newlines just makes it easier to read if you decide to Print
            except:
                pass #If there's an error, just move along and try again.
            self.nfc_checking = 0
        else:
            pass



class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':

    DigitalClockApp().run()
