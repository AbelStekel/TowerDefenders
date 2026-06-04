import pygame
import random

#DO NOT TOUCH
window_x = 1000
window_y = 1000
#bottom 250 for UI like shop?

white = pygame.Color(255, 255, 255)
grey = pygame.Color(127, 127, 127)
black = pygame.Color(0, 0, 0)

green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
red = pygame.Color(255, 0, 0)

yellow = pygame.Color(255, 255, 0)
orange = pygame.Color(165, 165, 0)
purple = pygame.Color(128, 0, 128)
#enemy path
brown = pygame.Color(200, 150, 25)

#create stuff
pygame.init()
# pygame.display.set_icon(pygame.image.load('flag.png'))
pygame.display.set_caption('Tower Defender')
game_window = pygame.display.set_mode((window_x, window_y))
bigfont = pygame.font.SysFont('Bahnschrift', 24)
smallfont = pygame.font.SysFont('Bahnschrift', 16)
fps = pygame.time.Clock()

# > select a map? -> maps postponed for now. focus on core gameplay mechanics
# > place a tower. this costs money. tower can be removed/sold
# > start a round -> figure out wave info. scale difficulty. etc
# > enemies come in
# > towers attack enemies
# > survive until wave end
# > damage if enemy reaches end of track. death if hp = 0
# > kills give money
# > upgrade towers? -> TBD. focus elsewhere first

def game():
	#start with full hp and some $$$
	hp = 100
	current_money = 250
	#track kills and wether wave is coming in or not
	kill_amount = 0
	wave_number = 0
	gameplay = False
	# level_number = 0

	#this is used to give towers and enemies unique identifiers
	#helps figure out if theyre dead or not i guess
	entity_counter = 0

	#this is information about the tower/enemy
	#- name is enemy or tower type (STRING) 						tower/enemy[0]
	#- value decides money gained on sell/buy (INTEGER) 			tower[1]
	#- range is distance tower can see (INTEGER) 					tower[2]
	#- damage is hp dmg done per loop (INTEGER) 					tower[3]
	#- x_pos, y_pos are for tracking enemy/tow er (INTEGER?)		tower/enemy[4]/[5]
	#- ent_id is for lookups (INTEGER)								tower/enemy[6]
	#- hp is damage enemy can take (INTEGER)						enemy[1]
	#- reward decides gold reward on enemy kill (INTEGER)			enemy[2]
	#- speed is units moved per loop (INTEGER)						enemy[3]
	#- this field (current_path) is used for figuring out enemy movement		enemy[7]
	#- also store last checkpoint												enemy[8]
	#- upgrades is a value that increments based on purchased upgrades (TBD) 	tower[7]
	tower_template = ["name", "value", "range", "damage", "x_pos", "y_pos", "entity_id", "upgrades"]
	enemy_template = ["name", "hp", "reward", "speed", "x_pos", "y_pos", "entity_id", "current_path", "last_checkpoint"]

	path_this_wave = [("checkpoint index (where length = 1 -> index 1)", "direction", "checkpoint x_pos", "checkpoint y_pos"), ]

	#these lists hold towers or enemies
	tower_list = []
	enemy_list = []

	#id path with this
	path_id = -1

	#while alive
	while(hp > 0):
		#get inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:  
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					if gameplay == False:
						gameplay = True
						new_path = generate_path()
						path_this_wave = new_path[0]
						path_id = new_path[1]
						wave_number += 1
						enemies_left = int(get_waveinfo(wave_number)[0]) + int(get_waveinfo(wave_number)[1]) + int(get_waveinfo(wave_number)[2])
			# if event.type == pygame.MOUSEBUTTONDOWN:
			# 	#track position[x][y]
			# 	position = pygame.mouse.get_pos()
			# 	#left mouse button
			# 	if event.button == 1:
			# 		#press play button
			# 		if > position[0] >  and > position[1] > :
			# 			if gameplay == False:
			# 				gameplay = True
			# 		#this checks to see if the tower exists at the location
			# 		elif find_tower_by_coordinate(position) >= 0:
			# 			clicked_tower_id  = find_tower_by_coordinate(position)
			# 			#loop thru towers
			# 			for tower in tower_list:
			# 				#if ids match, do stuff
			# 				if clicked_tower_id == tower[6]:
			# 					display_tower = find_towerinfo_by_id(tower[6])
			# 					#do uistuff(display_tower)

		#refresh screen
		game_window.fill(green)

		#you pressed play. make stuff happen
		if gameplay == True:
			draw_path(path_id)
			#spawn an enemy per loop
			while enemies_left > 0:
				return_value = create_enemy(entity_counter, wave_number, enemy_list, path_this_wave)
				enemy_list = return_value[0]
				entity_counter += return_value[1]
				enemies_left -= return_value[1]

			#you won the wave, do these things
			if len(enemy_list) == 0:
				gameplay = False
				current_money = current_money + wave_number * 150
			else:
				for enemy in enemy_list:
					#enemy reaches out-of-bounds (4 cases -> each screen edge)
					#take dmg based on size
					if enemy[4] < 0 or enemy[4] > window_x or enemy[5] < 0 or enemy[5] > window_y:
						if enemy[0] == "small":
							hp -= 2
							enemy_list.remove(enemy)
						elif enemy[0] == "medium":
							hp -= 4
							enemy_list.remove(enemy)
						elif enemy[0] == "big":
							hp -= 10
							enemy_list.remove(enemy)

					#check list of towers and enemies
					for tower in tower_list:
						#check if any enemy in range of any tower
						if (tower[4] - tower[2] < enemy[4] < tower[4] + tower[2]) and (tower[5] - tower[2] < enemy[5] < tower[5] + tower[2]):
							#subtract damage from hp
							enemy[1] -= tower[3]

					#if no hp, enemy dies
					if enemy[1] < 1:
						money += enemy[2]
						kill_amount += 1
						enemy_list.remove(enemy)

					#x,y
					#enemy[4], enemy[5]
					#speed = enemy[3]
					#check direction, apply movement
					if enemy[8] == "N":
						enemy[5] = enemy[5] - enemy[3]
					elif enemy[8] == "NE":
						enemy[4] = enemy[4] + enemy[3]
						enemy[5] = enemy[5] - enemy[3]
					elif enemy[8] == "E":
						enemy[4] = enemy[4] + enemy[3]
					elif enemy[8] == "SE":
						enemy[4] = enemy[4] + enemy[3]
						enemy[5] = enemy[5] + enemy[3]
					elif enemy[8] == "S":
						enemy[5] = enemy[5] + enemy[3]
					elif enemy[8] == "SW":
						enemy[4] = enemy[4] - enemy[3]
						enemy[5] = enemy[5] + enemy[3]
					elif enemy[8] == "W":
						enemy[4] = enemy[4] - enemy[3]
					elif enemy[8] == "NW":
						enemy[4] = enemy[4] - enemy[3]
						enemy[5] = enemy[5] - enemy[3]

					#check all predetermined checkpoints
					# offset = 0
					n = 0
					for checkpoint in enemy[7]:
						# debug2_text = smallfont.render(str(checkpoint), True, red) 
						# debug2_surface = debug2_text.get_rect()
						# debug2_surface.midtop = (200 + offset, 500 + offset)
						# game_window.blit(debug2_text, debug2_surface)
						# offset += 15

						#avoid indexing outside of list
						if (n + 1 < len(enemy[7])):
						#if enemy at checkpoint, update direction
							if (checkpoint[2] == enemy[4] and checkpoint[3] == enemy[5]):
								enemy[8] = enemy[7][n + 1][1]
						n += 1

		def debug(enemy_list):
			offset = 0
			for enemy in enemy_list:
				debug1_text = smallfont.render(str(enemy[4]), True, red) 
				debug1_surface = debug1_text.get_rect()
				debug1_surface.midtop = (200 + offset, 0 + offset)
				game_window.blit(debug1_text, debug1_surface)
				offset += 7
		debug(enemy_list)

		if len(enemy_list) > 0:
			draw_enemies(enemy_list)

		if len(tower_list) > 0:
			draw_towers(tower_list)

		#draw hp
		hp_text = smallfont.render("Remaining Health: " + str(hp) + " hp.", True, red)
		hp_surface = hp_text.get_rect()
		hp_surface.midtop = (window_x - 100, 25)
		game_window.blit(hp_text, hp_surface)

		#draw money
		money_text = smallfont.render("$$$: " + str(current_money), True, red)
		money_surface = money_text.get_rect()
		money_surface.midtop = (window_x - 100, 50)
		game_window.blit(money_text, money_surface)

		fps.tick(60)
		pygame.display.flip()

	#if u got here, it means the game ended. gg
	game_over(wave_number, kill_amount)

#helper function fetches currently active towers
def draw_towers(tower_list):
	for tower in tower_list:
		pygame.draw.rect(game_window, yellow, pygame.Rect(int(tower[4]) - 5, int(tower[5]) - 5, 10, 10))

#function fetches list of currently active enemies to draw them
def draw_enemies(enemy_list):
	for enemy in enemy_list:
		if enemy[0] == "small":
			pygame.draw.rect(game_window, blue, pygame.Rect(int(enemy[4]) - 2, int(enemy[5]) - 2, 4, 4))
		elif enemy[0] == "medium":
			pygame.draw.rect(game_window, purple, pygame.Rect(int(enemy[4]) - 3, int(enemy[5]) - 3, 6, 6))			
		elif enemy[0] == "big":
			pygame.draw.rect(game_window, red, pygame.Rect(int(enemy[4]) - 5, int(enemy[5]) - 5, 10, 10))

# #helper function to draw play button, tower selection, money, wave number, kill count etc
# def draw_ui(money, kills, wave_number, gameplay):
# 	if gameplay == True:
# 		#draw play button
# 	else:
# 		#draw pause button

#this function helps spawn enemies
#by checking the wave info
def create_enemy(entity_counter, wave_number, enemy_list, path_this_wave):
	enemy_data = []
	enemy_data = get_waveinfo(wave_number)
	int ;spawned_count = 0

	while enemy_data[0] > 0 or enemy_data[1] > 0 or enemy_data[2] > 0:
		if enemy_data[0] > 0:
			smallenemy = ["small", 15, 5, 3, 0, 0, entity_counter, path_this_wave, path_this_wave[0][1]]
			enemy_list.append(smallenemy)
			spawned_count += 1
			enemy_data[0] -= 1
		if enemy_data[1] > 0:
			mediumenemy = ["medium", 30, 15, 2, 0, 0, entity_counter, path_this_wave, path_this_wave[0][1]]
			enemy_list.append(mediumenemy)
			spawned_count += 1
			enemy_data[1] -= 1
		if enemy_data[2] > 0:
			bigenemy = ["big", 200, 55, 1, 0, 0, entity_counter, path_this_wave, path_this_wave[0][1]]
			enemy_list.append(bigenemy)
			spawned_count += 1
			enemy_data[2] -= 1

	return_value = (enemy_list, spawned_count)
	return return_value

#each wave has a unique enemy distribution
def get_waveinfo(wave_number):
	#array structure
	return_value = ["small_enemy_count", "medium_enemy_count", "big_enemy_count"]
	#decide this on a per-level basis
	if wave_number == 1:
		#small enemy amount
		return_value[0] = 3
		#medium enemy amount
		return_value[1] = 2
		#big enemy count
		return_value[2] = 1
	elif wave_number == 2:
		#small enemy amount
		return_value[0] = 10
		#medium enemy amount
		return_value[1] = 5
		#big enemy count
		return_value[2] = 1
	elif wave_number == 3:
		#small enemy amount
		return_value[0] = 5
		#medium enemy amount
		return_value[1] = 10
		#big enemy count
		return_value[2] = 2
	elif wave_number == 4:
		#small enemy amount
		return_value[0] = 20
		#medium enemy amount
		return_value[1] = 10
		#big enemy count
		return_value[2] = 5
	elif wave_number == 5:
		#small enemy amount
		return_value[0] = 50
		#medium enemy amount
		return_value[1] = 25
		#big enemy count
		return_value[2] = 15
	return return_value

#returns entity_id
def find_towerid_by_coordinate(x_pos, y_pos, tower_list):
	#loop thru all towers
	for tower in tower_list:
		#match coords
		if tower[4] == x_pos and tower[5] == y_pos:
			return tower[6]
	#if this is reached, error code. check for this
	return -1

#helps show what upgrades have been purchased/are available
def find_towerinfo_by_id(entity_id, tower_list):
	#loop thru list, looking for matches
	for tower in tower_list:
		if entity_id == tower[6]:
			return tower
	#no tower with id
	return -1

#layouts to be generated semi-randomly at wave start
def generate_path():
	path_information = [("checkpoint index (where length = 1 -> index 1)", "direction", "checkpoint x_pos", "checkpoint y_pos"),]
	epicrandomnumber = random.randint(0, 4)
	#design 5 levels. here is one (worked out on paper)
	if epicrandomnumber < 5:
		id = 0
		path_information = [
		(1, "E", 300, 0),
		(2, "S", 300, 300), 
		(3, "SE", 450, 450), 
		(4, "E", 600, 450), 
		(5, "NE", 750, 300), 
		(6, "N", 750, 150), 
		(7, "E", 900, 150), 
		(8, "S", 900, 300), 
		(9, "SW", 750, 600), 
		(10, "W", 600, 600),
		(11, "W", 450, 600)
		]
		#due to a quirk in the code, u have to end on 2x the same direction
	return (path_information, id)

#use the id from the generated path (function above)
#draw path (a path is just a collection of rectangles/lines)
def draw_path(path_id):
	if path_id == 0:
		pygame.draw.rect(game_window, brown, pygame.Rect(0, 0, 315, 15))
		pygame.draw.rect(game_window, brown, pygame.Rect(285, 0, 30, 300))
		pygame.draw.line(game_window, brown, (300, 300), (463, 463), 30)
		pygame.draw.rect(game_window, brown, pygame.Rect(450, 435, 150, 30))
		pygame.draw.line(game_window, brown, (585, 464), (749, 300), 30)
		pygame.draw.rect(game_window, brown, pygame.Rect(735, 135, 30, 165))
		pygame.draw.rect(game_window, brown, pygame.Rect(735, 135, 180, 30))
		pygame.draw.rect(game_window, brown, pygame.Rect(885, 135, 30, 165))
		pygame.draw.line(game_window, brown, (587, 614), (899, 299), 30)
		pygame.draw.rect(game_window, brown, pygame.Rect(0, 585, 600, 30))
	# elif path_id == 1:

	# elif path_id == 2:
	
	# elif path_id == 3:
	
	# elif path_id == 4:

#end game
def game_over(wave_number, kill_amount):
	#show some text about the game
	#"u made it to wave x. you got y kills"
	gameover_text = smallfont.render("You made it to wave: " + str(wave_number) + " while getting " + str(kill_amount) + " frags.", True, red)
	gameover_surface = gameover_text.get_rect()
	gameover_surface.midtop = (window_x / 2, window_y / 2)
	game_window.blit(gameover_text, gameover_surface)
	pygame.display.flip()

game()