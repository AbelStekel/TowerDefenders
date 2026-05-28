import pygame
import time

#DO NOT TOUCH
window_x = 1200
window_y = 1200


#towers
yellow = pygame.Color(255, 255, 0)
white = pygame.Color(255, 255, 255)
grey = pygame.Color(127, 127, 127)
#walls
black = pygame.Color(0, 0, 0)
#grass
green = pygame.Color(0, 255, 0)
#water
blue = pygame.Color(255, 0, 0)
#lava
orange = pygame.Color(255, 165, 0)
#enemies
red = pygame.Color(255, 0, 0)

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
	level_number = 0

	#this is used to give towers and enemies unique identifiers
	#helps figure out if theyre dead or not i guess
	entity_counter = 0

	#this is information about the tower/enemy
	#- name is enemy or tower type (STRING) 					tower/enemy[0]
	#- value decides money gained on sell/buy (INTEGER) 		tower[1]
	#- range is distance tower can see (INTEGER) 				tower[2]
	#- damage is hp dmg done per loop (INTEGER) 				tower[3]
	#- x_pos, y_pos are for tracking enemy/tow er (INTEGER?)	tower/enemy[4]/[5]
	#- ent_id is for lookups (INTEGER)							tower/enemy[6]
	#- hp is damage enemy can take (INTEGER)					enemy[1]
	#- reward decides gold reward on enemy kill (INTEGER)		enemy[2]
	#- speed is units moved per loop (INTEGER)					enemy[3]
	#- upgrades is a value that increments based on purchased upgrades (TBD) tower[7]
	tower_template = ("name", "value", "range", "damage", "x_pos", "y_pos", "entity_id", "upgrades")
	enemy_template = ("name", "hp", "reward", "speed", "x_pos", "y_pos", "entity_id")

	#these lists hold towers or enemies
	tower_list = ()
	enemy_list = ()

	#while alive
	while(hp > 0):
		#refresh screen
		game_window.fill(green)
		#draw_level(level_number)
		#draw_ui()
		draw_enemies(enemy_list)
		draw_towers(tower_list)

		#get inputs
		for event in pygame.event.get():
			if event.type == pygame.QUIT:  
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				#track position[x][y]
				position = pygame.mouse.get_pos()
				#left mouse button
				if event.button == 1:
					#press play button
					if > position[0] >  and > position[1] > :
						if gameplay == False:
							gameplay = True
					#this checks to see if the tower exists at the location
					elif find_tower_by_coordinate(position) >= 0:
						clicked_tower_id  = find_tower_by_coordinate(position)
						#loop thru towers
						for tower in tower_list:
							#if ids match, do stuff
							if clicked_tower_id == tower[6]:
								display_tower = find_towerinfo_by_id(tower[6])
								#do uistuff(display_tower)
								
		#you pressed play. make stuff happen
		if gameplay == True:
			#spawn an enemy per loop
			while enemies_left > 0:
				enemy_list = create_enemy(entity_counter, wave_number, enemy_list)
				enemies_left -= 1

			#you won the wave, do these things
			if len(enemy_list) == 0:
				gameplay = False
				wave_number += 1
				money = money + wave_number * 150

			#check list of towers and enemies
			for tower in tower_list:
				for enemy in enemy_list:
					#enemy reaches out-of-bounds
					#take dmg based on size
					if enemy[4] > window_x and enemy[5] > window_y:
						if enemy[0] == "small":
							hp -= 1
							enemy_list.remove(enemy)
						elif enemy[0] == "medium":
							hp -= 4
							enemy_list.remove(enemy)
						elif enemy[0] == "big":
							hp -= 10
							enemy_list.remove(enemy)
					#check if any enemy in range of any tower
					if (tower[4] - tower[2] < enemy[4] < tower[4] + tower[2]) and (tower[5] - tower[2] < enemy[5] < tower[5] + tower[2]):
						#subtract damage from hp
						enemy[1] -= tower[3]

					#if no hp, enemy dies
					if enemy[1] < 1:
						money += enemy[2]
						kill_amount += 1
						enemy_list.remove(enemy)

					#this should move enemies around or something idk. very basic, needs rework
					enemy[4] += enemy[3]
					enemy[5] += enemy[3]
					#rn this just updates coordinates. could do something to allow more 'cool' track designs?
					#ie every loop, a unit is travelled. speed is a modifier to this value
					#or, every unit a % is travelled with speed modifying
					#how would that hook into level layouts specifically? etc.
	
		# >draw level
		# >draw towers
		# >buy towers ui/menu?
		# 	>tower ideas? castle tower. bow tower. sword tower. knife tower?
		# >take inputs. ie upgrades, level start, selling/placing tower
		# > if enemy in some range -> tower attacks
		# 	> if enemy hp = 0 -> kills + 1, it dies (remove from enemy_list). give money to player
		# > if: level_start -> spawn stuff based on level info
		# 	> if enemy coord > screen or something -> damage
		# > if hp 0 -> death

		fps.tick(24)
		pygame.display.flip()
	#if u got here, it means the game ended. gg
	game_over(wave_number, kill_amount)

#could potentially add wave number to function in order to make special wave-based level behaviour
#def draw_level(level_number):
	#NO LEVELS YET. TESTING ON BIG PLANE. 

#helper function fetches currently active towers
def draw_towers(tower_list):
	for tower in tower_list:
		pygame.draw.rect(game_window, yellow, pygame.Rect(tower[4] - 5, tower[5] - 5, 10, 10))

#function fetches list of currently active enemies to draw them
def draw_enemies(enemy_list):
	for enemy in enemy_list:
		pygame.draw.rect(game_window, red, pygame.Rect(enemy[4] - 5, enemy[5] - 5, 10, 10))

# #helper function to draw play button, tower selection, money, wave number, kill count etc
# def draw_ui(money, kills, wave_number, gameplay):
# 	if gameplay == True:
# 		#draw play button
# 	else:
# 		#draw pause button

#this function helps spawn enemies
#by checking the wave info
def create_enemy(entity_counter, wave_number, enemy_list):
	enemy_data = get_waveinfo(wave_number)
	if enemy_data[0] > 0:
		smallenemy = ("small", "50", "5", "3", "0", "0", entity_counter)
		enemy_list.append(smallenemy)
		entity_counter += 1
	if enemy_data[1] > 0:
		mediumenemy = ("medium", "100", "15", "2", "0", "0", entity_counter)
		enemy_list.append(mediumenemy)
		entity_counter += 1
	if enemy_data[2] > 0:
		bigenemy = ("big", "200", "35", "1", "0", "0", entity_counter)
		enemy_list.append(bigenemy)
		entity_counter += 1
	return enemy_list

#each wave has a unique enemy distribution
def get_waveinfo(wave_number):
	#array structure
	return_value = ["small_enemy_count", "medium_enemy_count", "big_enemy_count"]
	#decide this on a per-level basis
	if wave_number == 1:
		#small enemy amount
		return_value[0] = 5
		#medium enemy amount
		return_value[1] = 2
		#big enemy count
		return_value[1] = 0

	return return_value

#returns entity_id
def find_tower_by_coordinate(x_pos, y_pos, tower_list):
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

#end game
def game_over(wave_number, kill_amount):
	#show some text about the game
	#"u made it to wave x. you got y kills"
	gameover_text = smallfont.render("You made it to wave: " + str(wave_number) + " while getting " + str(kill_amount) + " frags.", True, red)
	gameover_surface = gameover_text.get_rect()
	gameover_surface.midtop = (window_x / 2, window_y / 2)
	game_window.blit(gameover_text, gameover_surface)
	pygame.display.flip

game()