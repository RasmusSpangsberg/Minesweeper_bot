# rules for this minesweeper game:
# first square clicked will not have any bombs within adjacent squares

# TODO spam Q and make it work

"""
import urllib.request
import sys
from bs4 import BeautifulSoup
url = "http://minesweeperonline.com"
response = urllib.request.urlopen(url).read()
soup = BeautifulSoup(response, 'html.parser') # .encode(sys.stdout.encoding, errors='replace')
#html = list(soup.children)[3]
#body = list(html.children)
#print(list(body.children))
#print(soup.body.find_all("div", "square blank"))
print(soup.body.table.tr.td.div.find(id="center-column").find(id="game-container").find(id="game").parent)
# div#1_1.square.blank
"""

from random import randint, randrange
import pygame
import time
import timeit

BLACK = (0,0,0)
GREY  = (127, 127, 127)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

pygame.init()
display_width = 800
display_height = 600
game_display = pygame.display.set_mode((display_width, display_height))
clock = pygame.time.Clock()

class Square(object):
	def __init__(self, row, col, value):
		self.row = row
		self.col = col
		self.value = value
		self.side_len = 26

		x_margin = 10
		y_margin = 80
		self.x_pos = self.col*self.side_len + x_margin
		self.y_pos = self.row*self.side_len + y_margin

		self.revealed = False
		self.flagged = False

	def draw(self):
		if not self.revealed:
			pygame.draw.rect(game_display, WHITE, [self.x_pos-1, self.y_pos-1, self.side_len+2, self.side_len+2]) # edge of box
			pygame.draw.rect(game_display, GREY, [self.x_pos, self.y_pos, self.side_len, self.side_len]) # box
			
			if self.flagged:
				pygame.draw.rect(game_display, RED, [self.x_pos+3, self.y_pos, 13, 10]) # flag
				pygame.draw.rect(game_display, WHITE, [self.x_pos+10, self.y_pos+10, 5, 16]) # pole
		else:

			myfont = pygame.font.SysFont("Comic Sans MS", 18)

			myfont = pygame.font.SysFont("Comic Sans MS", 30)

			if self.value == "0":
				surface = myfont.render(" ", False, WHITE)
			else:
				surface = myfont.render(self.value, False, WHITE)

			game_display.blit(surface, (self.x_pos+10, self.y_pos+3))

	def is_clicked(self, mouse_x, mouse_y):
		if mouse_x > self.x_pos and mouse_x < self.x_pos + self.side_len:
			if mouse_y > self.y_pos and mouse_y < self.y_pos + self.side_len:
				return True
		return False

	def reveal(self):
		self.revealed = True
	
	def flagged(self):
		self.flagged = True

class Board(object):
	def __init__(self):
		self.board = []

		for row in range(16):
			self.board.append([])
			for col in range(30):
				square = Square(row, col, "_")
				self.board[row].append(square)

		self.game_started = False
		self.first_click = True
		self.game_exit = False

		self.num_mines = 0
		self.num_squares_not_revealed = 30*16

	def gen_mines(self, first_square_clicked):
		# number of mines in the game
		while(self.num_mines < 99):
			x_pos = randint(0, 15)
			y_pos = randint(0, 29)

			if (self.board[x_pos][y_pos].value != "M") and \
			 (self.board[x_pos][y_pos] not in self.adjacent_squares(first_square_clicked) and \
			 (self.board[x_pos][y_pos] != first_square_clicked)):

				self.board[x_pos][y_pos].value = "M"
				self.num_mines += 1

	# adjacent_not_revealed_squares
	def adjacent_squares(self, square):
		adjacent_squares = []

		for i in range(-1, 2):
			for j in range(-1, 2):
				if not (i == 0 and j == 0):

					if (square.row - i >= 0 and square.col - j >= 0) and (square.row - i <= 15 and square.col - j <= 29):
						if not self.board[square.row-i][square.col-j].revealed:
							adjacent_squares.append(self.board[square.row-i][square.col-j])
					
		return adjacent_squares

	def reveal_adjacent_squares(self, square):
		for adjacent_square in self.adjacent_squares(square):
			if not adjacent_square.revealed and not adjacent_square.flagged:
				adjacent_square.revealed = True
				self.num_squares_not_revealed -= 1

				if adjacent_square.value == "0":
					self.reveal_adjacent_squares(adjacent_square)
				
				if adjacent_square.value == "M" and adjacent_square.flagged:
					return "clicked on mine"
		
	def gen_numbers(self):
		for row in self.board:
			for square in row:
				if square.value == "_":
					adjacent_mines = 0

					for adjacent_square in self.adjacent_squares(square):
						if adjacent_square.value == "M":
							adjacent_mines += 1

					square.value = str(adjacent_mines)

	def gen_board(self, first_square_clicked):
		self.gen_mines(first_square_clicked)
		self.gen_numbers()

	def pretty_print(self):
		for row in self.board:
			for square in row:
				print(square.value, end="")
			print()

	def draw(self):
		for row in self.board:
			for square in row:
				square.draw()
		myfont = pygame.font.SysFont("Comic Sans MS", 30)

		num_mines_string = "Mines: " + str(self.num_mines)
		surface = myfont.render(num_mines_string, False, WHITE)
		game_display.blit(surface, (10, 10))

	def won(self):
		if self.num_squares_not_revealed == 99:
			return True
		else:
			return False

	def lost(self):
		print("clicked on mine")
		self.game_exit = True


	def play(self, left_click, middle_click, right_click, square):
		import time

		if not self.game_started:
			self.start_time = time.time()
			self.game_started = True
					
		if left_click and not square.flagged:
			if self.first_click:
				self.gen_board(square)
				self. first_click = False

			if square.value == "M":
				square.reveal()
				print("You clicked on a mine")
				time.sleep(3)
				self.game_exit = True

			elif square.value == "0" and not square.revealed:
				square.reveal()
				self.num_squares_not_revealed -= 1
				self.reveal_adjacent_squares(square)

			elif not square.revealed:
				square.reveal()
				self.num_squares_not_revealed -= 1

		elif right_click:
			if square.flagged:
				square.flagged = False
				self.num_mines += 1
			else:
				square.flagged = True
				self.num_mines -= 1

		elif middle_click:
			adjacent_squares = self.adjacent_squares(square)
			adjacent_flagged_squares = 0

			for adjacent_square in adjacent_squares:
				if adjacent_square.flagged:
					adjacent_flagged_squares += 1

			if square.revealed and (adjacent_flagged_squares == int(square.value)):
				# found mine
				if self.reveal_adjacent_squares(square) == "clicked on mine":
					square.reveal()
					print("You clicked on a mine")
					time.sleep(3)
					self.game_exit = True
			else:
				print("Not a valid move")

		if self.won():
			time = round(time.time() - self.start_time, 2)
			print("You won! Time:", time, "seconds")
			self.game_exit = True


		else:
			print(self.num_mines, self.num_squares_not_revealed)


class Bot(object):
	def __init__(self, board):
		self.board = board

	def reduced_value(self, square):
		reduced_value = int(square.value)

		for adjacent_square in self.board.adjacent_squares(square):
			if adjacent_square.flagged:
				reduced_value -= 1

		return reduced_value

	# we want to know if there are two squares, where one of them shares all its squares with the other. (but not the other way around)
	# name: shared_not_revealed_squares??
	def shared_squares(self, square1, square2):
		shared_squares = []

		for adjacent_square in self.board.adjacent_squares(square1):
			if adjacent_square in self.board.adjacent_squares(square2):
				shared_squares.append(adjacent_square)

		return shared_squares

	# if the first shares all not revealed with the second, that doesn't mean that the second shares all not revealed with the first
	# TODO new name? 
	# and not flagged

	# DOESN'T WORK PROPERLY -----------------------------------------------------------------
	def shares_all_not_revealed_squares(self, square1, square2):
		
		print("comparing:", square1.value, "and", square2.value)
		# adjacent_not_revealed_and_not_flagged_squares
		adjacent_blank_squares1 = self.board.adjacent_squares(square1)
		adjacent_blank_squares2 = self.board.adjacent_squares(square2)

		for adjacent_blank_square in adjacent_blank_squares1:
			if adjacent_blank_square.flagged:
				adjacent_blank_squares1.remove(adjacent_blank_square)
				print("removing", adjacent_blank_square.value, "from", square1.value)

		for adjacent_blank_square in adjacent_blank_squares2:
			if adjacent_blank_square.flagged:
				adjacent_blank_squares2.remove(adjacent_blank_square)
				print("removing", adjacent_blank_square.value, "from", square2.value)

		if set(adjacent_blank_squares1) < set(adjacent_blank_squares2):
			print("true")
			return True
		print("false")
		return False


		"""
		adjacent_squares1 = self.board.adjacent_squares(square1) 

		for adjacent_square1 in adjacent_squares1:
			if adjacent_square1.flagged:
				adjacent_squares1.remove(adjacent_square1)

		shared_squares = self.shared_squares(square1, square2)

		if all(x in adjacent_squares1 for x in shared_squares) and len(shared_squares) == len(adjacent_squares1):# and all(x in shared_squares for x in adjacent_squares1):
			return True
		else:
			for adjacent_square1, shared_square in zip(adjacent_squares1, shared_squares): # 
				print("adjacent_square1:", adjacent_square1.value)
				print("shared_square:", shared_square.value)
		return False
		"""

	def nearby_number_squares(self, square):
		nearby_number_squares = []

		for i, j in zip([0, 0, 1, -1], [-1, 1, 0, 0]):
			try:
				nearby_number_square = self.board.board[square.row - i][square.col - j]

				if nearby_number_square.value != "M" and nearby_number_square.value != "0":
					nearby_number_squares.append(nearby_number_square)
			except IndexError:
				pass

		return nearby_number_squares

	# make it the x_x_pattern?
	def one_one_pattern(self, square):
		if self.reduced_value(square) == 1:
			nearby_number_squares = self.nearby_number_squares(square)

			print("1")
			for nearby_number_square in nearby_number_squares:
				if self.reduced_value(nearby_number_square) == 1:

					print("2")
					# and not flagged
					if self.shares_all_not_revealed_squares(square, nearby_number_square):
						shared_squares = self.shared_squares(square, nearby_number_square)

						print("3")
						for adjacent_square in self.board.adjacent_squares(nearby_number_square):
							if adjacent_square not in shared_squares:
								left_click = True
								right_click = False
								middle_click = False
								print("4")

								self.board.play(left_click, middle_click, right_click, adjacent_square)

	# DOESN'T WORK
	def one_two_pattern(self, square):
		if self.reduced_value(square) == 1:
			nearby_number_squares = self.nearby_number_squares(square)

			for nearby_number_square in nearby_number_squares:
				if self.reduced_value(nearby_number_square) == 2:
					# and not flagged

					# this needs to be, "if nearby_number_square shares all but one square, with the number1 square"
					#if self.shares_all_not_revealed_squares(square, nearby_number_square):
						#shared_squares = self.shared_squares(square, nearby_number_square)

					shared_squares = self.shared_squares(square, nearby_number_square)
					# mark the bomb that is not shared between squares
					if len(self.board.adjacent_squares(nearby_number_square)) == 3:
						for adjacent_square in self.board.adjacent_squares(nearby_number_square):
							if adjacent_square not in shared_squares:
								left_click = False
								right_click = True
								middle_click = False

								self.board.play(left_click, middle_click, right_click, adjacent_square)
							

	def solve(self):
		if board.first_click:
			for row in self.board.board:
				for square in row:
					if square.is_clicked(412, 273):
						left_click = True
						right_click = False
						middle_click = False
						board.play(left_click, middle_click, right_click, square)
		
		for row in self.board.board:
			for square in row:
				if square.revealed and square.value == "M":
					self.board.lost()

				if square.revealed and square.value != "0":
					adjacent_squares = self.board.adjacent_squares(square)

					if len(adjacent_squares) == int(square.value):
						left_click = False
						right_click = True
						middle_click = False

						for adjacent_square in adjacent_squares:
							if not adjacent_square.flagged: 
								board.play(left_click, middle_click, right_click, adjacent_square)
								print("right click")

					flagged_squares = 0
					for adjacent_square in adjacent_squares:
						if adjacent_square.flagged:
							flagged_squares += 1

					if flagged_squares == int(square.value):
						left_click = True
						right_click = False
						middle_click = False

						for adjacent_square in adjacent_squares:
							if not adjacent_square.flagged:
								board.play(left_click, middle_click, right_click, adjacent_square)
								print("left click")

					
					self.one_one_pattern(square)
					#self.one_two_pattern(square)



board = Board()
first_move = True

while not board.game_exit:
	game_display.fill(BLACK)

	# hold W to solve as fast as possible
	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		if first_move:
			bot = Bot(board)
			first_move = False
		bot.solve()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			board.game_exit = True

		# press Q to solve one step at a time
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				if first_move:
					bot = Bot(board)
					first_move = False

				bot.solve()

		if event.type == pygame.MOUSEBUTTONUP:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			
			left_click = False
			right_click = False
			middle_click = False

			if event.button == 1:
				left_click = True

			elif event.button == 2:
				middle_click = True

			elif event.button == 3:
				right_click = True
			
			for row in board.board:
				for square in row:
					if square.is_clicked(mouse_x, mouse_y):
						if middle_click:
							bot.one_one_pattern(square)

						board.play(left_click, middle_click, right_click, square)

	board.draw()
	pygame.display.update()
	# TODO make it one frame per mouse click, since nothing happens in between
	clock.tick(120)