# ai.py
import copy

class AI:
    def __init__(self, game):
        self.game = game
        self.clockwise = game.clockwise
        self.counterclockwise = game.counterclockwise

    def get_legal_moves(self, player):
        """Lấy tất cả nước đi hợp lệ của người chơi (ô và hướng)."""
        moves = []
        if player == 1:
            # Người chơi 1: ô 0-4
            for pos in range(5):
                if self.game.board[pos] > 0:
                    moves.append((pos, "R"))  # Rải thuận
                    moves.append((pos, "L"))  # Rải ngược
        else:
            # Người chơi 2 (AI): ô 6-10
            for pos in range(6, 11):
                if self.game.board[pos] > 0:
                    moves.append((pos, "R"))  # Rải thuận
                    moves.append((pos, "L"))  # Rải ngược
        return moves

    def get_next_pos(self, current_pos, direction):
        """Lấy ô tiếp theo theo hướng rải."""
        if direction == "R":
            current_idx = self.clockwise.index(current_pos)
            next_idx = (current_idx + 1) % 12
            return self.clockwise[next_idx]
        else:
            current_idx = self.counterclockwise.index(current_pos)
            next_idx = (current_idx + 1) % 12
            return self.counterclockwise[next_idx]

    def simulate_spread(self, board, position, direction, player):
        """Mô phỏng quá trình rải sỏi, trả về bàn cờ mới và điểm số ăn được."""
        new_board = copy.deepcopy(board)
        current_pos = position
        score = 0

        while True:
            stones = new_board[current_pos]
            new_board[current_pos] = 0

            for _ in range(stones):
                current_pos = self.get_next_pos(current_pos, direction)
                new_board[current_pos] += 1

            next_pos = self.get_next_pos(current_pos, direction)
            
            if next_pos in [5, 11] or new_board[next_pos] == 0:
                break
            
            current_pos = next_pos

        # Mô phỏng ăn sỏi
        score += self.simulate_eat_stones(new_board, next_pos, direction, player)
        return new_board, score

    def simulate_eat_stones(self, board, last_pos, direction, player):
        """Mô phỏng quá trình ăn sỏi, trả về điểm số ăn được."""
        current_pos = last_pos
        score = 0

        if board[current_pos] != 0:
            return score

        while True:
            next_pos = self.get_next_pos(current_pos, direction)
            
            if board[next_pos] > 0:
                score += board[next_pos]
                board[next_pos] = 0
                current_pos = next_pos
            else:
                next_next_pos = self.get_next_pos(next_pos, direction)
                if board[next_next_pos] == 0:
                    break
                current_pos = next_pos
                continue

            next_pos = self.get_next_pos(current_pos, direction)
            if board[next_pos] > 0:
                break

        return score

    def evaluate(self, board, player1_score, player2_score):
        """Hàm đánh giá trạng thái trò chơi."""
        return player2_score - player1_score

    def is_terminal(self, board):
        """Kiểm tra xem trạng thái có phải trạng thái kết thúc không."""
        return board[5] == 0 and board[11] == 0

    def calculate_final_score(self, board, player1_score, player2_score):
        """Tính điểm cuối cùng khi trò chơi kết thúc."""
        final_player1_score = player1_score
        final_player2_score = player2_score

        # Người chơi 1: ô 0-4
        for i in range(5):
            final_player1_score += board[i]

        # Người chơi 2: ô 6-10
        for i in range(6, 11):
            final_player2_score += board[i]

        return final_player1_score, final_player2_score

    def minimax(self, board, player1_score, player2_score, depth, maximizing_player, alpha, beta):
        """Thuật toán Minimax với Alpha-Beta Pruning."""
        if depth == 0 or self.is_terminal(board):
            if self.is_terminal(board):
                final_player1_score, final_player2_score = self.calculate_final_score(board, player1_score, player2_score)
                return self.evaluate(board, final_player1_score, final_player2_score), None
            return self.evaluate(board, player1_score, player2_score), None

        if maximizing_player:  # AI (Người chơi 2)
            max_eval = float('-inf')
            best_move = None
            moves = self.get_legal_moves(2)  # Nước đi của AI

            for move in moves:
                pos, direction = move
                new_board, score = self.simulate_spread(board, pos, direction, 2)
                new_player2_score = player2_score + score
                eval_score, _ = self.minimax(new_board, player1_score, new_player2_score, depth - 1, False, alpha, beta)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break

            return max_eval, best_move
        else:  # Người chơi 1
            min_eval = float('inf')
            best_move = None
            moves = self.get_legal_moves(1)  # Nước đi của người chơi

            for move in moves:
                pos, direction = move
                new_board, score = self.simulate_spread(board, pos, direction, 1)
                new_player1_score = player1_score + score
                eval_score, _ = self.minimax(new_board, new_player1_score, player2_score, depth - 1, True, alpha, beta)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break

            return min_eval, best_move

    def get_best_move(self, depth=4):
        """Tìm nước đi tốt nhất cho AI."""
        _, best_move = self.minimax(self.game.board, self.game.player1_score, self.game.player2_score, depth, True, float('-inf'), float('inf'))
        return best_move