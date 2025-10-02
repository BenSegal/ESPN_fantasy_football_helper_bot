# ESPN_fantasy_football_helper_bot
A simple script that monitors your ESPN Fantasy Football team and checks if you should adjust your starters or pickup any new players from waivers.

As someone who does not like ads I stopped using the ESPN Fantasy Football app but this meant that I no longer got notifications when someone on my bench was projected to outperform my starters.

As such - using the help of the ESPN API (https://pypi.org/project/espn-api/) I made a bot to do this for me. 

I run this hourly via the crontab with:
'''
57 * * * * /usr/bin/python3 path/to/file/espn_monitor_team.py
'''

Sample emails I have received that have been really helpful are below:

<img width="694" height="310" alt="image" src="https://github.com/user-attachments/assets/c04d5a8f-0a12-4ad6-ad6c-08b7942f1b22" />

- Bucky Irving is injured and this helped me quickly pickup a new RB from Free Agency. I was notified immediately about the injury which is really convenient.
