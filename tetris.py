import random
import pygame

pygame.init()

CELL_SIZE = 30
COLS = 10
ROWS = 20
PLAY_WIDTH = CELL_SIZE * COLS
PLAY_HEIGHT = CELL_SIZE * ROWS
SIDE_PANEL = 200
WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL
WINDOW_HEIGHT = PLAY_HEIGHT

BLACK = (20, 20, 20)
GRAY = (60, 60, 60)
WHITE = (255, 255, 255)

SHAPES = {
    "I": [[(0, 0), (1, 0), (2, 0), (3, 0)]],
    "O": [[(0, 0), (1, 0), (0, 1), (1, 1)]],
    "T": [[(0, 0), (1, 0), (2, 0), (1, 1)]],
    "S": [[(1, 0), (2, 0), (0, 1), (1, 1)]],
    "Z": [[(0, 0), (1, 0), (1, 1), (2, 1)]],
    "J": [[(0, 0), (0, 1), (1, 1), (2, 1)]],
    "L": [[(2, 0), (0, 1), (1, 1), (2, 1)]],
}

SHAPE_COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}


def rotate_cells(cells):
    return [(y, -x) for x, y in cells]


def normalize(cells):
    min_x = min(c[0] for c in cells)
    min_y = min(c[1] for c in cells)
    return [(x - min_x, y - min_y) for x, y in cells]


class Piece:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.cells = SHAPES[shape_key][0]
        self.color = SHAPE_COLORS[shape_key]
        self.x = COLS // 2 - 2
        self.y = 0

    def get_cells(self, x=None, y=None, cells=None):
        cells = cells if cells is not None else self.cells
        x = self.x if x is None else x
        y = self.y if y is None else y
        return [(x + cx, y + cy) for cx, cy in cells]

    def rotated_cells(self):
        return normalize(rotate_cells(self.cells))


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def valid_position(self, cells):
        for x, y in cells:
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, piece):
        for x, y in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color

    def clear_lines(self):
        full_rows = [r for r in range(ROWS) if all(cell is not None for cell in self.grid[r])]
        for r in full_rows:
            del self.grid[r]
            self.grid.insert(0, [None for _ in range(COLS)])
        return len(full_rows)


def new_bag():
    keys = list(SHAPES.keys())
    random.shuffle(keys)
    return keys


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 40)
        self.board = Board()
        self.bag = new_bag()
        self.next_bag = new_bag()
        self.current = self.spawn_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 0.6
        self.game_over = False

    def spawn_piece(self):
        if not self.bag:
            self.bag = self.next_bag
            self.next_bag = new_bag()
        key = self.bag.pop(0)
        return Piece(key)

    def move(self, dx, dy):
        cells = self.current.get_cells(self.current.x + dx, self.current.y + dy)
        if self.board.valid_position(cells):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self):
        new_cells = self.current.rotated_cells()
        for kick in (0, -1, 1, -2, 2):
            cells = self.current.get_cells(self.current.x + kick, self.current.y, new_cells)
            if self.board.valid_position(cells):
                self.current.cells = new_cells
                self.current.x += kick
                return

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_current()

    def lock_current(self):
        self.board.lock_piece(self.current)
        cleared = self.board.clear_lines()
        if cleared:
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(cleared, 0) * self.level
            self.lines_cleared += cleared
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(0.08, 0.6 - (self.level - 1) * 0.05)
        self.current = self.spawn_piece()
        if not self.board.valid_position(self.current.get_cells()):
            self.game_over = True

    def update(self, dt):
        if self.game_over:
            return
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move(0, 1):
                self.lock_current()

    def draw_cell(self, x, y, color):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw(self):
        self.screen.fill(BLACK)

        for y in range(ROWS):
            for x in range(COLS):
                color = self.board.grid[y][x]
                if color:
                    self.draw_cell(x, y, color)
                else:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        if not self.game_over:
            for x, y in self.current.get_cells():
                if y >= 0:
                    self.draw_cell(x, y, self.current.color)

        panel_x = PLAY_WIDTH + 20
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(score_text, (panel_x, 20))
        self.screen.blit(level_text, (panel_x, 50))
        self.screen.blit(lines_text, (panel_x, 80))

        next_label = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_label, (panel_x, 130))
        next_key = self.bag[0] if self.bag else self.next_bag[0]
        for cx, cy in SHAPES[next_key][0]:
            rect = pygame.Rect(panel_x + cx * 20, 160 + cy * 20, 20, 20)
            pygame.draw.rect(self.screen, SHAPE_COLORS[next_key], rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

        controls = [
            "Controls:",
            "Left/Right: Move",
            "Down: Soft drop",
            "Up: Rotate",
            "Space: Hard drop",
            "R: Restart",
        ]
        for i, line in enumerate(controls):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (panel_x, 250 + i * 25))

        if self.game_over:
            overlay = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            text = self.big_font.render("GAME OVER", True, WHITE)
            rect = text.get_rect(center=(PLAY_WIDTH // 2, PLAY_HEIGHT // 2 - 20))
            self.screen.blit(text, rect)
            hint = self.font.render("Press R to restart", True, WHITE)
            hint_rect = hint.get_rect(center=(PLAY_WIDTH // 2, PLAY_HEIGHT // 2 + 20))
            self.screen.blit(hint, hint_rect)

        pygame.display.flip()

    def restart(self):
        self.__init__()


def main():
    game = Game()
    running = True
    while running:
        dt = game.clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif not game.game_over:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        if not game.move(0, 1):
                            game.lock_current()
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        game.update(dt)
        game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
