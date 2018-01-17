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
			myfont = pygame.font.SysFont("Comic Sans MS", 30)
			if self.value == "0":
				surface = myfont.render(" ", False, WHITE)
			else:
				surface = myfont.render(self.value, False, WHITE)

			game_display.blit(surface, (self.x_pos+10, self.y_pos+3))

	def clicked(self, mouse_x, mouse_y):
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
		while(self.num_mines < 99):
			x_pos = randint(0, 15)
			y_pos = randint(0, 29)

			if (self.board[x_pos][y_pos].value != "M") and \
			 (self.board[x_pos][y_pos] not in self.adjacent_squares(first_square_clicked) and \
			 (self.board[x_pos][y_pos] != first_square_clicked)):

				self.board[x_pos][y_pos].value = "M"
				self.num_mines += 1

	def adjacent_squares(self, square):
		adjacent_squares = []

		for i in range(-1, 2):
			for j in range(-1, 2):
				if not (i == 0 and j == 0):
					try:
						if square.row - i >= 0 and square.col - j >= 0:
							if not self.board[square.row-i][square.col-j].revealed:
								adjacent_squares.append(self.board[square.row-i][square.col-j])
					except IndexError:
						pass 
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
		if self.num_squares_not_revealed == self.num_mines:
			return True
		else:
			return False

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
			else:
				square.flagged = True
				self.num_mines -= 1

		elif middle_click:
			adjacent_squares = self.board.adjacent_squares(square)
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

	def solve(self):
		if board.first_click:
			for row in self.board.board:
				for square in row:
					if square.clicked(412, 273):
						left_click = True
						right_click = False
						middle_click = False
						board.play(left_click, middle_click, right_click, square)
		
		for row in self.board.board:
			for square in row:
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

board = Board()
first_move = True

while not board.game_exit:
	game_display.fill(BLACK)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			board.game_exit = True

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
					if square.clicked(mouse_x, mouse_y):
						board.play(left_click, middle_click, right_click, square)

	board.draw()
	pygame.display.update()
	# TODO make it one frame per mouse click, since nothing happens in between
	clock.tick(120)