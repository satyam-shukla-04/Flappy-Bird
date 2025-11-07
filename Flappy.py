import cv2
import mediapipe as mp
import pygame
import random
import sys
import numpy as np

# ------------------ Initialize Mediapipe ------------------ #
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.7
)
cap = cv2.VideoCapture(0)

# ------------------ Initialize Pygame ------------------ #
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Gesture Edition")
clock = pygame.time.Clock()

# ------------------ Load Images ------------------ #
bg_img = pygame.transform.scale(pygame.image.load("Images/background-day.png"), (WIDTH, HEIGHT))

pipe_img = pygame.image.load("Images/pipe-green.png").convert_alpha()
# scale pipe to screen height and responsive width
pipe_width = int(WIDTH * 0.09)
pipe_img = pygame.transform.scale(pipe_img, (pipe_width, HEIGHT))

bird_frames = [
    pygame.transform.scale(pygame.image.load("Images/yellowbird-downflap.png"), (60, 45)),
    pygame.transform.scale(pygame.image.load("Images/yellowbird-midflap.png"), (60, 45)),
    pygame.transform.scale(pygame.image.load("Images/yellowbird-upflap.png"), (60, 45))
]

font = pygame.font.SysFont("Arial", 36)

# ------------------ Game Variables ------------------ #
bird_x = 120
bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.4
pipe_gap = 160
pipe_speed = 4
pipes = []
score = 0
game_over = False
frame_index = 0
animation_speed = 0.15

# For smooth hand tracking
smooth_y = bird_y
alpha = 0.2  # smoothing factor

def create_pipe():
    height = random.randint(170, 330)
    top = pipe_img.get_rect(midbottom=(WIDTH + 40, height - pipe_gap // 2))
    bottom = pipe_img.get_rect(midtop=(WIDTH + 40, height + pipe_gap // 2))
    return top, bottom

pipes.extend(create_pipe())

# ------------------ Main Game Loop ------------------ #
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r and game_over:
                # Reset game
                bird_y = HEIGHT // 2
                smooth_y = bird_y
                bird_velocity = 0
                pipes = []
                pipes.extend(create_pipe())
                score = 0
                game_over = False

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Use hand Y position (index finger tip) to move bird
    if results.multi_hand_landmarks and not game_over:
        for handLms in results.multi_hand_landmarks:
            hand_y = handLms.landmark[8].y * HEIGHT
            smooth_y = alpha * hand_y + (1 - alpha) * smooth_y
            bird_y = int(smooth_y)

    if not game_over:
        # Move pipes
        for i in range(0, len(pipes), 2):
            top, bottom = pipes[i], pipes[i + 1]
            top.centerx -= pipe_speed
            bottom.centerx -= pipe_speed

        # Add new pipes
        if pipes[-2].centerx < 300:
            pipes.extend(create_pipe())

        # Remove old pipes
        if pipes[0].centerx < -100:
            pipes.pop(0)
            pipes.pop(0)
            score += 1

        # Gravity
        bird_velocity += gravity
        bird_y += bird_velocity

        # Collision detection
        bird_rect = bird_frames[1].get_rect(center=(bird_x, bird_y))
        for i in range(0, len(pipes), 2):
            top, bottom = pipes[i], pipes[i + 1]
            if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):
                game_over = True
                break
        if bird_y > HEIGHT - 20 or bird_y < 0:
            game_over = True
    else:
        bird_velocity = 0

    # ------------------ Draw Everything ------------------ #
    screen.blit(bg_img, (0, 0))  # Sky background

    # Draw pipes
    for i in range(0, len(pipes), 2):
        top, bottom = pipes[i], pipes[i + 1]
        screen.blit(pipe_img, top)
        flipped_pipe = pygame.transform.flip(pipe_img, False, True)
        screen.blit(flipped_pipe, bottom)

    # Animate bird
    frame_index += animation_speed
    if frame_index >= len(bird_frames):
        frame_index = 0
    bird_img = bird_frames[int(frame_index)]
    screen.blit(bird_img, (bird_x - 20, bird_y - 15))

    # Display score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if game_over:
        over_text = font.render("Game Over", True, (255, 110, 100))
        screen.blit(over_text, (40, HEIGHT // 2))

    pygame.display.update()
    clock.tick(60)
