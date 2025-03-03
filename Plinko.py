# to do:
# find better way to compute
# find better way to handle higher layer numbers
# change gui to fit higher layer numbers
# button in game to play more rounds
# button in game to change layer number
# button in game to change bet amount
# button in game to end simulation
# more automatic statistics

import pygame
import random
import math
import sys

manual_multipliers = {
    8:  [1.5, 1.2, 1.0, 0.8, 0.6, 0.8, 1.0, 1.2, 1.5],
    10: [1.8, 1.4, 1.1, 0.9, 0.7, 0.5, 0.7, 0.9, 1.1, 1.4, 1.8],
    12: [2.0, 1.7, 1.4, 1.1, 0.9, 0.7, 0.5, 0.7, 0.9, 1.1, 1.4, 1.7, 2.0]
}

def get_multipliers(n):
    if n in manual_multipliers:
        return manual_multipliers[n]
    else:
        center_multiplier = 0.5
        delta = 0.25
        multipliers = []
        center_index = n / 2
        for i in range(n + 1):
            m = center_multiplier + delta * abs(i - center_index)
            multipliers.append(round(m, 2))
        return multipliers

def simulate_plinko(n):
    positions = [0]
    for _ in range(n):
        move = random.choice([-1, 1])
        positions.append(positions[-1] + move)
    return positions

def compute_multiplier(n, final_x, *_):
    pocket_index = (final_x + n) // 2
    multipliers = get_multipliers(n)
    # len(multipliers) == n+1
    multiplier = multipliers[pocket_index]
    return multiplier, pocket_index

def draw_pegs(screen, board_params, n):
    margin = board_params["margin"]
    spacing_y = board_params["spacing_y"]
    center_x = board_params["center_x"]
    spacing_x = board_params["spacing_x"]
    
    peg_radius = 3
    peg_color = (200, 200, 0)
    
    for i in range(1, n+1):
        y = margin + (i - 0.5) * spacing_y
        start_x = center_x - ((i - 1) * spacing_x) / 2
        for j in range(i):
            x = start_x + j * spacing_x
            pygame.draw.circle(screen, peg_color, (int(x), int(y)), peg_radius)

def draw_board(screen, board_params, n):
    margin = board_params["margin"]
    spacing_y = board_params["spacing_y"]
    center_x = board_params["center_x"]
    spacing_x = board_params["spacing_x"]
    width = board_params["width"]
    
    screen.fill((30, 30, 30))
    # horiz lines
    for i in range(n + 1):
        y = margin + i * spacing_y
        pygame.draw.line(screen, (60, 60, 60), (margin, y), (width - margin, y), 1)
    draw_pegs(screen, board_params, n)
    bottom_y = margin + (n + 1) * spacing_y
    pocket_spacing = spacing_x * 0.5
    font = pygame.font.SysFont(None, 20)
    multipliers = get_multipliers(n)
    # n+1 pockets
    for idx, x_step in enumerate(range(-n, n + 1, 2)):
        x = center_x + x_step * pocket_spacing
        pygame.draw.rect(screen, (80, 80, 200), (x - 15, bottom_y, 30, 20))
        multiplier_text = f"x{multipliers[idx]:.1f}"
        text_surface = font.render(multiplier_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, bottom_y + 20 + text_surface.get_height()/2))
        screen.blit(text_surface, text_rect)

def animate_transition(screen, clock, start_x, start_y, end_x, end_y, board_params, n, steps=20):
    amplitude = 10  # bounce amplitude
    for step in range(steps + 1):
        t = step / steps
        x = start_x + (end_x - start_x) * t
        base_y = start_y + (end_y - start_y) * t
        offset = amplitude * math.sin(math.pi * t)
        y = base_y - offset
        draw_board(screen, board_params, n)
        pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 10)
        pygame.display.flip()
        clock.tick(60)

def animate_play(screen, clock, positions, n, bet, board_params):
    margin = board_params["margin"]
    spacing_y = board_params["spacing_y"]
    center_x = board_params["center_x"]
    spacing_x = board_params["spacing_x"]

    draw_board(screen, board_params, n)
    pygame.display.flip()
    
    xs = [center_x]
    ys = [margin]
    
    for layer in range(1, len(positions)):
        p = positions[layer]
        peg_index = int((p + layer - 1) / 2)
        peg_index = max(0, min(peg_index, layer - 1))
        x = center_x - (((layer - 1) * spacing_x) / 2) + peg_index * spacing_x
        y = margin + (layer - 0.5) * spacing_y - 5
        xs.append(x)
        ys.append(y)
    
    current_x, current_y = xs[0], ys[0]
    for i in range(1, len(xs)):
        target_x, target_y = xs[i], ys[i]
        animate_transition(screen, clock, current_x, current_y, target_x, target_y, board_params, n)
        current_x, current_y = target_x, target_y
    
    final_simulated_x = positions[-1]
    multiplier, pocket_index = compute_multiplier(n, final_simulated_x)
    
    bottom_y = margin + (n + 1) * spacing_y
    pocket_spacing = spacing_x * 0.5
    pockets = []
    for x_step in range(-n, n + 1, 2):
        x_pos = center_x + x_step * pocket_spacing
        pockets.append(x_pos)
    target_x = pockets[pocket_index]
    target_y = bottom_y + 10
    
    animate_transition(screen, clock, current_x, current_y, target_x, target_y, board_params, n)
    pygame.time.wait(300)
    
    payout = round(bet * multiplier, 2)
    return multiplier, pocket_index, payout

def display_stats(screen, board_params, text_lines):
    font = pygame.font.SysFont(None, 28)
    y = 10
    for line in text_lines:
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (10, y))
        y += 30
    pygame.display.flip()

def draw_bar_chart(screen, board_params, pocket_counts, score_multipliers, num_plays):
    font = pygame.font.SysFont(None, 24)
    margin = board_params["margin"]
    width = board_params["width"]
    height = board_params["height"]
    n = len(pocket_counts) - 1
    chart_top = height - 200
    chart_bottom = height - 50
    chart_left = margin
    chart_right = width - margin
    chart_width = chart_right - chart_left
    chart_height = chart_bottom - chart_top

    pygame.draw.rect(screen, (200, 200, 200), (chart_left, chart_top, chart_width, chart_height), 2)
    max_count = max(pocket_counts) if max(pocket_counts) > 0 else 1
    num_pockets = n + 1
    bar_width = chart_width // num_pockets

    for i, count in enumerate(pocket_counts):
        bar_height = int((count / max_count) * (chart_height - 30))
        x = chart_left + i * bar_width
        y = chart_bottom - bar_height
        pygame.draw.rect(screen, (100, 200, 100), (x, y, bar_width - 5, bar_height))
        multiplier_label = font.render(f"x{score_multipliers[i]:.1f}", True, (255, 255, 255))
        screen.blit(multiplier_label, (x + (bar_width - multiplier_label.get_width()) // 2, chart_bottom + 5))
        count_label = font.render(f"{count}", True, (255, 255, 255))
        screen.blit(count_label, (x + (bar_width - count_label.get_width()) // 2, y - 25))
    pygame.display.flip()

def main():
    try:
        bet = float(input("Enter your bet amount (e.g., 1.0): "))
    except ValueError:
        print("Invalid bet amount. Defaulting to $1.0")
        bet = 1.0

    try:
        n = int(input("Enter the number of layers: "))
    except ValueError:
        print("Invalid input. Defaulting to 8 layers.")
        n = 8
    if n < 1:
        print("Number of layers must be at least 1. Defaulting to 8 layers.")
        n = 8

    try:
        num_plays = int(input("Enter the number of plays to simulate: "))
    except ValueError:
        print("Invalid number of plays. Defaulting to 100 plays.")
        num_plays = 100

    sim_choice = input("Do you want to see the simulation animation? (y/n): ").strip().lower()
    simulate_animation = sim_choice.startswith('y')
    
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("The Only Way is Down")
    clock = pygame.time.Clock()
    
    margin = 50
    spacing_y = (height - 2 * margin) / (n + 2)
    center_x = width // 2
    spacing_x = (width - 2 * margin) / (2 * n)
    board_params = {
        "margin": margin,
        "spacing_y": spacing_y,
        "center_x": center_x,
        "spacing_x": spacing_x,
        "width": width,
        "height": height
    }
    
    total_multiplier = 0
    total_payout = 0
    multipliers_list = []
    pocket_counts = [0] * (n + 1)
    play_number = 0
    
    while play_number < num_plays:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        positions = simulate_plinko(n)
        if simulate_animation:
            multiplier, pocket_index, payout = animate_play(screen, clock, positions, n, bet, board_params)
            pygame.time.wait(300)
        else:
            final_x = positions[-1]
            multiplier, pocket_index = compute_multiplier(n, final_x)
            payout = round(bet * multiplier, 2)
        total_multiplier += multiplier
        total_payout += payout
        multipliers_list.append(multiplier)
        pocket_counts[pocket_index] += 1
        play_number += 1

    if num_plays > 0:
        avg_multiplier = total_multiplier / num_plays
        avg_payout = total_payout / num_plays
        variance = sum((m - avg_multiplier) ** 2 for m in multipliers_list) / num_plays
        single_play_std = math.sqrt(variance)
        total_sum_std = single_play_std * math.sqrt(num_plays)
    else:
        avg_multiplier = avg_payout = single_play_std = total_sum_std = 0

    score_multipliers = get_multipliers(n)

    stats_lines = [
        "Simulation Complete",
        f"Total Plays: {num_plays}",
        f"Total Payout: ${total_payout:.2f}",
        f"Avg Multiplier: {avg_multiplier:.2f}",
        f"Avg Payout: ${avg_payout:.2f}",
        f"Single-Play Std. Dev: {single_play_std:.2f}",
        f"Total Sum Std. Dev: {total_sum_std:.2f}",
        "Pocket Distribution:"
    ]
    for i, count in enumerate(pocket_counts):
        percentage = (count / num_plays) * 100
        stats_lines.append(f"  Pocket {i}: {count} plays ({percentage:.1f}%)")
    
    print("\n--- Simulation Complete ---")
    print(f"Total Plays: {num_plays}")
    print(f"Total Payout: ${total_payout:.2f}")
    print(f"Avg Multiplier: {avg_multiplier:.2f}")
    print(f"Avg Payout: ${avg_payout:.2f}")
    print(f"Single-Play Std. Dev: {single_play_std:.2f}")
    print(f"Total Sum Std. Dev: {total_sum_std:.2f}")
    print("\n--- Pocket Distribution ---")
    for i, count in enumerate(pocket_counts):
        percentage = (count / num_plays) * 100
        print(f"  Pocket {i} (x{score_multipliers[i]:.1f}): {count} plays ({percentage:.1f}%)")

    screen.fill((30, 30, 30))
    draw_bar_chart(screen, board_params, pocket_counts, score_multipliers, num_plays)
    display_stats(screen, board_params, stats_lines)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    main()
