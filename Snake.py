import pygame
import random
import sys # Used for sys.exit() to cleanly close the application

# Initialize Pygame modules
pygame.init()

# --- Game Configuration ---

# Define colors using RGB tuples
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)         # Color for the food
GREEN = (0, 170, 0)       # Darker green for snake body or accents
LIGHT_GREEN = (0, 255, 0) # Bright green for snake head/body
BLUE = (50, 153, 213)
DARK_GRAY = (30, 30, 30)    # Background color for a modern look

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Snake properties
SNAKE_BLOCK_SIZE = 20  # Size of each snake segment and food item
SNAKE_SPEED = 15       # Frames per second, controls game speed

# Create the game display surface (window)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Python Snake Game')

# Clock for controlling the game's frame rate
clock = pygame.time.Clock()

# Font styles for messages and score
# Using common system fonts. If not available, Pygame will use a default.
try:
    TITLE_FONT = pygame.font.SysFont("comicsansms", 70)
    MESSAGE_FONT = pygame.font.SysFont("arial", 40)
    SCORE_FONT = pygame.font.SysFont("comicsansms", 35)
    INSTRUCTION_FONT = pygame.font.SysFont("arial", 30)
except pygame.error: # Fallback if specific fonts are not found
    TITLE_FONT = pygame.font.Font(None, 70) # Pygame's default font
    MESSAGE_FONT = pygame.font.Font(None, 40)
    SCORE_FONT = pygame.font.Font(None, 35)
    INSTRUCTION_FONT = pygame.font.Font(None, 30)


# --- Helper Functions ---

def display_score(score):
    """Renders and displays the current score on the screen."""
    score_text = SCORE_FONT.render("Score: " + str(score), True, YELLOW)
    screen.blit(score_text, [10, 10]) # Position at top-left

def draw_snake(snake_block_size, snake_segments_list):
    """Draws the snake on the screen.
    
    Args:
        snake_block_size (int): The size of each snake segment.
        snake_segments_list (list): A list of [x, y] coordinates for snake segments.
    """
    for i, segment_pos in enumerate(snake_segments_list):
        # Use LIGHT_GREEN for the head and alternate GREEN/LIGHT_GREEN for the body
        is_head = (i == len(snake_segments_list) - 1)
        
        segment_color = LIGHT_GREEN if is_head else (GREEN if i % 2 == 0 else LIGHT_GREEN)
        
        # Draw a slightly larger black rectangle for border effect
        pygame.draw.rect(screen, BLACK, 
                         [segment_pos[0], segment_pos[1], snake_block_size, snake_block_size])
        # Draw the colored segment on top, slightly smaller
        pygame.draw.rect(screen, segment_color, 
                         [segment_pos[0] + 1, segment_pos[1] + 1, snake_block_size - 2, snake_block_size - 2])

def display_message(text, color, y_offset=0, font=MESSAGE_FONT):
    """Renders and displays a centered message on the screen.
    
    Args:
        text (str): The message string to display.
        color (tuple): RGB color tuple for the text.
        y_offset (int): Vertical offset from the center of the screen.
        font (pygame.font.Font): The font to use for the message.
    """
    rendered_text = font.render(text, True, color)
    # Get the rectangle of the rendered text to center it
    text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_offset))
    screen.blit(rendered_text, text_rect)

# --- Main Game Logic ---

def game_loop():
    """Main function to run the Snake game, including intro, gameplay, and game over states."""
    
    game_is_over = False  # True when player loses (collision), leading to game over screen
    quit_game_app = False # True when player wants to quit the application entirely

    # --- Game Intro/Start Screen ---
    intro_active = True
    while intro_active and not quit_game_app:
        screen.fill(DARK_GRAY)
        display_message("SnakePy", LIGHT_GREEN, -150, TITLE_FONT)
        display_message("Use Arrow Keys to Move", WHITE, -50, MESSAGE_FONT)
        display_message("Eat the Red Food to Grow", WHITE, 0, MESSAGE_FONT)
        display_message("Avoid Walls and Yourself!", WHITE, 50, MESSAGE_FONT)
        display_message("Press SPACE to Start", YELLOW, 150, INSTRUCTION_FONT)
        display_message("Press Q to Quit", YELLOW, 200, INSTRUCTION_FONT)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro_active = False
                quit_game_app = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro_active = False
                if event.key == pygame.K_q:
                    intro_active = False
                    quit_game_app = True
        
        clock.tick(15) # Intro screen doesn't need high FPS

    if quit_game_app: # If Q pressed or window closed during intro
        pygame.quit()
        sys.exit()

    # --- Gameplay Initialization ---
    # Initial position of the snake (center of the screen, aligned to grid)
    snake_x = (SCREEN_WIDTH / 2 // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
    snake_y = (SCREEN_HEIGHT / 2 // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE

    # Initial movement direction (snake starts moving right after intro)
    snake_x_change = SNAKE_BLOCK_SIZE 
    snake_y_change = 0
    last_key_pressed = pygame.K_RIGHT # Corresponds to initial right movement

    snake_segments = [] # List to store coordinates of snake's body segments
    snake_current_length = 1
    current_player_score = 0

    # Place initial food randomly, ensuring it's grid-aligned
    # Uses integer division for grid alignment
    food_x = random.randrange(0, SCREEN_WIDTH // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
    food_y = random.randrange(0, SCREEN_HEIGHT // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
    
    # Ensure food doesn't spawn on the initial snake position
    while food_x == snake_x and food_y == snake_y:
         food_x = random.randrange(0, SCREEN_WIDTH // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
         food_y = random.randrange(0, SCREEN_HEIGHT // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE

    # --- Main Gameplay Loop ---
    while not game_is_over and not quit_game_app:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # If window is closed
                quit_game_app = True
            if event.type == pygame.KEYDOWN:
                # Handle arrow key presses to change snake direction
                # Prevents immediate reversal (e.g., moving right, then pressing left)
                if event.key == pygame.K_LEFT and last_key_pressed != pygame.K_RIGHT:
                    snake_x_change = -SNAKE_BLOCK_SIZE
                    snake_y_change = 0
                    last_key_pressed = pygame.K_LEFT
                elif event.key == pygame.K_RIGHT and last_key_pressed != pygame.K_LEFT:
                    snake_x_change = SNAKE_BLOCK_SIZE
                    snake_y_change = 0
                    last_key_pressed = pygame.K_RIGHT
                elif event.key == pygame.K_UP and last_key_pressed != pygame.K_DOWN:
                    snake_y_change = -SNAKE_BLOCK_SIZE
                    snake_x_change = 0
                    last_key_pressed = pygame.K_UP
                elif event.key == pygame.K_DOWN and last_key_pressed != pygame.K_UP:
                    snake_y_change = SNAKE_BLOCK_SIZE
                    snake_x_change = 0
                    last_key_pressed = pygame.K_DOWN
        
        # Update snake's head position based on current direction
        snake_x += snake_x_change
        snake_y += snake_y_change

        # --- Collision Detection ---
        # 1. Wall collision: Check if snake hits the screen boundaries
        if snake_x >= SCREEN_WIDTH or snake_x < 0 or snake_y >= SCREEN_HEIGHT or snake_y < 0:
            game_is_over = True # Player lost

        # Add current head position to the snake's segments list
        snake_head_pos = [snake_x, snake_y]
        snake_segments.append(snake_head_pos)

        # Maintain snake's length: if it's longer than allowed, remove the tail segment
        if len(snake_segments) > snake_current_length:
            del snake_segments[0]

        # 2. Self-collision: Check if snake's head collides with any part of its body
        # This check is meaningful only if the snake is long enough to potentially collide.
        if snake_current_length > 1: # Or a higher number like >3 for more strictness
            for segment in snake_segments[:-1]: # Check all segments except the newly added head
                if segment == snake_head_pos:
                    game_is_over = True # Player lost
        
        if game_is_over: # If a collision occurred, break loop to go to game over screen
            break

        # --- Screen Drawing ---
        screen.fill(DARK_GRAY) # Fill background

        # Draw food (as a circle)
        food_radius = SNAKE_BLOCK_SIZE // 2
        pygame.draw.circle(screen, RED, 
                           (food_x + food_radius, food_y + food_radius), food_radius)

        draw_snake(SNAKE_BLOCK_SIZE, snake_segments) # Draw the snake
        display_score(current_player_score) # Display the score

        pygame.display.update() # Refresh the screen to show changes

        # --- Food Consumption Logic ---
        if snake_x == food_x and snake_y == food_y:
            # Respawn food at a new random location
            # Ensure the new food position is not on any part of the snake's body
            while True:
                food_x = random.randrange(0, SCREEN_WIDTH // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
                food_y = random.randrange(0, SCREEN_HEIGHT // SNAKE_BLOCK_SIZE) * SNAKE_BLOCK_SIZE
                
                is_on_snake = False
                for segment in snake_segments:
                    if segment[0] == food_x and segment[1] == food_y:
                        is_on_snake = True
                        break
                if not is_on_snake: # Found a valid spot for the food
                    break
            
            snake_current_length += 1  # Increase snake length
            current_player_score += 10 # Increase score
            # Optional: Increase SNAKE_SPEED here for progressive difficulty
            # global SNAKE_SPEED
            # if current_player_score % 50 == 0 and current_player_score > 0:
            #    SNAKE_SPEED += 1

        clock.tick(SNAKE_SPEED) # Control game speed (FPS)

    # --- Game Over Screen ---
    # This loop runs when game_is_over is True (player lost) but quit_game_app is False
    while game_is_over and not quit_game_app:
        screen.fill(DARK_GRAY)
        display_message("Game Over!", RED, -100, TITLE_FONT)
        display_message(f"Final Score: {current_player_score}", YELLOW, -20, MESSAGE_FONT)
        display_message("Press C to Play Again", WHITE, 80, INSTRUCTION_FONT)
        display_message("Press Q to Quit", WHITE, 130, INSTRUCTION_FONT)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game_app = True # User closed window
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit_game_app = True # User chose to quit
                if event.key == pygame.K_c:
                    # To play again, recursively call game_loop().
                    # This will restart the game from the intro screen.
                    game_loop() 
                    # After the new game_loop() returns (either by quitting or finishing another game),
                    # this current instance of game_loop (which is on game over screen) must also exit.
                    return # Exit this finished game_loop instance.

    # If quit_game_app is True, then uninitialize Pygame and exit the script
    pygame.quit()
    sys.exit()


# --- Start the Game ---
if __name__ == "__main__":
    game_loop()
