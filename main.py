#!/bin/python

import time
import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.graphics import *



class DigitalClock(FloatLayout):
    display_time = StringProperty("00 : 00")
    alarm_time = StringProperty("00 : 00")
    clock_view = StringProperty("1")
    settings_view = StringProperty("0")
    clock_disable = StringProperty("0")
    settings_disabled = StringProperty("1")


    def update(self, dt=0):
        self.display_time = time.strftime("%H : %M")
        self.schedule_update()


    def schedule_update(self):
        current_time = time.localtime()
        seconds = current_time[5]

        # Handle leap seconds?
        secs_to_next_minute = 60 - seconds

        Clock.schedule_once(self.update, secs_to_next_minute)


    def click_settings(self, *args):
        if args[1] == 'down':
            self.settings_view = "1"
            self.settings_disabled = "0"
            self.clock_disable = '1'
            self.clock_view = "0"
            print("clock disabled: " + self.clock_disable)
            print("settings  disabled: " + self.settings_disabled)
            self.update()

        else:
            self.settings_disabled = "1"
            self.settings_view = "0"
            self.clock_disable = "0"
            self.clock_view = "1"
            print("clock disalbed: " + self.clock_disable)
            print("settings  disabled: " + self.settings_disabled)


    def switch_state(self, *args):
        if args[1] == True:
            print("Alarm On")
        else:
            print("Alarm Off")

    def hour10_up(self):
        print("Hour 10 Up")

    def hour1_up(self):
        print("Hour 1 Up")

    def min10_up(self):
        print("Min 10 Up")

    def min1_up(self):
        print("Min 1 Up")

    def hour10_dn(self):
        print("Hour 10 Down")

    def hour1_dn(self):
        print("Hour 1 Down")

    def min10_dn(self):
        print("Minute 10 Down")

    def min1_dn(self):
        print("Minute 1 Down")





class DigitalClockApp(App):
    def build(self):
        dc = DigitalClock()
        dc.update()

        return dc


if __name__ == '__main__':
    DigitalClockApp().run()
