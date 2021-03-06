import pygame
from random import shuffle, seed
from keyboard import is_pressed
from time import sleep, time
import sys
# 0, 0 is TOP LEFT FOR BLITTING - REMEMBER
# piece order - 0S, 1Z, 2J, 3L, 4T, 5O, 6I, 7Garbage

class tetromino:
    def __init__(self, tet_type):
        self.type = tet_type
        self.grid, self.pos = self.spawn_tet()
        self.length = len(self.grid)
        self.rotation = 0 #0 is default, 1 is right, 2 is double, 3 is left
        self.ghost_pos = [None, None]

    def spawn_tet(self):
        _tet = self.type
        if _tet == 's':
            grid = [
                [0, 1, 0],
                [1, 1, 0],
                [1, 0, 0]
            ]
            _pos = [3, -2]
        elif _tet == 'z':
            grid = [
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0]
            ]
            _pos = [3, -2] 
        elif _tet == 'j':
            grid = [
                [1, 1, 0],
                [0, 1, 0],
                [0, 1, 0]
            ]
            _pos = [3, -2]
        elif _tet == 'l':
            grid = [
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 0]
            ]
            _pos = [3, -2]
        elif _tet == 't':
            grid = [
                [0, 1, 0],
                [1, 1, 0],
                [0, 1, 0]
            ]
            _pos = [3, -2]
        elif _tet == 'o':
            grid = [
                [1, 1],
                [1, 1]
            ]
            _pos = [4, -2]
        elif _tet == 'i':
            grid = [
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0]
            ]
            _pos = [3, -2]
        return grid, _pos

    def rotate(self, direction):
        new_grid = [x[:] for x in self.grid]
        length = self.length

        if direction == 'left':
            for y in range(length):
                for x in range(length):
                    new_grid[x][length - y - 1] = self.grid[y][x]
        elif direction == 'right':
            for y in range(length):
                for x in range(length):
                    new_grid[length - x - 1][y] = self.grid[y][x]
        elif direction == 'double':
            for y in range(length):
                self.grid[y].reverse()
                new_grid[length - y - 1] = self.grid[y]
        self.grid = [x[:] for x in new_grid]

class playfield:
    def __init__(self, position): #position is top left of field - DOES NOT INCLUDE BORDER
        self.position = position #[64, 0] for now
        self.left_border = 32 * 2
        self.right_border = 32 * 2
        self.lines_left_pos_y = 32 * 4
        self.field = [ [0 for _ in range(20)] for _ in range(10)]
        self.overflow_field = [ [0 for _ in range(20)] for _ in range(10)]

        self.fall_delay = 15 #every 15 frames at 30fps
        self.block_delay = 30
        self.soft_drop_delay = 0 #will fall one block every frame
        
        movement_file = open("settings/DAS ARR.txt", "r")
        self.das = int(movement_file.readline())
        self.arr = int(movement_file.readline())
        
        self.hold_tet = ''

        self.das_timer = self.das
        self.arr_timer = 0
        self.soft_drop_timer = 0 #start soft immediately when pressed
        self.fall_delay_timer = 0 #immediatly drop a space when initiated
        self.above_block_timer = self.block_delay

        self.hold = False
        self.held_already = False
        self.old_presses = []
        self.presses = []
        self.placed_piece = False

        self.next_pieces = []
        self.next_pieces.extend(make_bag())
        self.next_pieces.extend(make_bag())

        self.pieces_placed = 0
        self.lines_left = 40

        screen.fill((60, 60, 60), (position[0] - self.left_border, position[1], self.left_border, 32 * 20))
        screen.fill((60, 60, 60), (position[0] + 32 * 10, position[1], self.right_border, 32 * 20))

        screen.blit(helvetica_big.render(str(self.lines_left), False, (150, 150, 150)), (32 * 14, self.lines_left_pos_y))
    
    def advance_frame(self, presses):
        if self.cur_tetromino.ghost_pos != [None, None]:
            blit_tet(self.cur_tetromino.grid, 'black', self.cur_tetromino.ghost_pos)
        blit_tet(self.cur_tetromino.grid, 'black', self.cur_tetromino.pos)
        self.blit_previews()
        self.old_presses = self.presses[:]
        self.presses = presses
        
    
        for press in presses:
            if press == buttons[4]: #move left
                if self.test_array(offset=[-1, 0]):
                    if press in self.old_presses:
                        if self.das_timer == 0:
                            if self.arr > -1:
                                if self.arr_timer == 0:
                                    self.cur_tetromino.pos[0] -= 1
                                    self.arr_timer = self.arr
                                else:
                                    self.arr_timer -= 1
                            else:
                                while self.test_array(offset=[-1, 0]):
                                    self.cur_tetromino.pos[0] -= 1
                        else:
                            self.das_timer -= 1
                    else:
                        self.cur_tetromino.pos[0] -= 1
                        self.das_timer = self.das
                        self.arr_timer = 0
            elif press == buttons[6]: #move right
                if self.test_array(offset=[1, 0]):
                    if press in self.old_presses:
                        if self.das_timer == 0:
                            if self.arr > -1:
                                if self.arr_timer == 0:
                                    self.cur_tetromino.pos[0] += 1
                                    self.arr_timer = self.arr
                                else:
                                    self.arr_timer -= 1
                            else:
                                while self.test_array(offset=[1, 0]):
                                    self.cur_tetromino.pos[0] += 1
                        else:
                            self.das_timer -= 1
                    else:
                        self.cur_tetromino.pos[0] += 1
                        self.das_timer = self.das
                        self.arr_timer = 0
            elif press == buttons[3]: #soft drop
                if self.soft_drop_timer == 0:
                    self.soft_drop_timer = self.soft_drop_delay
                    if not self.test_array(offset=[0, 1]): #if below are pieces - then place at current pos.
                        if self.above_block_timer <= 0:
                            self.placed_piece = True
                            self.above_block_timer = self.block_delay
                        else:
                            self.above_block_timer -= 1
                    else:
                        blit_tet(self.cur_tetromino.grid, 'black', self.cur_tetromino.pos)
                        self.cur_tetromino.pos[1] += 1
                        self.above_block_timer == self.block_delay
                else:
                    self.soft_drop_timer -= 1
        
            if press not in self.old_presses:
                if press == buttons[1] and not self.held_already: #hold
                    if self.hold_tet != '':
                        self.next_pieces.insert(0, self.hold_tet)
                    self.hold_tet = self.cur_tetromino.type
                    self.held_already = True
                    self.hold = True
                    screen.blit(prev_tet_table[tetrominoes.index(self.hold_tet)], (0,0))
                    break #out of presses loop
                elif press == buttons[0]: #rotate left
                    self.cur_tetromino.rotate('left')
                    if not self.test_array(): #rotates into block - do kick stuff
                        kick = self.test_srs('left')
                        if kick != 0:
                            self.cur_tetromino.pos[0] += kick[0]
                            self.cur_tetromino.pos[1] += kick[1]
                        
                            self.cur_tetromino.rotation = (self.cur_tetromino.rotation - 1) % 4 #can wrap around back to 3
                        else: #kick fails, so rotate back
                            self.cur_tetromino.rotate('right')
                    else:
                        self.cur_tetromino.rotation = (self.cur_tetromino.rotation - 1) % 4
                elif press == buttons[5]: #hard drop
                    self.placed_piece = True
                elif press == buttons[2]: #rotate right
                    self.cur_tetromino.rotate('right')
                    if not self.test_array(): #rotates into block - do kick stuff
                        kick = self.test_srs('right')
                        if kick != 0:
                            self.cur_tetromino.pos[0] += kick[0]
                            self.cur_tetromino.pos[1] += kick[1]
                        
                            self.cur_tetromino.rotation = (self.cur_tetromino.rotation + 1) % 4 #can wrap around back to 0
                        else: #kick fails, so rotate back
                            self.cur_tetromino.rotate('left')
                    else:
                        self.cur_tetromino.rotation = (self.cur_tetromino.rotation + 1) % 4

    

        if not self.placed_piece and buttons[3] not in presses:
            if self.fall_delay_timer > 0:
                self.fall_delay_timer -= 1
            else:
                if not self.test_array(offset=[0, 1]): #if below are pieces - then place at current pos.
                    if self.above_block_timer > 0:
                        self.above_block_timer -= 1
                    else:
                        self.placed_piece = True
                else:
                    self.cur_tetromino.pos[1] += 1
                    self.fall_delay_timer = self.fall_delay
                    self.above_block_timer = self.block_delay

        self.cur_tetromino.ghost_pos = self.find_ghost_pos()
        blit_tet(self.cur_tetromino.grid, self.cur_tetromino.type, self.cur_tetromino.ghost_pos, True)
        blit_tet(self.cur_tetromino.grid, self.cur_tetromino.type, self.cur_tetromino.pos)
        

        if self.hold or self.placed_piece:
            #Congrats you've placed a piece
            
            blit_tet(self.cur_tetromino.grid, 'black', self.cur_tetromino.pos)
    
            if not self.hold:
                self.pieces_placed += 1
                self.test_if_spin()
                
                self.place_piece()
                blit_tet(self.cur_tetromino.grid, self.cur_tetromino.type, self.cur_tetromino.ghost_pos)

                if self.clear_lines(self.cur_tetromino.ghost_pos):
                    if self.lines_left <= 0:
                        self.finish_time = time()
                    self.reblit_field()

            else:
                blit_tet(self.cur_tetromino.grid, 'black', self.cur_tetromino.ghost_pos)
            #reset stuffs
            self.soft_drop_timer = 0
            self.fall_delay_timer = 0
            self.cur_tetromino.rotation = 0
            self.above_block_timer = self.block_delay
            self.placed_piece = False
            
            #spawn new tet
            self.new_piece()

            if not self.hold:
                self.held_already = False
            else:
                self.hold = False

            if not self.test_array(): self.end_game() #end by spawn overlap
            
    def reblit_field(self):
        screen.fill((0, 0, 0), (self.position[0], self.position[1], 32 * 10, 32 * 20))
        for x in range(10):
            for y in range(20):
                if self.field[x][y]:
                    screen.blit(tet_table[self.field[x][y] - 1], (32 * x + self.position[0], 32 * y + self.position[1]))

    def clear_lines(self, coordinates):
        length = self.cur_tetromino.length
        removed_lines = False
        
        for y in range(length):
            line = []
            if 0 <= y + coordinates[1] <= 19:
                for x in range(10):
                    line.append(self.field[x][y + coordinates[1]])
                if 0 not in line:
                    for n in range(10):
                        self.field[n].pop(y + coordinates[1])  
                        self.field[n].insert(0, self.overflow_field[n].pop(19))
                        self.overflow_field[n].insert(0, 0)
                    removed_lines = True
                    self.lines_left -= 1
                    screen.fill((0, 0, 0), (32 * 14, self.lines_left_pos_y, 6 * 32, 2 * 32))
                    screen.blit(helvetica_big.render(str(self.lines_left), False, (150, 150, 150)), (32 * 14, self.lines_left_pos_y))
            elif 0 > y + coordinates[1]:
                for x in range(10):
                    line.append(self.overflow_field[x][y + coordinates[1] + 20])
                if 0 not in line:
                    for n in range(10):
                        self.overflow_field[n].pop(y + coordinates[1] + 20)  
                        self.overflow_field[n].insert(0, 0) #rewrite
                    removed_lines = True
                    self.lines_left -= 1
                    screen.fill((0, 0, 0), (32 * 14, self.lines_left_pos_y, 6 * 32, 2 * 32))
                    screen.blit(helvetica_big.render(str(self.lines_left), False, (150, 150, 150)), (32 * 14, self.lines_left_pos_y))
        return removed_lines

    def place_piece(self): #coords are top left... for now. Imagine aligning top left of grid with coords on field
        grid = self.cur_tetromino.grid
        coordinates = self.cur_tetromino.ghost_pos
        length = self.cur_tetromino.length
        blocks = 0

        for y in range(length):
            for x in range(length):
                if grid[x][y] > 0:
                    blocks += 1
                    if coordinates[1] + y >= 0:
                        self.field[coordinates[0] + x][coordinates[1] + y] = tetrominoes.index(self.cur_tetromino.type) + 1 # +1 because zero is blank in field
                    else:
                        self.overflow_field[coordinates[0] + x][coordinates[1] + y + 20] = tetrominoes.index(self.cur_tetromino.type) + 1
                        blocks -= 1
        if blocks == 0: #placing all blocks in the overflow is an end condition
            self.end_game()

    def new_piece(self):
        self.cur_tetromino = tetromino(self.next_pieces.pop(0))
        if len(self.next_pieces) == 7:
            self.next_pieces.extend(make_bag())

    def blit_previews(self):
        for x in range(5):
            screen.blit(prev_tet_table[tetrominoes.index(self.next_pieces[x])], (self.position[0] + 10 * 32, 64 * x))

    def test_array(self, offset=[0, 0]): #coords are top left... for now. Imagine aligning top left of grid with coords on field
        length = self.cur_tetromino.length
        grid = self.cur_tetromino.grid
        coordinates = [self.cur_tetromino.pos[0] + offset[0], self.cur_tetromino.pos[1] + offset[1]]

        for x in range(length):
            for y in range(length):
                if grid[x][y] == 1:
                    #test for oob or overlapping blocks
                    _x = coordinates[0] + x
                    _y = coordinates[1] + y

                    if _x < 0 or _x > 9 or _y > 19:
                        return False
                    elif _y >= 0:
                        if self.field[_x][_y] > 0:
                            return False
                    else:
                        if self.overflow_field[_x][_y + 20] > 0:
                            return False
        return True

    def test_srs(self, direction):
        
        length = self.cur_tetromino.length
        old_rotation = self.cur_tetromino.rotation
        if direction == 'right':
            new_rotation = (old_rotation + 1) % 4
        elif direction == 'left':
            new_rotation = (old_rotation - 1) % 4
        elif direction == 'double':
            new_rotation = (old_rotation + 2) % 4
        tests = []

        if length == 3: #sztlj
            if old_rotation == 0 or old_rotation == 2:
                if new_rotation == 1: #0>1 or 2>1 
                    tests = [(-1, 0),(-1,-1),( 0,+2),(-1,+2)]
                elif new_rotation == 3:# 0>3 or 2>3
                    tests = [(+1, 0),(+1,-1),( 0,+2),(+1,+2)]
            elif old_rotation == 1:#1>0 or 1>2
                tests = [(+1, 0),(+1,+1),( 0,-2),(+1,-2)]
            elif old_rotation == 3:#3>2 or 3>0
                tests = [(-1, 0),(-1,+1),( 0,-2),(-1,-2)]
        elif length == 4: #i
            if (old_rotation == 0 and new_rotation == 1) or (old_rotation == 3 and new_rotation == 2):
                tests = [(-2, 0),(+1, 0),(-2,+1),(+1,-2)] #0>1 or 3>2
            elif (old_rotation == 1 and new_rotation == 0) or (old_rotation == 2 and new_rotation == 3):
                tests = [(+2, 0),(-1, 0),(+2,-1),(-1,+2)]#1>0 or 2>3
            elif (old_rotation == 1 and new_rotation == 2) or (old_rotation == 0 and new_rotation == 3):
                tests = [(-1, 0),(+2, 0),(-1,-2),(+2,+1)]#1>2 or 0>3
            elif (old_rotation == 2 and new_rotation == 1) or (old_rotation == 3 and new_rotation == 0):
                tests = [(+1, 0),(-2, 0),(+1,+2),(-2,-1)]#2>1 or 3>0
        else: #o - will never happen. O can't spin into a placed block
            print('how you do that!')
        
        for test in tests:
            if self.test_array(offset=test):
                return test
        return 0

    def find_ghost_pos(self):
        grid = self.cur_tetromino.grid
        coordinates = self.cur_tetromino.pos
        
        length = self.cur_tetromino.length
        blocks = []
        smallest_distance = 99
        index = 0
        for x in range(length): # get indexes (indexi?) of all blocks
            for y in range(length):
                if grid[x][y] > 0:
                    blocks.append([x + coordinates[0], y + coordinates[1]])
        
        for block in blocks:
            index = first_non_zero(self.field[block[0]][block[1]+1:])
            if index == None:
                if smallest_distance > 19 - block[1]:
                    smallest_distance = 19 - block[1]
            elif smallest_distance > index:
                smallest_distance = index

        return [coordinates[0], coordinates[1] + smallest_distance]

    def end_game(self):
        pygame.quit()
        sys.exit()

    def test_if_spin(self):
        _tet = self.cur_tetromino.type
        _pos = self.cur_tetromino.pos
        corners = 0
        mobile = False

        if _tet == 't':
            for x in [0, 2]:
                for y in [0, 2]:
                    _x = _pos[0] + x
                    _y = _pos[1] + y
                    if _x > 9 or _x < 0 or _y > 19:
                        corners += 1
                    elif self.field[_x][_y]:
                        corners += 1
            if corners >= 3:
                for i in [-1, 1]:
                    if self.test_array(offset=[0, i]) or self.test_array(offset=[i, 0]): 
                        mobile = True
                        break

                if not mobile:
                    print('T-spin')
                    return True
        return False
        
    def add_garbage(self, num_lines):
        pass

def load_tile_line(filename, tile_length):
    image = pygame.image.load(filename).convert()
    image_width = image.get_size()[0]
    tile_line = []
    tile_num = int(image_width/tile_length)
    for x in range(0, tile_num):
        rect = (x * tile_length, 0, tile_length, tile_length)
        tile_line.append(image.subsurface(rect))
    return tile_line

def make_bag():
    tets = ['s', 'z', 'j', 'l', 't', 'o', 'i']
    shuffle(tets)
    return tets

def blit_tet(grid, tet, coordinates, ghost=False, position=[64, 0]):#coords are top left... for now. Imagine aligning top left of grid with coords on field
    #Maybe make into a field method?
    length = len(grid[0])

    if ghost:
        for y in range(length):
            for x in range(length):
                if grid[x][y] == 1:
                    screen.blit(ghost_tet_table[tetrominoes.index(tet)], (32 * (coordinates[0] + x) + position[0], 32 * (coordinates[1] + y) + position[1]))
    else:  
        for y in range(length):
            for x in range(length):
                if grid[x][y] == 1:
                    screen.blit(tet_table[tetrominoes.index(tet)], (32 * (coordinates[0] + x) + position[0], 32 * (coordinates[1] + y) + position[1]))

def test_for_presses():
    presses = []
    for button in buttons:
        if is_pressed(button):
            presses.append(button)
    if 's' in presses: #put hard drop at end if there - want to process it last.
        del presses[presses.index('s')]
        presses.append('s')
    return presses

def first_non_zero(myList):
    for i, n in enumerate(myList):
        if n != 0:
            return i
    return None

def game_intro():
    screen.fill((0, 0, 0), (32 * 6, 32 * 9, 32 * 4, 32 * 3))
    screen.blit(helvetica_big.render('Ready', True, (150, 150, 150)), (32 * 6, 32 * 9))
    pygame.display.flip()
    sleep(1)
    screen.fill((0, 0, 0), (32 * 6, 32 * 9, 32 * 4, 32 * 3))
    screen.blit(helvetica_big.render('Go', True, (150, 150, 150)), (32 * 6, 32 * 9))
    pygame.display.flip()
    sleep(1)
    screen.fill((0, 0, 0), (32 * 6, 32 * 9, 32 * 4, 32 * 3))

def blit_stats_constants():
    screen.blit(helvetica_small.render("PPS:", False, (150, 150, 150)), (32 * 14, 0))
    screen.blit(helvetica_small.render("Time:", False, (150, 150, 150)), (32 * 14, 44))

def play_game():
    screen.fill((0, 0, 0))
    pygame.display.flip()
    frame = 0
    field = playfield([32 * 2, 0])
    field.blit_previews()
    blit_stats_constants()
    game_intro()
    field.new_piece()
    game_start_time = time()
    while True:
        start = time()
        
        presses = test_for_presses()
        if buttons[7] in presses and time() - game_start_time > 0.1: #reset
            frame = 0
            screen.fill((0, 0, 0))
            field = playfield([32 * 2, 0])
            field.blit_previews()
            blit_stats_constants()
            game_intro()
            field.new_piece()
            game_start_time = time()
            start = time()
            presses = test_for_presses()

        field.advance_frame(presses)

        #Pieces per second and time display
        if (frame - 1) % 30 == 0:
            _time = time() - game_start_time
            screen.fill((0, 0, 0), (32 * 14, 20, 6 * 32, 20))
            screen.blit(helvetica_small.render(str(round(field.pieces_placed / _time, 2)), False, (150, 150, 150)), (32 * 14, 18))
            screen.fill((0, 0, 0), (32 * 14, 64, 6 * 32, 20))
            screen.blit(helvetica_small.render(str(round(_time, 2)), False, (150, 150, 150)), (32 * 14, 64))



        pygame.display.flip()
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if field.lines_left <= 0:
            break

        frame += 1
        sleep(max(0, 0.03333333333 - (time() - start)))

    screen.fill((0, 0, 0))
    screen.blit(helvetica_big.render(str(round(field.finish_time - game_start_time, 4)), True, (150, 150, 150)), (32 * 6, 32 * 9))
    pygame.display.flip()

if __name__=='__main__':
    pygame.init()
    seed(a = None, version = 2)
    helvetica_big = pygame.font.SysFont('Helvetica', 40)
    helvetica_small = pygame.font.SysFont('Helvetica', 20)


    screen_width = 32 * 16
    screen_height = 32 * 20
    screen = pygame.display.set_mode((screen_width, screen_height))

    tet_table = load_tile_line("imgs/blocks32.png", 32)
    ghost_tet_table = load_tile_line("imgs/ghostblocks32.png", 32)
    prev_tet_table = load_tile_line("imgs/prev_blocks16.png", 64)

    tetrominoes = ['s', 'z', 'j', 'l', 't', 'o', 'i', 'garbage', 'black']
    f = open("settings/controls.txt", 'r')
    buttons = []
    for n in range(0, 8):
        buttons.append(f.readline()[0])

    while True:
        play_game()
        while not is_pressed(buttons[7]):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()