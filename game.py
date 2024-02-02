import pygame
import sqlite3
from random import randrange

RES = 800  # Разрешение экрана
SIZE = 50  # Размер клетки
WIN_SCORE = 77  # Очки, необходимые для победы


class Snake:
    def __init__(self, x, y):
        # Инициализация тела змеи, направления движения и длины
        self.body = [(x, y)]
        self.dx = 0
        self.dy = 0
        self.length = 1

    def move(self):
        # Перемещение змеи
        x, y = self.body[-1]
        x += self.dx * SIZE
        y += self.dy * SIZE
        self.body.append((x, y))
        self.body = self.body[-self.length:]

    def draw(self, surface):
        # Отрисовка змеи
        for i, j in self.body:
            pygame.draw.rect(surface, pygame.Color('green'), (i, j, SIZE - 2, SIZE - 2))


class Database:
    def __init__(self, db_name):
        # Инициализация соединения с базой данных и курсора
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # Создание таблицы, если она не существует
        self.create_table()

    def create_table(self):
        # Создание таблицы для хранения результатов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
        ''')
        self.conn.commit()

    def save_score(self, name, score):
        # Сохранение результата в базу данных
        self.cursor.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        # Получение топ-5 игроков по очкам
        self.cursor.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def close(self):
        # Закрытие соединения с базой данных
        self.cursor.close()
        self.conn.close()


# Инициализация Pygame
pygame.init()

# Создание окна игры
sc = pygame.display.set_mode([RES, RES])
clock = pygame.time.Clock()
font_score = pygame.font.SysFont('Arial', 26, bold=True)
font_end = pygame.font.SysFont('Arial', 66, bold=True)
img = pygame.image.load('background.png')
# Создание объекта базы данных
db = Database('snake_scores.db')
print('Привет, это игра "Змейка". Управляй змейкой с помощью стрелочек.')
# Запрос имени игрока
player_name = input("Введите ваше имя: ")
print(f'Отлично {player_name}, набери 77 очков чтобы победить')

# Создание объекта змеи
snake = Snake(randrange(0, RES, SIZE), randrange(0, RES, SIZE))
apple = randrange(0, RES, SIZE), randrange(0, RES, SIZE)
fps = 9
score = 0

# Основной игровой цикл
while True:
    sc.blit(img, (0, 0))
    snake.move()
    snake.draw(sc)
    pygame.draw.rect(sc, pygame.Color('red'), (*apple, SIZE, SIZE))

    render_score = font_score.render(f'SCORE: {score}', 1, pygame.Color('orange'))
    sc.blit(render_score, (5, 5))

    if snake.body[-1] == apple:
        apple = randrange(0, RES, SIZE), randrange(0, RES, SIZE)
        snake.length += 1
        score += 1
        # Проверка победы
        if score >= WIN_SCORE:
            db.save_score(player_name, score)
            top_scores = db.get_top_scores()
            db.close()

            # Отображение сообщения о победе и топ-5 игроков
            while True:
                sc.fill(pygame.Color('black'))
                render_end = font_end.render('YOU WIN!', 1, pygame.Color('green'))
                sc.blit(render_end, (RES // 2 - 200, RES // 3))

                for i, (name, score) in enumerate(top_scores):
                    render_score = font_score.render(f'{i + 1}. {name}: {score}', 1, pygame.Color('orange'))
                    sc.blit(render_score, (RES // 2 - 200, RES // 3 + 50 * (i + 1)))

                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
                        break

                if not running:
                    break
    # Проверка столкновения змеи со стеной или со своим телом
    if (snake.body[-1][0] < 0 or snake.body[-1][0] > RES - SIZE or
            snake.body[-1][1] < 0 or snake.body[-1][1] > RES - SIZE or
            len(snake.body) != len(set(snake.body))):
        # Сохранение результата в базу данных
        db.save_score(player_name, score)
        # Получение топ-5 игроков
        top_scores = db.get_top_scores()
        # Закрытие соединения с базой данных
        db.close()

        # Отображение сообщения о конце игры и топ-5 игроков
        while True:
            sc.fill(pygame.Color('black'))
            render_end = font_end.render('GAME OVER', 1, pygame.Color('red'))
            sc.blit(render_end, (RES // 2 - 200, RES // 3))

            # Вывод топ-5 игроков на экран
            for i, (name, score) in enumerate(top_scores):
                render_score = font_score.render(f'{i + 1}. {name}: {score}', 1, pygame.Color('orange'))
                sc.blit(render_score, (RES // 2 - 200, RES // 3 + 50 * (i + 1)))

            pygame.display.flip()  # Обновление содержимого
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

    pygame.display.flip()
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            db.close()
            exit()

    key = pygame.key.get_pressed()  # реализация управления на стрелочках
    if key[pygame.K_UP]:
        snake.dx, snake.dy = 0, -1
    if key[pygame.K_DOWN]:
        snake.dx, snake.dy = 0, 1
    if key[pygame.K_LEFT]:
        snake.dx, snake.dy = -1, 0
    if key[pygame.K_RIGHT]:
        snake.dx, snake.dy = 1, 0
