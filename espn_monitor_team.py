from espn_api.football import League
from email.mime.text import MIMEText
import smtplib
import csv
import sys
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

league = League(league_id=config['league_info']['league_id'],year=2025,espn_s2=config['league_info']['espn_s2'],swid=config['league_info']['swid'])

cur_week = league.current_week

my_team = league.get_team_data(team_id=7)
my_players = my_team.roster

bench = []
starters = []
starter_counts = {}
for player in my_players:
    if player.lineupSlot in ('BE','IR'):
        bench.append(player)
    else:
        starters.append(player)
        slot = player.lineupSlot
        slot = 'DST' if slot == 'D/ST' else slot
        starter_counts[slot] = starter_counts.get(slot,0) + 1

lowest = {}
lowest_name = {}
lowest_position = {}
for player in starters:        
    if cur_week in player.stats and 'points' in player.stats[cur_week]:
        continue
    slot = player.lineupSlot
    proj_points = player.stats[cur_week]['projected_points'] if cur_week in player.stats else 0
    if slot == 'D/ST':
        slot = 'DST'
    if slot not in lowest:
        lowest[slot] = proj_points
        lowest_name[slot] = player.name
        lowest_position[slot] = player.position
    else:
        if player.stats[cur_week]['projected_points'] < lowest[slot]:
            lowest[slot] = proj_points
            lowest_name[slot] = player.name    
            lowest_position[slot] = player.position        

def find_top_players(players):
    highest = {}
    highest_name = {}
    for player in players:
        if cur_week not in player.stats or 'points' in player.stats[cur_week]:
            continue
        position = player.position
        if position == 'D/ST':
            position = 'DST'
        if position not in highest:
            highest[position] = player.stats[cur_week]['projected_points']
            highest_name[position] = player.name
        else:
            if player.stats[cur_week]['projected_points'] > highest[position]:
                highest[position] = player.stats[cur_week]['projected_points']
                highest_name[position] = player.name
    return highest, highest_name

highest, highest_name = find_top_players(bench)

rows = []

def find_best_in_slot(slot):
    best = 0
    best_name = ''
    best_position = ''
    if slot == 'D/ST':
        slot = 'DST'
    for position in slot.split('/'):
        high = highest.get(position,0)
        if high > best:
            best = high
            best_name = highest_name[position]
            best_position = position
    return best,best_name,best_position

expected_starters = {'WR': 2, 'K': 2, 'QB': 1, 'RB': 2, 'DST': 1, 'RB/WR/TE': 1, 'TE': 1}
for slot in expected_starters:
    expected_count = expected_starters[slot]
    actual_count = starter_counts.get(slot,0)
    if actual_count != expected_count:
        best,best_name,best_position = find_best_in_slot(slot)
        rows.append(f'You are missing in the {slot} slot. You have {actual_count} you need {expected_count}. You should swap in {best_name} {best_position} he is expected to have {best} points')

for slot in ['WR','K','QB','RB','TE','DST','RB/WR/TE']:
    if slot not in lowest:
        continue
    low = lowest[slot]
    best,best_name,best_position = find_best_in_slot(slot)
    if best > low:
        rows.append(f'Currently in {slot} you are starting {lowest_name[slot]} {lowest_position[slot]}. You should swap in {best_name} {best_position} instead. Points comparison is {best} to {low}')
                
players = [player for player in league.free_agents(size=10000)]
highest, highest_name = find_top_players(players)

for slot in expected_starters:
    expected_count = expected_starters[slot]
    actual_count = starter_counts.get(slot,0)
    if actual_count != expected_count:
        best,best_name,best_position = find_best_in_slot(slot)
        rows.append(f'You are missing in the {slot} slot. You have {actual_count} you need {expected_count}. You should pickup {best_name} {best_position}. he is expected to have {best} points')

for slot in ['WR','K','QB','RB','TE','DST','RB/WR/TE']:
    if slot not in lowest:
        continue
    low = lowest[slot]
    best,best_name,best_position = find_best_in_slot(slot)
    if best > low:
        rows.append(f'Currently in {slot} you are starting {lowest_name[slot]} {lowest_position[slot]}. You should pickup {best_name} {best_position} instead. Points comparison is {best} to {low}')

try:
    with open('email_txt.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows_old = next(reader)
except:
    rows_old = []

with open('email_txt.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(rows)

if not rows:
    sys.exit('No actions needed. Empty email')

if rows == rows_old:
    sys.exit('No actions needed. Same email as last time')

sender_email = config['email_info']['sender_email']
sender_password = config['email_info']['sender_password']
recipient_email = config['email_info']['recipient_email']
subject = "Fantasy Football Alert!!"
body = """
<html>
  <body>"""
for row in rows:
    body = body + '<p> ' + row + '</p>'
body += """
  </body>
</html>
"""
html_message = MIMEText(body, 'html')
html_message['Subject'] = subject
html_message['From'] = sender_email
html_message['To'] = recipient_email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
   server.login(sender_email, sender_password)
   server.sendmail(sender_email, recipient_email, html_message.as_string())
