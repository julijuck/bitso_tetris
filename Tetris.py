
""" 
Bitso Tetris - Developed by @julian_colombo

Version: 1.0
Description:
Classic Tetris clone built with Pygane, featuring Bitso branding,
local leaderboard, game states, scoring, levels, and pause functionality.
"""


import sys
import random
import pygame


# === Constants ===
# Constant for high score file
RECORD_FILE = "record.txt"

# Inicializar pygame
pygame.init()

# Prepare space for logo
logo_bitso = pygame.image.load("bitso_logo.png")
logo_bitso = pygame.transform.scale(logo_bitso, (60, 60))

CONFIG = {
    "WINDOW_WIDTH": 560,
    "WINDOW_HEIGHT": 680,
    "CELL_SIZE": 30,
    "COLUMNS": 10,
    "ROWS": 20,
    "FPS": 60,
    "INITIAL_FALL_DELAY": 500,
    "FAST_DROP_SPEED": 50,
    "LATERAL_SPEED": 150,
}

PANEL_X = 330  # Panel X position for info display

# === Utility Functions ===
def load_high_score():
    """Reads the high score from the RECORD_FILE."""
    try:
        with open(RECORD_FILE, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# === Global Variables ===
current_piece = None
current_color = None
current_rotation = 0
piece_x = 0
piece_y = 0
score = 0
level = 1
last_left_move_time = 0
last_right_move_time = 0
next_piece, next_color = None, None  # Next piece and color
total_lines = 0  # Total lines cleared to increase level
game_state = "playing"
is_paused = False
high_score = load_high_score()
start_time = pygame.time.get_ticks()

# === Pieces and Colors ===
PIECES = [
    # I
    [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    # O
    [
        [[1, 1],
         [1, 1]]
    ],
    # T
    [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    # S
    [
        [[0, 1, 1],
         [1, 1, 0]],
        [[1, 0],
         [1, 1],
         [0, 1]]
    ],
    # Z
    [
        [[1, 1, 0],
         [0, 1, 1]],
        [[0, 1],
         [1, 1],
         [1, 0]]
    ],
    # J
    [
        [[1, 0, 0],
         [1, 1, 1]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    # L
    [
        [[0, 0, 1],
         [1, 1, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ]
]


COLORS = [
    (34, 221, 145),  # Bitso green main
    (20, 180, 120),  # Darker green
    (70, 240, 180),  # Aqua green
    (50, 200, 130),  # Medium green
    (60, 160, 120),  # Moss green
    (90, 255, 190),  # Light green
    (0, 100, 80)     # Deep dark green
]

# === Pygame Window and Board ===
window = pygame.display.set_mode((
    CONFIG["WINDOW_WIDTH"],
    CONFIG["WINDOW_HEIGHT"]
))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

# Create the board as a 2D list of black cells
board = [
    [(0, 0, 0) for _ in range(CONFIG["COLUMNS"])]
    for _ in range(CONFIG["ROWS"])
]

# === Drawing Functions ===
def draw_board():
    """Draws the Tetris board and cell grid."""
    for row in range(CONFIG["ROWS"]):
        for col in range(CONFIG["COLUMNS"]):
            color = board[row][col]
            pygame.draw.rect(
                window,
                color,
                (
                    col * CONFIG["CELL_SIZE"],
                    row * CONFIG["CELL_SIZE"] + 60,
                    CONFIG["CELL_SIZE"],
                    CONFIG["CELL_SIZE"]
                )
            )
            # Draw cell border
            pygame.draw.rect(
                window,
                (80, 80, 80),
                (
                    col * CONFIG["CELL_SIZE"],
                    row * CONFIG["CELL_SIZE"] + 60,
                    CONFIG["CELL_SIZE"],
                    CONFIG["CELL_SIZE"]
                ),
                1
            )

def draw_piece(piece, rotation, piece_x, piece_y, color):
    """Draws the current piece at its board position."""
    shape = piece[rotation]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == 1:
                x = (piece_x + j) * CONFIG["CELL_SIZE"]
                y = (piece_y + i) * CONFIG["CELL_SIZE"] + 60
                pygame.draw.rect(
                    window,
                    color,
                    (
                        x, y,
                        CONFIG["CELL_SIZE"],
                        CONFIG["CELL_SIZE"]
                    )
                )
                pygame.draw.rect(
                    window,
                    (80, 80, 80),
                    (
                        x, y,
                        CONFIG["CELL_SIZE"],
                        CONFIG["CELL_SIZE"]
                    ),
                    1
                )

# === Game Logic Functions ===
def new_piece():
    """Returns a random piece and its color."""
    index = random.randint(0, len(PIECES) - 1)
    return PIECES[index], COLORS[index]

def add_piece_to_board(piece, rotation, piece_x, piece_y, board, color):
    """Locks the current piece into the board."""
    shape = piece[rotation]
    for i, row in enumerate(shape):
        for j, value in enumerate(row):
            if value == 1:
                board_row = piece_y + i
                board_col = piece_x + j
                # Place piece if inside the board
                if (
                    0 <= board_row < CONFIG["ROWS"] and
                    0 <= board_col < CONFIG["COLUMNS"]
                ):
                    board[board_row][board_col] = color

def reset_game_state():
    """Resets all game state variables for a new game."""
    global board, score, level, fall_delay, total_lines
    global next_piece, next_color, game_state, start_time
    board = [[(0, 0, 0) for _ in range(CONFIG["COLUMNS"])]
             for _ in range(CONFIG["ROWS"])]
    score = 0
    level = 1
    fall_delay = CONFIG["INITIAL_FALL_DELAY"]
    total_lines = 0
    next_piece, next_color = new_piece()
    game_state = "playing"
    start_time = pygame.time.get_ticks()

def clear_complete_rows(board):
    """Removes all full rows and returns new board, count, and indices."""
    removed_rows = []
    new_rows = []
    for i, row in enumerate(board):
        if row.count((0, 0, 0)) == 0:
            removed_rows.append(i)
        else:
            new_rows.append(row)
    for _ in removed_rows:
        new_rows.insert(0, [(0, 0, 0)] * CONFIG["COLUMNS"])
    return new_rows, len(removed_rows), removed_rows

def calculate_score(rows_cleared):
    """Returns score based on the number of rows cleared."""
    if rows_cleared == 1:
        return 100
    elif rows_cleared == 2:
        return 300
    elif rows_cleared == 3:
        return 500
    elif rows_cleared == 4:
        return 800
    return 0

# === Piece and State Control ===
def reset_piece():
    """Sets the next piece as the current piece and spawns a new next piece."""
    global current_piece, current_color, next_piece, next_color
    global current_rotation, piece_x, piece_y
    current_piece, current_color = next_piece, next_color
    next_piece, next_color = new_piece()
    current_rotation = 0
    piece_x = (CONFIG["COLUMNS"] - 4) // 2
    piece_y = 0

    # Draw the board and piece immediately (no animation)
    draw_board()
    draw_piece(current_piece, current_rotation, piece_x, piece_y, current_color)
    pygame.display.flip()


# === Collision and Validation ===
def valid_position(piece, rotation, piece_x, piece_y, board):
    """Returns True if the piece fits at the given position on the board."""
    shape = piece[rotation]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == 1:
                board_row = piece_y + i
                board_col = piece_x + j
                if (
                    board_row < 0 or
                    board_row >= CONFIG["ROWS"] or
                    board_col < 0 or
                    board_col >= CONFIG["COLUMNS"]
                ):
                    return False
                if board[board_row][board_col] != (0, 0, 0):
                    return False
    return True

def is_game_over(piece, rotation, piece_x, piece_y, board):
    """Returns True if the current piece placement triggers game over."""
    return not valid_position(piece, rotation, piece_x, piece_y, board)


# === Piece Loc/Clear/Score Functions ===
def lock_piece_to_board():
    add_piece_to_board(
        current_piece,
        current_rotation,
        piece_x,
        piece_y,
        board,
        current_color
    )
    
def clear_and_animate_rows():
    """Clears filled rows and plays clear animation."""
    global board
    board, cleared, highlighted_rows = clear_complete_rows(board)
    if cleared > 0:
        for i in highlighted_rows:
            for col in range(CONFIG["COLUMNS"]):
                pygame.draw.rect(
                    window,
                    (255, 255, 255),
                    (
                        col * CONFIG["CELL_SIZE"],
                        i * CONFIG["CELL_SIZE"] + 60,
                        CONFIG["CELL_SIZE"],
                        CONFIG["CELL_SIZE"]
                    )
                )
        pygame.display.flip()
        pygame.time.delay(150)
    return cleared
    
def update_score_and_level(cleared):
    """Updates score, level, and fall speed after line clears."""
    global score, total_lines, level, fall_delay
    score += calculate_score(cleared)
    total_lines += cleared
    if total_lines >= level * 10:
        level += 1
        fall_delay = max(100, fall_delay - 50)

# === Game Loop Variables ===
next_piece, next_color = new_piece()
reset_piece()
fall_delay = CONFIG["INITIAL_FALL_DELAY"]  # ms
last_fall_time = pygame.time.get_ticks()

# === Leaderboard Display ===
def show_leaderboard():
    """Displays the leaderboard screen."""
    try:
        with open("leaderboard.txt", "r") as f:
            scores = [line.strip().split(",") for line in f.readlines()]
            scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)[:10]
    except FileNotFoundError:
        scores = []

    font = pygame.font.SysFont("Verdana", 24)
    font_title = pygame.font.SysFont("Verdana", 32, bold=True)
    while True:
        window.fill((15, 15, 15))
        title = font_title.render("Leaderboard", True, (255, 255, 255))
        window.blit(
            title,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - title.get_width() // 2,
                50
            )
        )
        for i, (name, score_val) in enumerate(scores):
            text = font.render(
                f"{i+1}. {name}: {score_val}",
                True,
                (255, 255, 255)
            )
            window.blit(text, (100, 100 + i * 30))
        text_exit = font.render(
            "Press ESC to return",
            True,
            (180, 180, 180)
        )
        window.blit(text_exit, (100, 450))
        window.blit(logo_bitso, (CONFIG["WINDOW_WIDTH"] - 70, 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

# === Menu Display ===
def show_menu():
    """Displays the main menu and returns the selected option."""
    font_menu = pygame.font.SysFont("Verdana", 28, bold=True)
    font_options = pygame.font.SysFont("Verdana", 22)
    selection = 0
    options = ["New Game", "Leaderboard"]

    while True:
        window.fill((15, 15, 15))
        title = font_menu.render("Bitso Tetris", True, (255, 255, 255))
        window.blit(
            title,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - title.get_width() // 2,
                100
            )
        )
        for i, text in enumerate(options):
            color = (34, 221, 145) if i == selection else (255, 255, 255)
            option_render = font_options.render(text, True, color)
            window.blit(
                option_render,
                (
                    CONFIG["WINDOW_WIDTH"] // 2 - option_render.get_width() // 2,
                    200 + i * 40
                )
            )
        window.blit(logo_bitso, (CONFIG["WINDOW_WIDTH"] - 70, 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selection = (selection - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selection = (selection + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selection]

# === Main Game Loop ===
# Show initial menu before starting the game
choice = show_menu()
if choice == "Leaderboard":
    show_leaderboard()
    choice = show_menu()
    if choice == "Leaderboard":
        show_leaderboard()

while True:
    for event in pygame.event.get():
        # Handle pause toggle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            is_paused = not is_paused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                new_rotation = (current_rotation + 1) % len(current_piece)
                if valid_position(
                    current_piece, new_rotation, piece_x, piece_y, board
                ):
                    current_rotation = new_rotation
            elif event.key == pygame.K_DOWN:
                if valid_position(
                    current_piece, current_rotation, piece_x, piece_y + 1, board
                ):
                    piece_y += 1
            elif event.key == pygame.K_SPACE:
                while valid_position(
                    current_piece, current_rotation, piece_x, piece_y + 1, board
                ):
                    piece_y += 1
                lock_piece_to_board()
                reset_piece()
                if is_game_over(
                    current_piece, 
                    current_rotation, 
                    piece_x, 
                    piece_y, 
                    board
                ):
                    game_state = "gameover"
                cleared = clear_and_animate_rows()
                update_score_and_level(cleared)
                last_fall_time = pygame.time.get_ticks()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Pause logic
    if is_paused:
        font_pause = pygame.font.SysFont("Verdana", 40, bold=True)
        text_pause = font_pause.render("PAUSED", True, (255, 255, 255))
        window.blit(
            text_pause,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - text_pause.get_width() // 2,
                CONFIG["WINDOW_WIDTH"] // 2 - text_pause.get_height() // 2
            )
        )
        pygame.display.flip()
        clock.tick(CONFIG["FPS"])
        continue

    # Continuous input handling
    now = pygame.time.get_ticks()
    if now - last_fall_time > fall_delay:
        if valid_position(
            current_piece, current_rotation, piece_x, piece_y + 1, board
        ):
            piece_y += 1
        else:
            lock_piece_to_board()
            reset_piece()
            if is_game_over(
                    current_piece, 
                    current_rotation, 
                    piece_x, 
                    piece_y, 
                    board
                ):
                game_state = "gameover"
            cleared = clear_and_animate_rows()
            update_score_and_level(cleared)
            last_fall_time = now

    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        if pygame.time.get_ticks() - last_fall_time > CONFIG["FAST_DROP_SPEED"]:
            if valid_position(
                current_piece, current_rotation, piece_x, piece_y + 1, board
            ):
                piece_y += 1
                last_fall_time = pygame.time.get_ticks()
    if (
        keys[pygame.K_LEFT]
        and now - last_left_move_time > CONFIG["LATERAL_SPEED"]
    ):
        if valid_position(
            current_piece, current_rotation, piece_x - 1, piece_y, board
        ):
            piece_x -= 1
            last_left_move_time = now
    if (
        keys[pygame.K_RIGHT]
        and now - last_right_move_time > CONFIG["LATERAL_SPEED"]
    ):
        if valid_position(
            current_piece, current_rotation, piece_x + 1, piece_y, board
        ):
            piece_x += 1
            last_right_move_time = now

    if game_state == "gameover":
        # Prompt for the player's name after game over
        name = ""
        entering_name = True
        font_info = pygame.font.SysFont("Arial", 20)
        font_name = pygame.font.SysFont("Arial", 22)
        while entering_name:
            window.fill((0, 0, 0))
            prompt = font_info.render("Enter your name:", True, (255, 255, 255))
            entry = font_name.render(name + "_", True, (255, 255, 255))
            window.blit(
                prompt,
                (
                    CONFIG["WINDOW_WIDTH"] // 2 - 100,
                    CONFIG["WINDOW_HEIGHT"] // 2 - 40
                )
            )
            window.blit(
                entry,
                (
                    CONFIG["WINDOW_WIDTH"] // 2 - 100,
                    CONFIG["WINDOW_HEIGHT"] // 2
                )
            )
            pygame.display.flip()
            for event_name in pygame.event.get():
                if event_name.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event_name.type == pygame.KEYDOWN:
                    if event_name.key == pygame.K_RETURN and name.strip():
                        entering_name = False
                    elif event_name.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event_name.unicode.isprintable() and len(name) < 12:
                        name += event_name.unicode
        try:
            with open("leaderboard.txt", "a") as f:
                f.write(f"{name},{score}\n")
        except Exception:
            pass
        if score > high_score:
            with open(RECORD_FILE, "w") as file:
                file.write(str(score))
            high_score = score
        # Show GAME OVER message and options
        font_gameover = pygame.font.SysFont("Verdana", 30, bold=True)
        text_gameover = font_gameover.render("GAME OVER", True, (255, 0, 0))
        font_info = pygame.font.SysFont("Verdana", 20)
        text_r = font_info.render(
            "Press R to restart", True, (255, 255, 255)
        )
        text_esc = font_info.render(
            "Press ESC to quit", True, (255, 255, 255)
        )
        text_m = font_info.render(
            "Press M for menu", True, (255, 255, 255)
        )
        window.fill((0, 0, 0))
        window.blit(
            text_gameover,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - text_gameover.get_width() // 2,
                CONFIG["WINDOW_HEIGHT"] // 2 - 40
            )
        )
        window.blit(
            text_r,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - text_r.get_width() // 2,
                CONFIG["WINDOW_HEIGHT"] // 2 + 10
            )
        )
        window.blit(
            text_esc,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - text_esc.get_width() // 2,
                CONFIG["WINDOW_HEIGHT"] // 2 + 40
            )
        )
        window.blit(
            text_m,
            (
                CONFIG["WINDOW_WIDTH"] // 2 - text_m.get_width() // 2,
                CONFIG["WINDOW_HEIGHT"] // 2 + 70
            )
        )
        pygame.display.flip()
        waiting_for_option = True
        while waiting_for_option:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        reset_game_state()
                        waiting_for_option = False
                    elif event.key == pygame.K_m:
                        choice = show_menu()
                        if choice == "Leaderboard":
                            show_leaderboard()
                            choice = show_menu()
                        reset_game_state()
                        waiting_for_option = False
        continue

    window.fill((15, 15, 15))  # Bitso-style dark background
    # Title
    font_title = pygame.font.SysFont("Verdana", 30, bold=True)
    title = font_title.render("Bitso Tetris", True, (255, 255, 255))
    text_width = title.get_width()
    board_width = CONFIG["COLUMNS"] * CONFIG["CELL_SIZE"]
    window.blit(
        title,
        ((board_width - text_width) // 2, 5)
    )
    font_author = pygame.font.SysFont("Verdana", 12, italic=True)
    author = font_author.render("@julian_colombo", True, (150, 150, 150))
    window.blit(
        author,
        (
            CONFIG["WINDOW_WIDTH"] - author.get_width() - 10,
            CONFIG["WINDOW_HEIGHT"] - 20
        )
    )
    draw_board()
    draw_piece(current_piece, current_rotation, piece_x, piece_y, current_color)
    # Display score and level
    font = pygame.font.SysFont("Verdana", 20)
    font_bold = pygame.font.SysFont("Verdana", 20, bold=True)
    current_time = pygame.time.get_ticks()
    seconds_played = (current_time - start_time) // 1000
    minutes = seconds_played // 60
    seconds = seconds_played % 60
    text_score = font_bold.render("Score:", True, (255, 255, 255))
    value_score = font.render(str(score), True, (255, 255, 255))
    text_level = font_bold.render("Level:", True, (255, 255, 255))
    value_level = font.render(str(level), True, (255, 255, 255))
    text_high_score = font_bold.render("High Score:", True, (255, 255, 255))
    value_high_score = font.render(str(high_score), True, (255, 255, 255))
    text_time = font_bold.render("Time:", True, (255, 255, 255))
    value_time = font.render(
        f"{minutes:02}:{seconds:02}",
        True,
        (255, 255, 255)
    )
    x_info = PANEL_X
    y_info = 120
    line_spacing = 30
    window.blit(text_score, (x_info, y_info))
    window.blit(value_score, (x_info + 140, y_info))
    y_info += line_spacing
    window.blit(text_level, (x_info, y_info))
    window.blit(value_level, (x_info + 140, y_info))
    y_info += line_spacing
    window.blit(text_high_score, (x_info, y_info))
    window.blit(value_high_score, (x_info + 140, y_info))
    y_info += line_spacing
    window.blit(text_time, (x_info, y_info))
    window.blit(value_time, (x_info + 140, y_info))

    # Display total lines cleared
    text_lines = font_bold.render("Lines:", True, (255, 255, 255))
    value_lines = font.render(str(total_lines), True, (255, 255, 255))
    y_info += line_spacing
    window.blit(text_lines, (x_info, y_info))
    window.blit(value_lines, (x_info + 140, y_info))
    
    # Display next piece
    font_next = pygame.font.SysFont("Verdana", 20, bold=True)
    text_next = font_next.render(
        "Next:",
        True,
        (255, 255, 255)
    )
    window.blit(text_next, (x_info, y_info + line_spacing))
    next_shape = next_piece[0]
    for i, row in enumerate(next_shape):
        for j, cell in enumerate(row):
            if cell == 1:
                x = x_info + j * CONFIG["CELL_SIZE"]
                y = y_info + line_spacing + 30 + i * CONFIG["CELL_SIZE"]
                pygame.draw.rect(
                    window,
                    next_color,
                    (x, y, CONFIG["CELL_SIZE"], CONFIG["CELL_SIZE"])
                )
                pygame.draw.rect(
                    window,
                    (80, 80, 80),
                    (x, y, CONFIG["CELL_SIZE"], CONFIG["CELL_SIZE"]),
                    1
                )
    window.blit(
        logo_bitso,
        (CONFIG["WINDOW_WIDTH"] - 70, 10)
    )
    pygame.display.flip()
    clock.tick(CONFIG["FPS"])