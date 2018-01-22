import csv
from bs4 import BeautifulSoup 
import requests
from pprint import pprint
import re
import difflib


# Name: Jacob Kreinik
# si 330 Final Project

def map_team_to_record(filename):
	team_records = {}
	with open(filename, 'r') as input_file:
		team_reader = csv.DictReader(input_file)
		for reader in team_reader:
			team_records[reader['Team']] = (reader['Win-Loss Record'], reader['Win %'], reader['MOV'])
	return team_records

def map_team_to_ATS_record(filename):
	team_ATS_records = {}
	with open(filename, 'r') as input_file:
		team_ATS_reader = csv.DictReader(input_file)
		for reader in team_ATS_reader:
			team_ATS_records[reader['Team']] = (reader['ATS Record'], reader['Cover %'], reader['MOV'])
	return team_ATS_records

def clean_team_record_dict(map_team_to_record_dict):
	quantify_season_records = {}
	for x in map_team_to_record_dict.items():
		record_lst = x[1][0].split('-')
		win_perc = x[1][1]
		MOV = float(x[1][2])


		wins = int(record_lst[0])
		losses = int(record_lst[1])
		ties = int(record_lst[2])
		total_games_played = wins + losses + ties
		normalize_win_per = float (win_perc[:-1])

		quantify_season_records[x[0]] = (wins, losses, ties, total_games_played, normalize_win_per, MOV)
	return(quantify_season_records)


def map_team_to_stats(filename):
	team_stats = {}
	with open(filename, 'r') as input_file:
		team_reader = csv.DictReader(input_file)
		for reader in team_reader:
			team_stats[reader['Team']] = reader['2016']
	return team_stats

def get_playoff_teams(record_dict):
	playoff_teams = []
	for x in record_dict.items():
		if x[1][3] > 82: 
			playoff_teams.append(x[0])

	return playoff_teams

def get_non_playoff_teams(record_dict):
	non_playoff_teams = []
	for x in record_dict.items():
		if x[1][3] <= 82: 
			non_playoff_teams.append(x[0])

	return non_playoff_teams

def string_difference(dic1, dic2):
	new_dict = {}
	for x in dic1.items(): 
		for y in dic2.items(): 
			word1 = x[0]
			word2 = y[0] 
			seq=difflib.SequenceMatcher(a=word1.lower(), b=word2.lower()).ratio()
			if seq > 0.57: 
				new_dict[word1] = y[1]
			else: 
				continue
	return new_dict





def main():
	all_games_season_ATS_record = map_team_to_ATS_record('ATS-16-17-records.csv')
	#print (all_games_season_ATS_record)
	all_games_season_ATS_record_clean = clean_team_record_dict(all_games_season_ATS_record) #dictionary mapping team name to ATS metricts in a 6 element tuple. Structure: Team Name:(wins, losses, ties, total games played, win %, MOV)
	#print (all_games_season_ATS_record_clean)

	all_games_season_records = map_team_to_record('winloss-16-17.csv') #dictionary where key is team name and value is a 2 element tuple. First element is record and second is win%
	all_games_season_records_clean = clean_team_record_dict(all_games_season_records)
	#print (all_games_season_records_clean)

	playoff_games_ATS_records = map_team_to_ATS_record('Playoff-ATS-16-17-records.csv')
	#print (playoff_games_ATS_records)
	playoff_games_ATS_records_clean = clean_team_record_dict(playoff_games_ATS_records)
	#print (playoff_games_ATS_records_clean)

	playoff_games_record = map_team_to_record('Playoff-winloss-16-17.csv')
	playoff_games_record_clean = clean_team_record_dict(playoff_games_record)
	#print (playoff_games_record_clean)

	playoff_teams = get_playoff_teams(all_games_season_records_clean)
	# print (playoff_teams)
	# print (len(playoff_teams))
	non_playoff_teams = get_non_playoff_teams(all_games_season_records_clean)
	# print (len(non_playoff_teams)

	turnovers_per_game = map_team_to_stats('Turnovers-per-game-16-17.csv')
	#print (turnovers_per_game)

	rebounds_per_game = map_team_to_stats('Rebounds-per-game-16-17.csv')

	shooting_percentage = map_team_to_stats('Shooting-percentage-16-17.csv')




	#---------------------------------- Second Data Source (Beautiful Soup) --------------------------------
	response = requests.get('https://www.si.com/nba/2016/10/24/nba-power-rankings-preseason-warriors-cavaliers')
	html_response = response.content
	soup = BeautifulSoup(html_response, "lxml")

	team_rank = soup.find_all('strong')#got all the tags that have power ranking and team name.
	team_content = []
	for team in team_rank: #iterates through the tags
		if re.search('[0-9]+.+', str(team.contents)):
			team_content.extend(team.contents) #used extend so the structure was not a list of lists. extracted team name and power ranking
	#print (team_content) #put the contents of the tags into a list. Ex of one element: 30. Brooklyn Nets
	
	#now with a list of team ranking and team name my goal is to map team name to ranking in a dictionary to give the data more structure
	team_to_power_rank = {}
	for rank in team_content: #iterates through list of strings of team and ranking as a single string
		split = re.split('([0-9]+)\. ', rank)#splits by ranking followed by "."
		power_rank = int(split[1]) #captures the ranking portion of the list
		team_name = split[2].strip() #captures team name
		team_to_power_rank[team_name] = power_rank

	sorted_power = sorted(team_to_power_rank.items(), key = lambda x: x[1])

	#--------------------------- editing team names of power rank dictionary ------------

	team_power_ranks = {}
	for x in team_to_power_rank.items():
		if x[0] == 'Golden State Warriors':
			team_power_ranks['Golden State'] = x[1]
		elif x[0] == 'Cleveland Cavaliers':
			team_power_ranks['Cleveland'] = x[1]
		elif x[0] == 'San Antonio Spurs':
			team_power_ranks['San Antonio'] = x[1]
		elif x[0] == 'L.A. Clippers':
			team_power_ranks['LA Clippers'] = x[1]
		elif x[0] == 'Toronto Raptors':
			team_power_ranks['Toronto'] = x[1]
		elif x[0] == 'Boston Celtics':
			team_power_ranks['Boston'] = x[1]
		elif x[0] == 'Portland Trail Blazers':
			team_power_ranks['Portland'] = x[1]
		elif x[0] == 'Utah Jazz':
			team_power_ranks['Utah'] = x[1]
		elif x[0] == 'Oklahoma City Thunder':
			team_power_ranks['Okla City'] = x[1]
		elif x[0] == 'Memphis Grizzlies':
			team_power_ranks['Memphis'] = x[1]
		elif x[0] == 'Atlanta Hawks':
			team_power_ranks['Atlanta'] = x[1]
		elif x[0] == 'Indiana Pacers':
			team_power_ranks['Indiana'] = x[1]
		elif x[0] == 'Charlotte Hornets':
			team_power_ranks['Charlotte'] = x[1]
		elif x[0] == 'Charlotte Hornets':
			team_power_ranks['Charlotte'] = x[1]
		elif x[0] == 'Minnesota Timberwolves':
			team_power_ranks['Minnesota'] = x[1]
		elif x[0] == 'Houston Rockets':
			team_power_ranks['Houston'] = x[1]
		elif x[0] == 'Detroit Pistons':
			team_power_ranks['Detroit'] = x[1]
		elif x[0] == 'Dallas Mavericks':
			team_power_ranks['Dallas'] = x[1]
		elif x[0] == 'Chicago Bulls':
			team_power_ranks['Chicago'] = x[1]
		elif x[0] == 'New York Knicks':
			team_power_ranks['New York'] = x[1]
		elif x[0] == 'Orlando Magic':
			team_power_ranks['Orlando'] = x[1]
		elif x[0] == 'Washington Wizards':
			team_power_ranks['Washington'] = x[1]
		elif x[0] == 'Milwaukee Bucks':
			team_power_ranks['Milwaukee'] = x[1]
		elif x[0] == 'Miami Heat':
			team_power_ranks['Miami'] = x[1]
		elif x[0] == 'New Orleans Pelicans':
			team_power_ranks['New Orleans'] = x[1]
		elif x[0] == 'Denver Nuggets':
			team_power_ranks['Denver'] = x[1]
		elif x[0] == 'Sacramento Kings':
			team_power_ranks['Sacramento'] = x[1]
		elif x[0] == 'Phoenix Suns':
			team_power_ranks['Phoenix'] = x[1]
		elif x[0] == 'Los Angeles Lakers':
			team_power_ranks['LA Lakers'] = x[1]
		elif x[0] == 'Philadelphia 76ers':
			team_power_ranks['Philadelphia'] = x[1]
		elif x[0] == 'Brooklyn Nets':
			team_power_ranks['Brooklyn'] = x[1]


	#print (team_power_ranks)



	#print (sorted_power)

	#print ('\n---------------------------------------------\n')

	mapped_power_rank = string_difference(all_games_season_records_clean, team_to_power_rank)
	sorted_map = sorted(mapped_power_rank.items(), key = lambda x: x[1])
	#print (sorted_map)
	#print (len(mapped_power_rank))

	#With a dictionary of team names and rankings, I need to change the teams to match the teams in the excel files



# --------------------------------- Outout File -----------------------------------------------
	with open('winloss-16-17.csv','r') as input_file:
		record_reader = csv.DictReader(input_file)
		with open('final-team-output.csv','w') as output_file:
			record_writer = csv.DictWriter(output_file,
                                                   fieldnames=['Team','Power-Rank','Total-Record','Total-Win%','MOV','Total-Wins',
                                                   'Total-Losses','Total-ATS-Record','Total-Cover%','Total-ATS-Wins',
                                                   'Total-ATS-Losses','Total-ATS-Ties','Reg-Season-Record','Reg-Season-Wins',
                                                   'Reg-Season-Losses','Reg-Season-Win%','Reg-Season-ATS-Wins',
                                                   'Reg-Season-ATS-Losses','Reg-Season-ATS-Ties','Turnovers-per-game','Rebounds-per-game',
                                                   'Shooting-percentage','Playoff-Team'],
                                                   extrasaction='ignore',delimiter=',',quotechar='"')
			record_writer.writeheader()
			for row in record_reader:
				row['Power-Rank'] = team_power_ranks[row['Team']]
				row['Total-Record'] = all_games_season_records[row['Team']][0]
				row['Total-Win%'] = all_games_season_records[row['Team']][1]
				row['MOV'] = all_games_season_records[row['Team']][2]
				row['Total-Wins'] = all_games_season_records_clean[row['Team']][0]
				row['Total-Losses'] = all_games_season_records_clean[row['Team']][1]
				row['Total-ATS-Record'] = all_games_season_ATS_record[row['Team']][0]
				row['Total-Cover%'] = all_games_season_ATS_record[row['Team']][1]
				row['Total-ATS-Wins'] = all_games_season_ATS_record_clean[row['Team']][0]
				row['Total-ATS-Losses'] = all_games_season_ATS_record_clean[row['Team']][1]
				row['Total-ATS-Ties'] = all_games_season_ATS_record_clean[row['Team']][2]
				row['Turnovers-per-game'] = turnovers_per_game[row['Team']]
				row['Rebounds-per-game'] = rebounds_per_game[row['Team']]
				row['Shooting-percentage'] = shooting_percentage[row['Team']]

				if row['Team'] in playoff_teams:
					row['Reg-Season-Wins'] = all_games_season_records_clean[row['Team']][0] - playoff_games_record_clean[row['Team']][0]
					row['Reg-Season-Losses'] = all_games_season_records_clean[row['Team']][1] - playoff_games_record_clean[row['Team']][1]
					row['Playoff-Team'] = 'Yes'
					row['Reg-Season-Record'] = str(row['Reg-Season-Wins']) + '-' + str(row['Reg-Season-Losses']) + '-' + '0'
					row['Reg-Season-ATS-Wins'] = all_games_season_ATS_record_clean[row['Team']][0] - playoff_games_ATS_records_clean[row['Team']][0]
					row['Reg-Season-ATS-Losses'] = all_games_season_ATS_record_clean[row['Team']][1] - playoff_games_ATS_records_clean[row['Team']][1]
					row['Reg-Season-ATS-Ties'] = all_games_season_ATS_record_clean[row['Team']][2] - playoff_games_ATS_records_clean[row['Team']][2]
				else: 
					row['Reg-Season-Wins'] = all_games_season_records_clean[row['Team']][0]
					row['Reg-Season-Losses'] = all_games_season_records_clean[row['Team']][1]
					row['Playoff-Team'] = 'No'
					row['Reg-Season-Record'] = all_games_season_records[row['Team']][0]
					row['Reg-Season-ATS-Wins'] = all_games_season_ATS_record_clean[row['Team']][0]
					row['Reg-Season-ATS-Losses'] = all_games_season_ATS_record_clean[row['Team']][1]
					row['Reg-Season-ATS-Ties'] = all_games_season_ATS_record_clean[row['Team']][2]
				row['Reg-Season-Win%'] = str(float((row['Reg-Season-Wins']/82)*100)) + '%'

				record_writer.writerow(row)

			
	
	




if __name__ == '__main__':
    main()