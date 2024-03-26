from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # Проверка на равенство
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


# Классы исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел мимо доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже выстрелили!"


class BoardWrongShipException(BoardException):
    pass


# Корабль и параметры
class Ship:
    def __init__(self, bow, l, d):
        self.bow = bow  # Точка размещения носа корабля
        self.len = l  # Длина корабля
        self.direction = d  # Направление корабля
        self.lives = l  # Количество жизней

    # Точки корабля
    @property
    def dots(self):
        ship_dots = []  # Список точек кораблей
        for i in range(self.len):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 0:  # Горизонталь
                cur_x += i

            elif self.direction == 1:  # Вертикаль
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))  # Добавление в список

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots  # Проверка попадания


# Игровая доска
class Board:
    def __init__(self, hid=False, size=6):  # Параметры
        self.size = size  # Размер
        self.hid = hid  # Скрытие кораблей

        self.count = 0  # Количество живых кораблей

        self.field = [["O"] * size for _ in range(size)]

        self.busy_dot = []
        self.ships = []

    def add_ship(self, ship):  # Ставление кораблей на доску
        for d in ship.dots:
            if self.out(d) or d in self.busy_dot:  # Проверка выхода точки за предел доски
                raise BoardWrongShipException()  # Выдачи ошибки

        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy_dot.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):  # Обводка корабля по контору
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy_dot:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy_dot.append(cur)

    def __str__(self):  # Вывод доски
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")

        return res

    def out(self, d):  # # Проверка выхода точки за предел доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):  # Выстрел по доске
        if self.out(d):  # Если выстрел за доской
            raise BoardOutException()  # Вывод ошибки

        if d in self.busy_dot:  # Если в эту точку уже стреляли
            raise BoardUsedException()

        self.busy_dot.append(d)

        for ship in self.ships:
            if d in ship.dots:  # Если коордианты выстрела находятся в списке
                ship.lives -= 1  # Минус одна жизнь
                self.field[d.x][d.y] = "X"  # Заменя корабля за X
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)  # Обводим корабль
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy_dot = []


# Класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board  # Собственная доска
        self.enemy = enemy  # Доска соперника

    def ask(self):
        raise NotImplementedError()

    def move(self):  # Ход в игре
        while True:
            try:
                target = self.ask()  # Куда сделает выстрел пользователь
                repeat = self.enemy.shot(target)  # Выстрел по доске врага
                return repeat
            except BoardException as e:
                print(e)  # Вывод в случае ошибки


# Класс нашего "ИИ"
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # Случайный выстрел с помощью библиотеки "random"
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Класс нашего пользователя
class User(Player):
    def ask(self):  # Запрос выстрела
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите две координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Класс игры с параметрами
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()  # Доска игрока
        co = self.random_board()  # Доска бота
        co.hid = True

        self.bot = AI(co, pl)
        self.us = User(pl, co)

    # Случайная доска
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # Случайная расстановка кораблей на доске
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0

        for i in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None

                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    @staticmethod
    def greet():  # Приветствие и формат ввода
        print("\nМорской бой!\nВводить: x y"
              "\nx - горизонтальная линия\ny - вертикальная линия")

    def loop(self):  # Цикл нашей игры
        num = 0
        while True:
            print("\nДоска игрока:")
            print(self.us.board)
            print("\nДоска бота:")
            print(self.bot.board)
            if num % 2 == 0:
                print("\nХодит игрок!")
                repeat = self.us.move()
            else:
                print("\nХодит бот!")
                repeat = self.bot.move()
            if repeat:
                num -= 1

            if self.bot.board.count == 7:
                print("\nИгрок выиграл!")
                break

            if self.us.board.count == 7:
                print("\nБот выиграл!")
                break
            num += 1

    # Запуск игры
    def start(self):
        self.greet()
        self.loop()


if __name__ == '__main__':
    g = Game()
    g.start()
