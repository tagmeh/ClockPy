#!/bin/python

import time
import os
import datetime
import random
import pyglet
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout





class DigitalClock(FloatLayout):
    display_time = StringProperty("00 : 00")
    alarm_time_hour = NumericProperty(00)
    alarm_time_minute = NumericProperty(00)
    clock_view = StringProperty("1")
    settings_view = StringProperty("0")
    alarm_time = StringProperty("00 : 00")
    alarm_mode = NumericProperty(0)
    alarm_state = NumericProperty(0)
    nfc_read = ListProperty()
    rando = NumericProperty(0)
    pyglet.lib.load_library('avbin')
    pyglet.have_avbin = True


    def update(self, dt=0):
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()


    def schedule_update(self):
        current_time = time.localtime()
        seconds = current_time[5]

        # Handle leap seconds?
        secs_to_next_minute = 60 - seconds

        Clock.schedule_once(self.update, secs_to_next_minute)

        # Activating the alarm
        print("Alarm Mode: " + str(self.alarm_mode))
        if (self.display_time == self.alarm_time) and (self.alarm_mode == 1):
            self.alarm_state = 1
            print("!!ALARM!!")
            self.rando = random.randint(1,7)
            print("Random Num: " + str(self.rando))


            ###### THIS PATH NEEDS TO CHANGE BASED ON UID READ FROM NFC / AND CHANGE FURTHER ONCE ON THE RASPPI ######

            #self.music = pyglet.media.load("C:/Users/tate.justin/AppData/Local/Programs/Python/Python36-32/PiClock/KivyDigitalClock-master/KivyDigitalClock-master/Sounds/01-CaptainAmerica/" + str(self.rando) + ".ogg", streaming=False)
            #if music:
            #    print("Sound found at %s" % sound.source)
            #    print("Sound is %.3f seconds" % sound.length)
            #    music.play()

    def snooze_mode(self): #snooze for 4 minutes
        if self.alarm_state == 1:

            Clock.schedule_once(self.update, 240)
            if music == False:
                pass #####


    def click_settings(self, *args):
        if args[1] == 'down':
            self.settings_view = "1"
            self.clock_view = "0"
            print("clock enabled: " + self.clock_view)
            print("settings enabled: " + self.settings_view)
            self.update()  # Used for testing only - Comment out after

        else:
            self.settings_view = "0"
            self.clock_view = "1"
            print("clock enabled: " + self.clock_view)
            print("settings enabled: " + self.settings_view)
            self.update()  # Used for testing only - Comment out after

    def switch_state(self, *args):
        if args[1] == True:
            self.alarm_mode = 1
            print("Alarm On: " + str(self.alarm_mode))
        else:
            self.alarm_mode = 0
            self.alarm_state = 0
            print("Alarm Off: " + str(self.alarm_mode))

    def hour10_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (14):
                self.alarm_time_hour = self.alarm_time_hour + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def hour1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_hour <= (23):
                self.alarm_time_hour = self.alarm_time_hour + 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_hour = 0

    def min10_up(self):
        if self.settings_view == "1":
            if self.alarm_time_minute <= (49):
                self.alarm_time_minute = self.alarm_time_minute + 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def min1_up(self):
        if self.settings_view == "1":
            if self.alarm_time_minute <= (58):
                self.alarm_time_minute = self.alarm_time_minute + 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_minute = 0

    def hour10_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_hour >= (10):
                self.alarm_time_hour = self.alarm_time_hour - 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def hour1_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_hour >= (1):
                self.alarm_time_hour = self.alarm_time_hour - 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_hour = 24

    def min10_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_minute >= (10):
                self.alarm_time_minute = self.alarm_time_minute - 10
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                pass

    def min1_dn(self):
        if self.settings_view == "1":
            if self.alarm_time_minute >= (1):
                self.alarm_time_minute = self.alarm_time_minute - 1
                self.alarm_time = str(self.alarm_time_hour).zfill(2) + " : " + str(self.alarm_time_minute).zfill(2)
            else:
                self.alarm_time_minute = 59





class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':
    DigitalClockApp().run()
