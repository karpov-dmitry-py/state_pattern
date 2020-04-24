from abc import ABC, abstractmethod
from functools import reduce


class FrameManager:

    STRIKE_SYMBOL = 'X'
    SPARE_SYMBOL = '/'
    MISS_SYMBOL = '-'

    # общее
    MAX_FRAMES = 10
    PINS_QTY = 10

    # для национальных правил
    STRIKE_POINTS = 20
    SPARE_POINTS = 15

    class Throw(ABC):

        def __init__(self, manager):
            self.manager = manager

        def _handle_extra_points(self, result, num_add_extra_throws=0):

            if not self.manager.extra_points:
                if num_add_extra_throws:
                    new_extra_throws_list = [num_add_extra_throws, []]
                    self.manager.extra_points.append(new_extra_throws_list)
                return

            for throw_data in self.manager.extra_points:
                num_extra_throws = throw_data[0]
                extra_throws_gathered_points = throw_data[1]
                if len(extra_throws_gathered_points) < num_extra_throws:# собрали доп. очки с недостаточного кол-ва бросков
                    extra_throws_gathered_points.append(result)

            if num_add_extra_throws:
                new_extra_throws_list = [num_add_extra_throws, []]
                self.manager.extra_points.append(new_extra_throws_list)

        def process(self, symbol):
            if symbol == FrameManager.STRIKE_SYMBOL:
                return self.strike()
            elif symbol == FrameManager.SPARE_SYMBOL:
                return self.spare()
            elif symbol == FrameManager.MISS_SYMBOL:
                return 0
            elif '1' <= symbol <= '9':
                result = int(symbol)

                if self.manager.rules == 0:
                    return result

                elif self.manager.rules == 1: # международные правила
                    self._handle_extra_points(result)
                    return result

                else:
                    return 0

            else:
                raise ValueError(f'Ошибка: неверный символ: {symbol}')

        @abstractmethod
        def strike(self):
            pass

        @abstractmethod
        def spare(self):
            pass

    class FirstThrow(Throw):

        def strike(self):
            if self.manager.rules == 0:
                return FrameManager.STRIKE_POINTS

            elif self.manager.rules == 1: # международные правила
                result = FrameManager.PINS_QTY
                self._handle_extra_points(result, 2)
                return result

            else:
                return 0

        def spare(self):
            raise ValueError(f'Ошибка: cимвол SPARE ({FrameManager.SPARE_SYMBOL}) указан в первом броске')

    class SecondThrow(Throw):
        def strike(self):
            raise ValueError(f'Ошибка: cимвол STRIKE ({FrameManager.STRIKE_SYMBOL}) указан во втором броске')

        def spare(self):
            if self.manager.rules == 0:
                return FrameManager.SPARE_POINTS - self.manager.spare_first_throw_points

            elif self.manager.rules == 1: # международные правила
                result = FrameManager.PINS_QTY - self.manager.spare_first_throw_points

                self._handle_extra_points(result, 1)
                return result

            else:
                return 0

    def __init__(self, game_result, rules: int = 1):
        self.game_result = str(game_result).upper()
        self.rules = rules
        self.extra_points = []
        self.spare_first_throw_points = 0

    def get_all_rules(self):
        rules = {
            0:'National rules',
            1:'International rules',
            #2: правила для межгалактического турнира в Нью-Васюках
        }
        return rules

    def _get_extra_points_total(self):

        total = sum(sum(points[1]) for points in self.extra_points)
        return total

    def get_frames(self):

        if not self.game_result:
            raise ValueError(f'Передан пустой результат игры.')

        if len(self.game_result) == 1 and self.game_result != FrameManager.STRIKE_SYMBOL:
            raise ValueError('Передан неверный результат игры')

        frames = []
        frame = ''

        for char_number, char in enumerate(self.game_result, start=1):

            frame += char
            if len(frame) == 1 and char_number == len(self.game_result) and \
                    char != FrameManager.STRIKE_SYMBOL:
                raise ValueError(f'Передан неверный результат игры - см. последний фрейм: {frame}')

            if len(frame) == 2 or frame == FrameManager.STRIKE_SYMBOL:

                if (all(char.isdigit() for char in frame)
                                                   and sum(int(char) for char in frame) >= FrameManager.PINS_QTY
                ):
                    raise ValueError(f'Передан неверный результат игры - неверный фрейм: ({frame})')

                frames.append(frame)
                frame = ''

                total_frames = len(frames)
                if total_frames > FrameManager.MAX_FRAMES:
                    raise ValueError(f'Передан неверный результат игры: ({frame}) '
                                                 f'Кол-во фактических фреймов ({total_frames}) '
                                                 f'превышает разрешенное кол-во фреймов: ({FrameManager.MAX_FRAMES})')

        return frames

    def get_score(self):

        FIRST_THROW = FrameManager.FirstThrow(manager=self)
        SECOND_THROW = FrameManager.SecondThrow(manager=self)

        total_score = 0
        frames = self.get_frames()

        for frame in frames:

            self.spare_first_throw_points = int(frame.replace('/', '')) if \
                FrameManager.SPARE_SYMBOL in frame else 0

            frame_score = 0
            for char_number, char in enumerate(frame, start=1):
                frame_score += FIRST_THROW.process(char) if char_number == 1 else \
                    SECOND_THROW.process(char)
            total_score += frame_score

        total_score += self._get_extra_points_total()
        return {'total_frames': len(frames), 'total_score': total_score}

def main():

    # game_result = 'Х' * 9 + ''
    # game_result = 'Х4/34'
    game_result = 'XXX347/21'
    # game_result = '12345/'

    try:
        result = FrameManager(game_result).get_score()
        print(
            f"Игра: {game_result}. Всего фреймов сыграно: {result['total_frames']}. Очков набрано: {result['total_score']}")
    except BaseException as exc:
        print(f'Ошибка расчета ({exc.__class__.__name__}): {exc.args}')

if __name__ == '__main__':
    main()