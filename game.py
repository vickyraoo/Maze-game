import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants for screen dimensions, grid size, and game features
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 8
MAZE_WIDTH = 30
MAZE_HEIGHT = 30
PLAYER_LIVES = 3
SCORE_PER_LEVEL = 100
LEVEL_TIME_LIMIT = 30  # Time limit for each level in seconds

# Constants for player and maze colors
PLAYER_COLOR = (255, 0, 0)
WALL_COLOR = (255, 140, 0)
EMPTY_COLOR = (0, 181, 226)
END_COLOR = (0, 255, 0)

# Constants for UI
FONT_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)
FONT_SIZE = 35
FONT = pygame.font.Font(None, FONT_SIZE)

# Load background music
pygame.mixer.music.load('brook.mp3')
pygame.mixer.music.set_volume(1.0)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play background music indefinitely

# Load sound effects
menu_select_sound = pygame.mixer.Sound('haki.mp3')
menu_select_sound.set_volume(1.0)
level_complete_sound = pygame.mixer.Sound('sound3.mp3')
level_complete_sound.set_volume(1.0)

# Function to draw text on the screen
def draw_text(screen, text, x, y):
    text_surface = FONT.render(text, True, FONT_COLOR)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to generate a random solvable path
def generate_random_path(width, height):
    path = []
    x, y = 0, 0
    while x < width - 1 or y < height - 1:
        if x < width - 1 and y < height - 1:
            direction = random.choice(['R', 'D'])
        elif x < width - 1:
            direction = 'R'
        elif y < height - 1:
            direction = 'D'
        path.append(direction)
        if direction == 'R':
            x += 1
        elif direction == 'D':
            y += 1
    return path

# Function to save the path to a file
def save_path_to_file(path):
    with open('path.txt', 'w') as file:
        file.write(''.join(path))

# Function to generate a maze based on a solvable path
def generate_maze(width, height, difficulty):
    solution_path = generate_random_path(width, height)
    save_path_to_file(solution_path)
    maze = [['wall' for _ in range(width)] for _ in range(height)]
    x, y = 0, 0
    maze[y][x] = 'empty'
    for move in solution_path:
        if move == 'R':
            x += 1
        elif move == 'D':
            y += 1
        maze[y][x] = 'empty'
    # Add density based on difficulty
    density = 0.2 * difficulty  # Adjust density of obstacles based on difficulty
    for i in range(height):
        for j in range(width):
            if maze[i][j] == 'wall' and random.random() < density:
                maze[i][j] = 'empty'
    maze[height - 1][width - 1] = 'end'
    end_point = (width-1, height-1)
    return maze, solution_path, end_point

def draw_maze(screen, maze, player_pos, end_point):
    cell_width = SCREEN_WIDTH // GRID_SIZE
    cell_height = SCREEN_HEIGHT // GRID_SIZE
    half_grid = 2  # Since we want to show 5x5 grid

    # Calculate the start_x and start_y based on the player's position
    start_x = max(0, min(player_pos[0] - half_grid, MAZE_WIDTH - 5))
    start_y = max(0, min(player_pos[1] - half_grid, MAZE_HEIGHT - 5))

    for i in range(5):  # Only iterate over the 5x5 grid
        for j in range(5):
            x = start_x + j
            y = start_y + i
            if 0 <= x < MAZE_WIDTH and 0 <= y < MAZE_HEIGHT:
                color = WALL_COLOR if maze[y][x] == 'wall' else EMPTY_COLOR
                screen_x = (j + half_grid) * cell_width
                screen_y = (i + half_grid) * cell_height
                pygame.draw.rect(screen, color, (screen_x, screen_y, cell_width, cell_height))

                # Draw the end point as a colored block
                if (x, y) == end_point:
                    pygame.draw.rect(screen, END_COLOR, (screen_x, screen_y, cell_width, cell_height))

                # Draw the player as a circle
                if (x, y) == player_pos:
                    pygame.draw.circle(screen, PLAYER_COLOR, (screen_x + cell_width // 2, screen_y + cell_height // 2), cell_width // 4)

    # Optionally, you can draw a border around the visible grid for clarity
    pygame.draw.rect(screen, WALL_COLOR, ((half_grid * cell_width, half_grid * cell_height), (5 * cell_width, 5 * cell_height)), 1)

# Function to move the player
def move_player(player_pos, direction, maze):
    x, y = player_pos
    if direction == 'U' and y > 0 and maze[y - 1][x] != 'wall':
        y -= 1
    elif direction == 'D' and y < MAZE_HEIGHT - 1 and maze[y + 1][x] != 'wall':
        y += 1
    elif direction == 'L' and x > 0 and maze[y][x - 1] != 'wall':
        x -= 1
    elif direction == 'R' and x < MAZE_WIDTH - 1 and maze[y][x + 1] != 'wall':
        x += 1
    return x, y

# Function for the gameplay loop
def gameplay(screen, level, difficulty):
    global PLAYER_LIVES
    start_time = time.time()  # Start the timer
    score = level * SCORE_PER_LEVEL
    maze, solution_path, end_point = generate_maze(MAZE_WIDTH, MAZE_HEIGHT, difficulty=difficulty)
    player_pos = (0,0)
    # Adjust time limit based on difficulty
    level_time_limit = LEVEL_TIME_LIMIT - difficulty * 2  # Decrease time limit based on difficulty

    clock = pygame.time.Clock()

    while True:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, LEVEL_TIME_LIMIT - int(elapsed_time))
        if remaining_time == 0:
            PLAYER_LIVES -= 1
            if PLAYER_LIVES == 0:
                return False, score  # Game over due to running out of lives
            else:
                return True, score  # Restart level due to running out of time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_pos = move_player(player_pos, 'U', maze)
                elif event.key == pygame.K_DOWN:
                    player_pos = move_player(player_pos, 'D', maze)
                elif event.key == pygame.K_LEFT:
                    player_pos = move_player(player_pos, 'L', maze)
                elif event.key == pygame.K_RIGHT:
                    player_pos = move_player(player_pos, 'R', maze)

        # Check if the player has reached the end point
        if maze[player_pos[1]][player_pos[0]] == 'end':
            score += remaining_time  # Add remaining time to score
            level_complete_sound.play()  # Play level complete sound effect
            if PLAYER_LIVES < 3:
                PLAYER_LIVES += 1  # Increase live by 1, but not more than 3
            return True, score  # Proceed to next level

        screen.fill(EMPTY_COLOR)
        draw_maze(screen, maze, player_pos, end_point)
        draw_text(screen, f"Lives: {PLAYER_LIVES}", 200 , 15)  # Top-left corner
        draw_text(screen, f"Score: {score}", SCREEN_WIDTH - 200, 15)  # Top-right corner
        draw_text(screen, f"Time: {remaining_time}", SCREEN_WIDTH // 2, 15)  # Top-center

        pygame.display.flip()
        clock.tick(30)

# Function to display the leaderboard on a new page
def show_leaderboard_page(screen,difficulty_level):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False  # Exit the leaderboard page when the player presses ESC

        screen.fill(BG_COLOR)
        draw_text(screen, "Leaderboard", SCREEN_WIDTH // 2, 50)
        # Display leaderboard here
        display_leaderboard(screen, difficulty_level)
        
        pygame.display.flip()

# Function for the main menu loop
def main_menu(screen):
    player_name = ""
    difficulty_level = 1
    show_leaderboard = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player_name != "":
                        return True, player_name, difficulty_level  # Start game
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()  # Quit game
                elif event.key == pygame.K_9:  # Toggle leaderboard visibility
                    show_leaderboard_page(screen, difficulty_level)  # Show leaderboard page   
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    difficulty_level = 1
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    difficulty_level = 2
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    difficulty_level = 3
                elif event.unicode.isalnum():
                    player_name += event.unicode

        screen.fill(BG_COLOR)
        draw_text(screen, "Maze Game", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 7 )
        draw_text(screen, "Enter Your Name:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, player_name, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 )
        draw_text(screen, "Difficulty Level:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50)
        draw_text(screen, "1 - Easy", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 100)
        draw_text(screen, "2 - Medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 150)
        draw_text(screen, "3 - Hard", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 200)
        draw_text(screen, "Press SPACE to Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 250)
        draw_text(screen, "Press Q to Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 300)
        draw_text(screen, "Press 9 to show Leader Board", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 350)

        if show_leaderboard:  # Display leaderboard if show_leaderboard is True
            display_leaderboard(screen, difficulty_level)
        # Highlight the selected difficulty level
        draw_text(screen, ">", SCREEN_WIDTH // 3 - 40, SCREEN_HEIGHT // 3 + 100 + (difficulty_level - 1) * 50)

        pygame.display.flip()

# Dictionary to store player scores
leaderboards = {1: {}, 2: {}, 3: {}}

# Function to update the leaderboard with a player's score
def update_leaderboard(player_name, score, difficulty_level):
    leaderboard = leaderboards[difficulty_level]
    if player_name in leaderboard:
        if score > leaderboard[player_name]:
            leaderboard[player_name] = score
    else:
        leaderboard[player_name] = score

# Function to display the leaderboard
def display_leaderboard(screen, difficulty_level):
    sorted_leaderboard = sorted(leaderboards[difficulty_level].items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "Leaderboard\n\n"
    for i, (player, score) in enumerate(sorted_leaderboard[:5], start=1):
        leaderboard_text += f"{i}. {player}: {score}\n"
    draw_text(screen, leaderboard_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()         

def game_over(screen, score, player_name, difficulty_level):
    # Game over loop
    update_leaderboard(player_name, score, difficulty_level)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    return True  # Start a new game
                elif event.key == pygame.K_m:
                    return False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()  # Quit game

        screen.fill(BG_COLOR)
        draw_text(screen, "Game Over!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text(screen, f"Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press N for New Game or Q to Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        draw_text(screen,"Press M to Return to Main Menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        pygame.display.flip()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Game")
    level = 1  # Starting level

    while True:
        start_game, player_name, difficulty_level = main_menu(screen)
        if start_game:
            global PLAYER_LIVES
            PLAYER_LIVES = 3
            level = 1
            while True:
                game_over_flag, score = gameplay(screen, level, difficulty_level)
                if game_over_flag:
                    level += 1  # Increase level after completing a level
                else:
                    if game_over(screen, score, player_name, difficulty_level):
                        continue
                    else:
                        break
                display_leaderboard(screen, difficulty_level)

if __name__ == "__main__":
    main()
