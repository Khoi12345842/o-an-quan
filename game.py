# main.py
import pygame
import sys
import random
from ai import AI

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trò chơi Ô ăn quan")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)

# Font chữ
font = pygame.font.SysFont("Arial", 30)

class OAnQuan:
    def __init__(self, play_mode="PvP"):
        self.board = [5] * 5 + [10] + [5] * 5 + [10]  # 12 ô: 0-4 (dân), 5 (quan), 6-10 (dân), 11 (quan)
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.message = "Chọn chế độ: 1 (PvP), 2 (PvAI), 3 (AIvAI)"
        self.selected_pos = -1
        self.animating = False
        self.stone_positions = []
        self.hand_position = None
        self.clockwise = [5, 6, 7, 8, 9, 10, 11, 4, 3, 2, 1, 0]
        self.counterclockwise = [5, 0, 1, 2, 3, 4, 11, 10, 9, 8, 7, 6]
        self.game_ended = False
        self.play_mode = None
        self.ai1 = None  # AI cho Người chơi 1 (dùng trong AI vs AI)
        self.ai2 = None  # AI cho Người chơi 2 (dùng trong PvAI và AI vs AI)
        self.mode_selection = True

    def draw_board(self, screen):
        screen.fill(WHITE)
        
        # Vẽ ô quan lớn
        pygame.draw.rect(screen, BLUE, (50, 200, 100, 200))  # Quan người 1 (ô 5), màu xanh
        pygame.draw.rect(screen, BLUE, (650, 200, 100, 200))  # Quan người 2 (ô 11), màu xanh
        
        # Vẽ ô dân người 2 (6-10, từ trái sang phải)
        for i in range(5):
            color = GRAY if (i + 6) != self.selected_pos else GREEN
            pygame.draw.rect(screen, color, (150 + i * 100, 200, 80, 80))
        
        # Vẽ ô dân người 1 (0-4, từ trái sang phải)
        for i in range(5):
            color = GRAY if i != self.selected_pos else GREEN
            pygame.draw.rect(screen, color, (150 + i * 100, 300, 80, 80))

        # Hiển thị sỏi dưới dạng chấm tròn
        for i in range(12):
            if i in [5, 11]:  # Ô quan
                stone_count = self.board[i] // 10  # Số quan (1 chấm đỏ = 10 sỏi)
                remaining_stones = self.board[i] % 10  # Sỏi lẻ (chưa đủ 10 để thành 1 quan)
                center_x, center_y = (100 if i == 5 else 700, 300)
                
                # Hiển thị chấm đỏ lớn (số quan)
                for j in range(stone_count):
                    offset_x = (j % 5) * 20 - 40
                    offset_y = (j // 5) * 20 - 20
                    pygame.draw.circle(screen, RED, (center_x + offset_x, center_y + offset_y), 10)
                
                # Hiển thị chấm đen nhỏ (sỏi lẻ)
                for j in range(remaining_stones):
                    offset_x = (j % 5) * 15 - 30
                    offset_y = (j // 5) * 15 + 20
                    pygame.draw.circle(screen, BLACK, (center_x + offset_x, center_y + offset_y), 5)
            else:  # Ô dân
                stone_count = self.board[i]
                if i < 5:  # Ô dân người 1 (0-4)
                    center_x, center_y = (180 + i * 100, 340)
                else:  # Ô dân người 2 (6-10)
                    center_x, center_y = (180 + (i - 6) * 100, 240)
                # Sắp xếp chấm đen trong ô dân
                for j in range(stone_count):
                    offset_x = (j % 5) * 15 - 30
                    offset_y = (j // 5) * 15 - 15
                    pygame.draw.circle(screen, BLACK, (center_x + offset_x, center_y + offset_y), 5)

        # Hiển thị bàn tay (nếu đang rải sỏi)
        if self.hand_position:
            x, y = self.hand_position
            pygame.draw.rect(screen, (255, 204, 153), (x - 15, y - 20, 30, 40))
            for finger in range(4):
                pygame.draw.line(screen, (255, 204, 153), (x - 10 + finger * 8, y - 20), (x - 10 + finger * 8, y - 30), 4)

        # Hiển thị điểm và thông tin
        score1 = font.render(f"P1: {self.player1_score}", True, BLUE)
        score2 = font.render(f"P2: {self.player2_score}", True, RED)
        turn = font.render(f"Lượt: Người {self.current_player}", True, BLACK)
        msg = font.render(self.message, True, BLACK)
        screen.blit(score1, (50, 50))
        screen.blit(score2, (650, 50))
        screen.blit(turn, (300, 50))
        screen.blit(msg, (200, 500))

        # Vẽ sỏi trong hiệu ứng
        for pos_x, pos_y in self.stone_positions:
            pygame.draw.circle(screen, BLACK, (int(pos_x), int(pos_y)), 5)

    def is_valid_move(self, position):
        if self.current_player == 1 and 0 <= position <= 4:
            return self.board[position] > 0
        elif self.current_player == 2 and 5 <= position <= 9:
            return self.board[position] > 0
        return False

    def get_center(self, position):
        if position == 5:
            return (100, 300)
        elif position == 11:
            return (700, 300)
        elif position < 5:
            return (180 + position * 100, 340)
        else:
            return (180 + (position - 6) * 100, 240)

    def get_next_pos(self, current_pos, direction):
        if direction == "R":
            current_idx = self.clockwise.index(current_pos)
            next_idx = (current_idx + 1) % 12
            return self.clockwise[next_idx]
        else:
            current_idx = self.counterclockwise.index(current_pos)
            next_idx = (current_idx + 1) % 12
            return self.counterclockwise[next_idx]

    def animate_spread(self, position, direction):
        self.animating = True
        current_pos = position
        self.stone_positions = []

        while True:
            stones = self.board[current_pos]
            self.board[current_pos] = 0

            for _ in range(stones):
                current_pos = self.get_next_pos(current_pos, direction)
                start_x, start_y = self.get_center(current_pos)
                end_x, end_y = self.get_center(current_pos)
                
                steps = 20
                for i in range(steps + 1):
                    x = start_x + (end_x - start_x) * i / steps
                    y = start_y + (end_y - start_y) * i / steps
                    self.hand_position = (x, y)
                    self.draw_board(screen)
                    pygame.display.flip()
                    pygame.time.delay(33)

                self.board[current_pos] += 1
                self.hand_position = None

            next_pos = self.get_next_pos(current_pos, direction)
            
            if next_pos in [5, 11] or self.board[next_pos] == 0:
                break
            
            current_pos = next_pos

        self.eat_stones(next_pos, direction)
        self.animating = False

    def eat_stones(self, last_pos, direction):
        current_pos = last_pos

        if self.board[current_pos] != 0:
            return

        while True:
            next_pos = self.get_next_pos(current_pos, direction)
            
            if self.board[next_pos] > 0:
                if self.current_player == 1:
                    self.player1_score += self.board[next_pos]
                else:
                    self.player2_score += self.board[next_pos]
                self.board[next_pos] = 0
                current_pos = next_pos
            else:
                next_next_pos = self.get_next_pos(next_pos, direction)
                if self.board[next_next_pos] == 0:
                    break
                current_pos = next_pos
                continue

            next_pos = self.get_next_pos(current_pos, direction)
            if self.board[next_pos] > 0:
                break

    def is_game_over(self):
        if self.board[5] == 0 and self.board[11] == 0 and not self.game_ended:
            for i in range(5):
                self.player1_score += self.board[i]
                self.board[i] = 0
            
            for i in range(6, 11):
                self.player2_score += self.board[i]
                self.board[i] = 0

            if self.player1_score > self.player2_score:
                self.message = f"Trò chơi kết thúc! Người 1 thắng! P1: {self.player1_score} - P2: {self.player2_score}"
            elif self.player2_score > self.player1_score:
                self.message = f"Trò chơi kết thúc! Người 2 thắng! P1: {self.player1_score} - P2: {self.player2_score}"
            else:
                self.message = f"Trò chơi kết thúc! Hòa! P1: {self.player1_score} - P2: {self.player2_score}"
            
            self.game_ended = True
            return True
        
        return False

    def get_position_from_click(self, pos):
        x, y = pos
        if 300 <= y <= 380:
            for i in range(5):
                if 150 + i * 100 <= x <= 230 + i * 100:
                    return i
        if 200 <= y <= 280:
            for i in range(5):
                if 150 + i * 100 <= x <= 230 + i * 100:
                    return i + 6
        return -1

def main():
    game = OAnQuan()
    clock = pygame.time.Clock()
    ai1 = None  # AI cho Người chơi 1 (dùng trong AI vs AI)
    ai2 = None  # AI cho Người chơi 2 (dùng trong PvAI và AI vs AI)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Chọn chế độ chơi
            if game.mode_selection:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game.play_mode = "PvP"
                        game.message = "Chọn ô để rải sỏi"
                        game.mode_selection = False
                    elif event.key == pygame.K_2:
                        game.play_mode = "PvAI"
                        game.message = "Chọn ô để rải sỏi"
                        game.mode_selection = False
                        ai2 = AI(game)  # AI cho Người chơi 2
                    elif event.key == pygame.K_3:
                        game.play_mode = "AIvAI"
                        game.message = "AI vs AI: Đang chơi..."
                        game.mode_selection = False
                        ai1 = AI(game)  # AI cho Người chơi 1
                        ai2 = AI(game)  # AI cho Người chơi 2
            
            # Chế độ PvP (Người với Người)
            else:
                if game.play_mode == "PvP":
                    if event.type == pygame.MOUSEBUTTONDOWN and not game.animating and not game.game_ended:
                        if not game.is_game_over():
                            pos = game.get_position_from_click(event.pos)
                            if pos != -1:
                                if game.is_valid_move(pos):
                                    game.selected_pos = pos
                                    game.message = "Nhấn 1 (thuận) hoặc 2 (ngược) để rải sỏi"
                                else:
                                    game.message = "Ô không hợp lệ! Chọn lại."
                            else:
                                game.message = "Click vào ô của bạn!"
                    
                    elif event.type == pygame.KEYDOWN and not game.game_ended:
                        if not game.animating and game.selected_pos != -1:
                            if event.key == pygame.K_1:
                                game.animate_spread(game.selected_pos, "R")
                                game.current_player = 2 if game.current_player == 1 else 1
                                game.selected_pos = -1
                                game.message = "Chọn ô để rải sỏi"
                            elif event.key == pygame.K_2:
                                game.animate_spread(game.selected_pos, "L")
                                game.current_player = 2 if game.current_player == 1 else 1
                                game.selected_pos = -1
                                game.message = "Chọn ô để rải sỏi"

                # Chế độ PvAI (Người với Máy)
                elif game.play_mode == "PvAI":
                    if game.current_player == 1:  # Lượt người chơi
                        if event.type == pygame.MOUSEBUTTONDOWN and not game.animating and not game.game_ended:
                            if not game.is_game_over():
                                pos = game.get_position_from_click(event.pos)
                                if pos != -1:
                                    if game.is_valid_move(pos):
                                        game.selected_pos = pos
                                        game.message = "Nhấn 1 (thuận) hoặc 2 (ngược) để rải sỏi"
                                    else:
                                        game.message = "Ô không hợp lệ! Chọn lại."
                                else:
                                    game.message = "Click vào ô của bạn!"
                        
                        elif event.type == pygame.KEYDOWN and not game.game_ended:
                            if not game.animating and game.selected_pos != -1:
                                if event.key == pygame.K_1:
                                    game.animate_spread(game.selected_pos, "R")
                                    game.current_player = 2
                                    game.selected_pos = -1
                                    game.message = "Chọn ô để rải sỏi"
                                elif event.key == pygame.K_2:
                                    game.animate_spread(game.selected_pos, "L")
                                    game.current_player = 2
                                    game.selected_pos = -1
                                    game.message = "Chọn ô để rải sỏi"
                    else:  # Lượt AI
                        if not game.animating and not game.game_ended:
                            if not game.is_game_over():
                                best_move = ai2.get_best_move(depth=4)
                                if best_move:
                                    pos, direction = best_move
                                    game.selected_pos = pos
                                    game.animate_spread(pos, direction)
                                    game.current_player = 1
                                    game.selected_pos = -1
                                    game.message = "Chọn ô để rải sỏi"

                # Chế độ AIvAI (Máy với Máy)
                elif game.play_mode == "AIvAI":
                    if not game.animating and not game.game_ended:
                        if not game.is_game_over():
                            if game.current_player == 1:
                                best_move = ai1.get_best_move(depth=4)
                                if best_move:
                                    pos, direction = best_move
                                    game.selected_pos = pos
                                    game.animate_spread(pos, direction)
                                    game.current_player = 2
                                    game.selected_pos = -1
                                    game.message = "AI vs AI: Đang chơi..."
                            else:
                                best_move = ai2.get_best_move(depth=4)
                                if best_move:
                                    pos, direction = best_move
                                    game.selected_pos = pos
                                    game.animate_spread(pos, direction)
                                    game.current_player = 1
                                    game.selected_pos = -1
                                    game.message = "AI vs AI: Đang chơi..."

        game.draw_board(screen)
        game.is_game_over()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()