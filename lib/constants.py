import os


"""
The home of any variable that should never change or be overwritten
"""

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # ~/ClockPy/
FILES = os.path.join(ROOT, 'files')  # ~/ClockPy/files/

DEFAULT_CONFIG = '''[Alarm Time]
alarm_time_minute = 20
alarm_time_hour = 4

[Alarm Days]
set_friday = 0
set_tuesday = 0
set_sunday = 0
set_wednesday = 0
set_saturday = 0
set_monday = 0
set_thursday = 0

[Miscellaneous]
hr_text = 12HR
switch_text = ON
am_pm_clock_text = PM
hr_setting = 12.0
am_pm_clock = 1.0
am_pm_setting = 1.0
am_pm_text = PM
alarm_switch = 1.0

[Character IDs]
nfc_cap2 = xb9
nfc_hulk = 48
nfc_hulk2 = 48
nfc_cap = 3e
'''
