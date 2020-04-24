# Требуется просчитать протокол турнира по боулингу в файле tournament.txt

# Пример записи из лога турнира
#   ### Tour 1
#   Алексей	35612/----2/8-6/3/4/
#   Татьяна	62334/6/4/44X361/X
#   Давид	--8/--8/4/8/-224----
#   Павел	----15623113-95/7/26
#   Роман	7/428/--4-533/34811/
#   winner is .........
#
# Нужно сформировать выходной файл tournament_result.txt c записями вида
#   ### Tour 1
#   Алексей	35612/----2/8-6/3/4/    98
#   Татьяна	62334/6/4/44X361/X      131
#   Давид	--8/--8/4/8/-224----    68
#   Павел	----15623113-95/7/26    69
#   Роман	7/428/--4-533/34811/    94
#   winner is Татьяна

# После обработки протокола турнира вывести на консоль рейтинг игроков в виде таблицы:
#
# +----------+------------------+--------------+
# | Игрок    |  сыграно матчей  |  всего побед |
# +----------+------------------+--------------+
# | Татьяна  |        99        |      23      |
# ...
# | Алексей  |        20        |       5      |
# +----------+------------------+--------------+

import os.path
from bowling_state_pattern import FrameManager as FM
from collections import defaultdict

class ProtocolProcessor:

    TOUR_HEADER = '### Tour'
    TOUR_FOOTER = 'winner is'
    TOUR_ROW_START_SYMBOL = '#'
    TOUR_ROW_VALUES_SEPARATOR = '\t'

    def __init__(self, protocol, encoding = 'utf8', print_players_stats=True, rules=1):
        self.protocol = os.path.normpath(os.path.join(os.path.dirname(__file__), protocol))
        self.encoding = encoding
        self.players_results = defaultdict(list)
        self.print_players_stats = print_players_stats
        self.rules = rules

    def _get_new_tour_results_dict(self):
        return {'points': {}, 'winner': None}

    def _get_tour_winner(self, tour_results):
        return sorted(tour_results.items(), key = lambda player_data: player_data[1][1], reverse=True)[0][0]

    def _print_block(self, sections_qty=3, section_length=18, starter='+', filler='-'):

        for _ in range(sections_qty):
            print(starter, end='')
            for __ in range (section_length):
                print(filler, end='')
        print(starter)

    def _print_line(self, items, row_filler='|'):
        print(row_filler, end='')
        for num, item in enumerate(items, start=1):
            end = '\n' if num == len(items) else ''
            if isinstance(item, str):
                print(' '*3, end='')
                print('{content:<15}'.format(content=item), end='')
            else:
                print('{content:^18}'.format(content=item), end='')
            print(row_filler, end=end)

    def _print_players_stats(self):

        self._print_block()
        self._print_line(('Игрок', 'Сыграно матчей', 'Всего побед'))
        self._print_block()

        self.players_results = sorted(self.players_results.items(), key=lambda value: value[1][1], reverse=True)

        for player_results in self.players_results:
            player_stats = [player_results[0]]
            for value in player_results[1]:
                player_stats.append(value)
            self._print_line(player_stats)
        self._print_block()

    def get_result(self):

        if not(os.path.exists(self.protocol) and os.path.isfile(self.protocol)):
            raise FileNotFoundError(f'Ошибка: не найден файл протокола <{self.protocol}>')

        with open(self.protocol, encoding=self.encoding) as protocol:

            protocol_results = {}
            tour_results = self._get_new_tour_results_dict()
            current_tour = None

            for row, line in enumerate(protocol, start=1):

                line = line.replace('\n', '').strip()

                # начало тура
                if ProtocolProcessor.TOUR_HEADER in line:
                    current_tour = line.replace(ProtocolProcessor.TOUR_HEADER, '').\
                        replace(ProtocolProcessor.TOUR_ROW_START_SYMBOL, '').strip()

                    if not current_tour:
                        raise ValueError(f'Ошибка: неверный номер тура в строке № {row} протокола')

                    if current_tour in protocol_results:
                        raise ValueError(f'Ошибка: итоги тура № {current_tour} задублированы в протоколе')

                    tour_results = self._get_new_tour_results_dict()
                    continue

                # конец тура
                if ProtocolProcessor.TOUR_FOOTER in line:
                    # результаты тура
                    tour_winner = self._get_tour_winner(tour_results['points'])
                    tour_results['winner'] = tour_winner
                    protocol_results[current_tour] = tour_results

                    # результаты игроков
                    if self.print_players_stats:
                        for player in tour_results['points'].keys():

                            if not self.players_results[player]:
                                self.players_results[player] = [0, 0]  # кол-во игр и кол-во побед

                            self.players_results[player][0] += 1
                            self.players_results[player][1] += player == tour_winner

                    tour_results = None
                    current_tour = None
                    continue

                # содержание тура
                if current_tour:
                    line = line.replace(ProtocolProcessor.TOUR_ROW_START_SYMBOL, '')

                    try:
                        player, player_game_result = line.split(ProtocolProcessor.TOUR_ROW_VALUES_SEPARATOR)
                    except Exception(f'Ошибка: неверный формат результата игры в строке № {row} протокола'):
                        return

                    player = player.strip()
                    player_game_result = player_game_result.strip()

                    if player in tour_results['points']:
                        raise ValueError(f'Ошибка: игрок {player} задублирован в итогах тура '                                         
                                         f'№ {current_tour} в протоколе')

                    tour_results['points'][player] = [player_game_result, 0]
                    try:
                        tour_results['points'][player][1] = FM(player_game_result, rules=self.rules).get_score()['total_score']
                    except BaseException as exc:
                        print(f'Ошибка при расчете очков игры в строке № {row} протокола. '
                              f'Тип ошибки: {exc.__class__.__name__}, описание ошибки: {exc.args}')

        if self.players_results:
            self._print_players_stats()

        return protocol_results

def main():
    ProtocolProcessor(protocol='tournament.txt').get_result()

if __name__ == '__main__':
    main()