import pygame
import sys

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
    def __init__(self):
        self.board = [5] * 5 + [10] + [5] * 5 + [10]  # 12 ô: 0-4 (dân), 5 (quan), 6-10 (dân), 11 (quan)
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.message = "Chọn ô để rải sỏi"
        self.selected_pos = -1
        self.animating = False
        self.stone_positions = []
        # Bảng ánh xạ hướng đi mới
        self.clockwise = [5, 6, 7, 8, 9, 10, 11, 4, 3, 2, 1, 0]  # Thuận: 5 6 7 8 9 10 11 4 3 2 1 0
        self.counterclockwise = [5, 0, 1, 2, 3, 4, 11, 10, 9, 8, 7, 6]  # Ngược: 5 0 1 2 3 4 11 10 9 8 7 6

    def draw_board(self, screen):
        screen.fill(WHITE)
        
        # Vẽ ô quan lớn
        pygame.draw.rect(screen, BLUE, (50, 200, 100, 200))  # Quan người 1 (ô 5)
        pygame.draw.rect(screen, RED, (650, 200, 100, 200))  # Quan người 2 (ô 11)
        
        # Vẽ ô dân người 2 (6-10, từ trái sang phải)
        for i in range(5):
            color = GRAY if (i + 6) != self.selected_pos else GREEN
            pygame.draw.rect(screen, color, (150 + i * 100, 200, 80, 80))
        
        # Vẽ ô dân người 1 (0-4, từ trái sang phải)
        for i in range(5):
            color = GRAY if i != self.selected_pos else GREEN
            pygame.draw.rect(screen, color, (150 + i * 100, 300, 80, 80))

        # Hiển thị số sỏi và đánh số ô
        for i in range(12):
            if i < 5:  # Ô dân người 1 (0-4)
                text = font.render(str(self.board[i]), True, BLACK)
                screen.blit(text, (180 + i * 100, 330))
                label = font.render(str(i), True, BLACK)
                screen.blit(label, (150 + i * 100, 280))
            elif i == 5:  # Quan người 1
                text = font.render(str(self.board[i]), True, BLACK)
                screen.blit(text, (90, 280))
                label = font.render(str(i), True, BLACK)
                screen.blit(label, (90, 180))
            elif i < 11:  # Ô dân người 2 (6-10)
                text = font.render(str(self.board[i]), True, BLACK)
                screen.blit(text, (180 + (i - 6) * 100, 230))
                label = font.render(str(i), True, BLACK)
                screen.blit(label, (150 + (i - 6) * 100, 180))
            else:  # Quan người 2
                text = font.render(str(self.board[i]), True, BLACK)
                screen.blit(text, (690, 280))
                label = font.render(str(i), True, BLACK)
                screen.blit(label, (690, 180))

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
            pygame.draw.circle(screen, BLACK, (int(pos_x), int(pos_y)), 10)

    def is_valid_move(self, position):
        if self.current_player == 1 and 0 <= position <= 4:
            return self.board[position] > 0
        elif self.current_player == 2 and 5 <= position <= 9:
            return self.board[position] > 0
        return False

    def get_center(self, position):
        if position == 5:  # Quan người 1
            return (100, 300)
        elif position == 11:  # Quan người 2
            return (700, 300)
        elif position < 5:  # Ô dân người 1 (0-4, từ trái sang phải)
            return (150 + position * 100 + 30, 340)
        else:  # Ô dân người 2 (6-10, từ trái sang phải)
            return (150 + (position - 6) * 100 + 30, 240)

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
        stones = self.board[position]
        self.board[position] = 0
        current_pos = position
        self.stone_positions = []

        for _ in range(stones):
            prev_pos = current_pos
            current_pos = self.get_next_pos(current_pos, direction)
            
            start_x, start_y = self.get_center(prev_pos)
            end_x, end_y = self.get_center(current_pos)
            
            steps = 20
            for i in range(steps + 1):
                x = start_x + (end_x - start_x) * i / steps
                y = start_y + (end_y - start_y) * i / steps
                self.stone_positions = [(x, y)]
                self.draw_board(screen)
                pygame.display.flip()
                pygame.time.delay(50)

            self.board[current_pos] += 1
            self.stone_positions = []

        self.eat_stones(current_pos, direction)
        self.animating = False

    def eat_stones(self, last_pos, direction):
        next_pos = self.get_next_pos(last_pos, direction)
        if self.board[next_pos] != 0:
            return

        second_next_pos = self.get_next_pos(next_pos, direction)
        if self.board[second_next_pos] > 0 and second_next_pos != 5 and second_next_pos != 11:
            if self.current_player == 1:
                self.player1_score += self.board[second_next_pos]
            else:
                self.player2_score += self.board[second_next_pos]
            self.board[second_next_pos] = 0

    def is_game_over(self):
        return self.board[5] == 0 and self.board[11] == 0

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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game.animating:
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
            elif event.type == pygame.KEYDOWN:
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

        game.draw_board(screen)
        if game.is_game_over():
            winner = "Hòa"
            if game.player1_score > game.player2_score:
                winner = "Người 1 thắng!"
            elif game.player2_score > game.player1_score:
                winner = "Người 2 thắng!"
            game.message = f"Trò chơi kết thúc! {winner}"

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()