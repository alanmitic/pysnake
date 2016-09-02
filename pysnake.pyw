#!/usr/bin/python3
######################################################################
# File: 	pysnake.pyw
# Author:	Alan Mitic
# Date:		17-APR-2012
# Version:	1.01
######################################################################
# Change History:
# 1.00	Original.
# 1.01  Make compatible with Python 3.2.3
#
from tkinter import *		# Tk GUI classes.
from tkinter.font import *	# Tk Font support functions.
from tkinter.simpledialog import *  # askstring dialog function.
from time import *		# Time support functions.
from random import *		# Random number generator functions.
import string			# Fancy string manipulation class.
import pickle			# Serialise support class.
import os.path			# Get script path name.
import sys			# Get arguments.

# Create full file path name to hi-score file.
def gen_hi_score_file_name():
    full_path = os.path.abspath(sys.argv[0])	# Get script path.
    p = full_path.rfind(".")			# Find the start of the ext.
    ext = full_path[p : len(full_path)]		# Extract extension.
    full_path = full_path.replace(ext, ".hsc") 	# Replace with ".hsc".
    return full_path
    
class game_map(Canvas):
    num_x_blks = 0	# Number of blocks wide.
    num_y_blks = 0	# Number of blocks high.
    blk_size = 0	# Size of each block (pixels).
    width = 0		# Width of play area (pixels).
    height = 0		# Height of play area (pixels).
    BLOCK_ILLEGAL = -1	# Illegal out of bounds block.
    BLOCK_EMPTY = 0	# Empty map entry
    BLOCK_DIR_UP = 1	# Snake direction up map entry.
    BLOCK_DIR_DOWN = 2	# Snake direction down map entry.
    BLOCK_DIR_LEFT = 3	# Snake direction left map entry.
    BLOCK_DIR_RIGHT = 4	# Snake direction right map entry.
    BLOCK_PILL = 5	# Pill map entry.
    map_grid = {}	# Grid of blocks values (dictionary).
    COL_SNAKE = "#00ff00"
    COL_PILL = "#ffff00"
    COL_BKG = ["#2222bb", "#000066"]
    
    # Constructor.
    def __init__(self, num_x_blks, num_y_blks, blk_size):
        # Initialise the member attributes.
        self.num_x_blks = num_x_blks
        self.num_y_blks = num_y_blks
        self.blk_size = blk_size
        self.width = num_x_blks * blk_size
        self.height = num_y_blks * blk_size

        # Call the base constructor.
        Canvas.__init__(self, width=self.width, height=self.height,\
            bg="blue", cursor="box_spiral")
        self.pack(side=LEFT)
        
        # Create p_area_w * p_area_h blocks on the the play area tagging then
        # as "x_y", where x is the x-coord and y is the y-coord.
        self.draw_blocks()
        self.reset()
    
    # Draw all the blocks.
    def draw_blocks(self):
        x = 0
        while x < self.num_x_blks:
            y = 0
            while y < self.num_y_blks:
                x0 = (x * self.blk_size) + 1
                x1 = x0 + self.blk_size
                y0 = (y * self.blk_size) + 1
                y1 = y0 + self.blk_size
                tag_name = str(x) + "_" + str(y)
                self.create_rectangle(x0, y0, x1, y1, tag=tag_name, width=0)
                y+=1
            x+=1
    
    # Reset all the blocks to empties.
    def reset(self):
        x = 0
        while x < self.num_x_blks:
            y = 0
            while y < self.num_y_blks:
                self.set(x, y, self.BLOCK_EMPTY)
                y += 1
            x += 1

    # Set the block entry at (x,y) to specifed value.
    def set(self, x, y, value):
        tag_name = str(x) + "_" + str(y)
        self.map_grid[tag_name] = value
        if value == self.BLOCK_EMPTY:	# Empty background block.
            if (not (x % 2) and not (y % 2)) or  ((x % 2) and (y % 2)):
                self.itemconfigure(tag_name, fill=self.COL_BKG[0])
            else:
                self.itemconfigure(tag_name, fill=self.COL_BKG[1])
        elif value == self.BLOCK_PILL:	# Block containing a pill.
            self.itemconfigure(tag_name, fill=self.COL_PILL)
        else:				# Block containing a snake segment.
            self.itemconfigure(tag_name, fill=self.COL_SNAKE)
        
    # Get the block entry as (x,y).
    def get(self, x, y):
        if x < 0 or x > self.num_x_blks - 1 or \
            y < 0 or y > self.num_y_blks - 1:
            return self.BLOCK_ILLEGAL
        tag_name = str(x) + "_" + str(y)
        return self.map_grid[tag_name]
    
    # Enable title text.
    def enable_title(self):
        fnt1 = Font(family="Courier New", size=10)
        fnt2 = Font(family="Courier New", size=20)
        x = self.num_x_blks * self.blk_size / 2
        y = self.num_y_blks * self.blk_size / 4
        self.create_text(x, y, text="PySnake",\
            font=fnt2, fill="yellow", justify=CENTER, tag="title_text")
        y = self.num_y_blks * self.blk_size * 3 / 4
        self.create_text(x, y, text="Press SPACE to Start!\n\n(c) 2003 Alan Mitic",\
            font=fnt1, fill="yellow", justify=CENTER, tag="title_text")

    # Disable title text.
    def disable_title(self):
        self.delete("title_text")
    
class hi_score_entry:
    score = 0	# The players score.
    name = ""	# The players name.

    # Constructor - Will construct entry with specifed score and name.
    def __init__(self, score, name):
        self.score = score
        self.name = name

    # Return string describing self.
    def __str__(self):
        return str(self.score).zfill(3) + " " + self.name
        
class hi_score_table:
    entries = []	# List of hi-score entries.
    max_num_entries = 0	# Max number of hi_score entries

    # Constructor - Will attempt to load the hi-score.
    def __init__(self, max_num_entries):
        self.max_num_entries = max_num_entries

        # Create the default number of entries.    	
        while max_num_entries:
            self.entries.append(hi_score_entry(0, "A.M"))
            max_num_entries -= 1
    
    # Is supplied score a hi-score (Position or -1 if not hi-score).
    def is_hi_score(self, score):
        # Find index of hi-score which is higher then player score.
        i = self.max_num_entries - 1
        while i != -1:
            if score <= self.entries[i].score:
                break
            i -= 1

        # Adjust index to point to the one below.
        i += 1
    
        # If not inside table return -1 else return index.
        if i == self.max_num_entries:
            return -1
        else:
            return i
        
    # Add score, with name.
    def add_score(self, score, name):
        # Determine the hi-score position.
        pos = self.is_hi_score(score)
        if pos == -1:
            return
        # Remove last entry (lowest score).
        del self.entries[-1]
        # Insert the new score in the correct position.
        self.entries.insert(pos, hi_score_entry(score, name))
    
    # Generate list of all the hi-scores.
    def to_list(self):
        lst = []
        for entry in self.entries:
            lst.append(str(entry))
        return lst

    # Load hi-score file.
    def load(self, file_name):
        try:
            f = open(file_name, 'rb')
            self.max_num_entries = pickle.load(f)	# Number of entries.
            self.entries = pickle.load(f)		# Entries (list).
            f.close()
            return True
        except IOError: # Error opening or reading from file.
            return False
        except TypeError:
            return False
        
    # Save hi-score file.
    def save(self, file_name):
        try:
            f = open(file_name, 'wb')
            pickle.dump(self.max_num_entries, f)	# Number of entries.
            pickle.dump(self.entries, f)		# Entires (list).
            f.close()
            return True
        except IOError: # Error creating or writing to file.
            return False
        except TypeError:
            return False
         
class info_panel(Frame):
    scores = None
    hs_list_box = None

    # Constructor.
    def __init__(self, master=None):
        # Call the Frames constructor.
        Frame.__init__(self, master)
        self.pack(side=RIGHT);
    
        # Create a "Hi-Scores" label above the hi-scores.
        hscrlab = Label(self, text="Hi-Scores")
        hscrlab.pack(side=TOP)
    
        # Create a fixed size font.
        fix_fnt = Font(family="Courier New", size=10, weight=BOLD)

        # Create a list box for the hi-scores.
        self.hs_list_box = Listbox(self)
        self.hs_list_box["font"] = fix_fnt	# Fixed size font.
        self.hs_list_box["width"] = 8		# 8 characters wide.
        self.hs_list_box["bg"] = "yellow"	# Yellow background.
        self.hs_list_box["height"] = 10		# 10 characters high.
        self.hs_list_box.pack(side=RIGHT)	# Pack to the right of the window.
    
        # Create a hi-score table, and update the list box with the scores.
        self.scores = hi_score_table(10)
        self.scores.load(gen_hi_score_file_name())
        self.update()

    # Update the hi score list box with latest scores.
    def update(self):
        self.hs_list_box.delete(0, self.scores.max_num_entries)
        for item in self.scores.to_list():
            self.hs_list_box.insert(END, item)
        
class snake_head:
    # Constructor.
    def __init__(self, x, y):
        self.x = x	# X-Coord.
        self.y = y	# Y-Coord.
        self.d = 0	# Direction.
        
    # To string.
    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.d)
    
class snake_tail:
    # Constructor.
    def __init__(self, x, y):
        self.x = x	# X-Coord.
        self.y = y	# Y-Coord.

    # To string.
    def __str__(self):
        return str(self.x) + " " + str(self.y)
        
class snk_app(Frame):
    version = "1.00"		# Version string.
    play_area = None;		# Game map play area.
    info_pan = None;		# Information panel (hi-score).
    frame_period = 60		# frame period.
    s_head = None		# Snake head.
    s_tail = None		# Snake tail.
    pill_swallowed = False	# Pill swallowed flag.
    score = 0			# Current games score.
    
    # Constructor.
    def __init__(self, master=None):
        # Call the Frames constructor.
        Frame.__init__(self, master)
        
        # Set the title, and disable the user resize option.
        self.update_title()
        self.master.resizable(0, 0)
    
        # Create a canvas for the play area.
        self.play_area = game_map(25,25, 8)
    
        # Create the information panel.
        self.info_pan = info_panel()
    
        # Bind the input keys to call backs.
        self.master.bind("<Key-Up>", self.up_callback)
        self.master.bind("<Key-Down>", self.down_callback)
        self.master.bind("<Key-Left>", self.left_callback)
        self.master.bind("<Key-Right>", self.right_callback)
        self.master.bind("<space>", self.start_callback)
    
        # Set hadndler for catching the window closing.
        self.master.protocol("WM_DELETE_WINDOW", self.quit_pysnake_callback)

        # Call the title logic.
        self.after(0, self.title_logic_callback)
      
    # Start the message loop.
    def start(self):
        self.master.mainloop()
        
    # Window closing, quit application.
    def quit_pysnake_callback(self):
        self.info_pan.scores.save(gen_hi_score_file_name())
        # Don't call self.quit(), instead use destroy, so that
        # we can run from within IDLE editor if we wish.
        self.master.destroy()

    # Start new game, reset all conditions for a new game.
    def start_callback(self, event):
        if self.s_head != None:	# Game in progress, don't restart.
            return
        self.play_area.disable_title()
        self.play_area.reset()

        self.s_head = snake_head(12, 12)
        self.s_head.d = self.play_area.BLOCK_DIR_UP
        self.s_tail = snake_tail(12, 12)

        self.play_area.set(self.s_head.x, self.s_head.y, self.s_head.d)

        self.pill_swallowed = False
        self.create_random_pill()
        self.score = 0
        self.update_title()
        self.after(500, self.game_logic_callback)

    # Up arrow pressed.
    def up_callback(self, event):
        if self.s_head == None or \
            (self.s_head.d == self.play_area.BLOCK_DIR_DOWN and self.score):
            return
        self.s_head.d = self.play_area.BLOCK_DIR_UP

    # Down arrow pressed.
    def down_callback(self, event):
        if self.s_head == None or \
            (self.s_head.d == self.play_area.BLOCK_DIR_UP and self.score):
            return
        self.s_head.d = self.play_area.BLOCK_DIR_DOWN

    # Left arrow pressed.
    def left_callback(self, event):
        if self.s_head == None or \
            (self.s_head.d == self.play_area.BLOCK_DIR_RIGHT and self.score):
            return
        self.s_head.d = self.play_area.BLOCK_DIR_LEFT

    # Right arrow pressed.
    def right_callback(self, event):
        if self.s_head == None or \
            (self.s_head.d == self.play_area.BLOCK_DIR_LEFT and self.score):
            return
        self.s_head.d = self.play_area.BLOCK_DIR_RIGHT
        
    # Update the title.
    def update_title(self):
        self.master.title("PySnake V" + self.version + \
            " : Score " + str(self.score).zfill(3))
    
    # Randomly place a pill in an empty block on the game map.
    def create_random_pill(self):
        empty_found = 0
        while not empty_found:
            x = randint(0, self.play_area.num_x_blks)
            y = randint(0, self.play_area.num_y_blks)
            if self.play_area.get(x, y) == self.play_area.BLOCK_EMPTY:
                empty_found = 1
        self.play_area.set(x, y, self.play_area.BLOCK_PILL)
    
    # Game logic callback, is called by the timer, and its job is to draw a
    # frame of animation in the play area and/or hi-score area.
    def game_logic_callback(self):
        # Get start time.
        start_time = time()

        # UPDATE THE HEAD SECTION.

        # Draw the head in it's old position, leaving a footprint for
        # the tail to follow.
        self.play_area.set(self.s_head.x, self.s_head.y, self.s_head.d)

        # Calculate the new snake head position.
        if self.s_head.d == self.play_area.BLOCK_DIR_UP:
            self.s_head.y -= 1
        elif self.s_head.d == self.play_area.BLOCK_DIR_DOWN:
            self.s_head.y += 1
        elif self.s_head.d == self.play_area.BLOCK_DIR_LEFT:
            self.s_head.x -= 1
        elif self.s_head.d == self.play_area.BLOCK_DIR_RIGHT:
            self.s_head.x += 1

        # Get the value at the new postion.
        m_val = self.play_area.get(self.s_head.x, self.s_head.y)
            
        # Check if a pill has been swallowed.
        if(m_val == self.play_area.BLOCK_PILL):
            self.score += 1
            self.update_title()
            self.pill_swallowed = True
            self.create_random_pill()

        # Check for any collision.
        if(m_val == self.play_area.BLOCK_ILLEGAL or \
            m_val == self.play_area.BLOCK_DIR_UP or \
            m_val == self.play_area.BLOCK_DIR_DOWN or \
            m_val == self.play_area.BLOCK_DIR_LEFT or \
            m_val == self.play_area.BLOCK_DIR_RIGHT):
            self.after(0, self.end_game_logic_callback)
            return

        # Draw the head in it's new position.
        self.play_area.set(self.s_head.x, self.s_head.y, self.s_head.d)

        # UPDATE THE TAIL SECTION.
                
        # Read the direction that the tail will need to go.
        m_val = self.play_area.get(self.s_tail.x, self.s_tail.y)
           
        # If pill has not been swallowed update tail, else to nothing allowing
        # the snake to grow in length.
        if not self.pill_swallowed:
            # Clear the block where the tail currently is.
            self.play_area.set(self.s_tail.x, self.s_tail.y,\
                self.play_area.BLOCK_EMPTY)
            # Calculate the new snake tail position using extracted direction.
            if m_val == self.play_area.BLOCK_DIR_UP:
                self.s_tail.y -= 1
            elif m_val == self.play_area.BLOCK_DIR_DOWN:
                self.s_tail.y += 1
            elif m_val == self.play_area.BLOCK_DIR_LEFT:
                self.s_tail.x -= 1
            elif m_val == self.play_area.BLOCK_DIR_RIGHT:
                self.s_tail.x += 1
                
        # Reset the pill swallowed flag.
        self.pill_swallowed = False
        
        # Get End time.
        end_time = time()
        
        # Calc time delay required to maintain 'frame_period' frame rate,
        # and trigger next frame at that delay.
        delay_time_ms = self.frame_period - ((end_time - start_time) * 1000)
        if delay_time_ms < 0:
            delay_time_ms = 0
        self.after(int(delay_time_ms), self.game_logic_callback)

    # Title sequence logic.
    def title_logic_callback(self):
        # Clear the snakes head and tail.
        self.s_head = None;
        self.s_tail = None;
        # Clear the play area, and display the game title.
        self.play_area.reset()
        self.play_area.enable_title()

    # End game sequence logic.
    def end_game_logic_callback(self):
        # Check the hi-score, and get the players name if needed.
        if self.info_pan.scores.is_hi_score(self.score) != -1:
            # Ask user for initials.
            initials = askstring("New Hi-Score!",\
                "Enter Initials (3 characters max)")
            # If nothing entered default to "...".
            if initials == None:
                initials = "..."
            # Strip the whitespaces.
            initials.strip()
            # Pad with '.'s if not wide enough.
            while len(initials) < 3:
                initials += "."
            # Trim to 3 chars, and make uppercase.
            initials = initials[0:3].upper()
            # Add score and name to hi-score table.
            self.info_pan.scores.add_score(self.score, initials)
            self.info_pan.update()
        
        # Call the title callback after about 1/2 second delay.
        self.after(500, self.title_logic_callback)
    
# Create an instance of the application, and start the
# message processing.
a = snk_app()
a.start()

