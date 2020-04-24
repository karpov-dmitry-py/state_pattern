# -*- coding: utf-8 -*-

# Правила расчета очков игры в боулинг:
#
# Всего 10 кеглей. Игра состоит из 10 фреймов. В одном фрейме до 2х бросков, цель - сбить все кегли.
# Результаты фрейма записываются символами:
#   «Х» – «strike», все 10 кеглей сбиты первым броском
#   «<число>/», например «4/» - «spare», в первый бросок сбиты 4 кегли, во второй – остальные
#   «<число><число>», например, «34» – в первый бросок сбито 3, во второй – 4 кегли.
#   вместо <число> может стоять прочерк «-», например «-4» - ни одной кегли не было сбито за первый бросок
# Результат игры – строка с записью результатов фреймов. Символов-разделителей между фреймами нет.
# Например, для игры из 4 фреймов запись результатов может выглядеть так:
#   «Х4/34-4»
# Предлагается упрощенный способ подсчета количества очков:
#   «Х» – strike всегда 20 очков
#   «4/» - spare всегда 15 очков
#   «34» – сумма 3+4=7
#   «-4» - сумма 0+4=4
# То есть для игры «Х4/34-4» сумма очков равна 20+15+7+4=46
#
# Международные правила подсчета очков: !!!!!
# Если во фрейме страйк, сумма очков за этот фрейм будет равна количеству сбитых кеглей в этом фрейме (10 кеглей)
# плюс количество фактически сбитых кеглей за два следующих броска (в одном или двух фреймах,
# в зависимости от того, был ли страйк в следующем броске).
# Если во фрейме сбит спэр, то сумма очков будет равна количеству сбитых кеглей в этом фрейме (10 кеглей)
# плюс количество фактически сбитых кеглей за первый бросок в следующем фрейме.
# Если фрейм остался открытым, то сумма очков будет равна количеству сбитых кеглей в этом фрейме.
# Страйк и спэр в последнем фрейме - по 10 очков.
#
# То есть для игры «Х4/34» сумма очков равна 10+10 + 10+3 + 3+4 = 40,
# а для игры «ХXX347/21» - 10+20 + 10+13 + 10+7 + 3+4 + 10+2 + 3 = 92

# Из текущего файла сделать консольный скрипт для формирования файла с результатами турнира.
# Параметры скрипта: --input <файл протокола турнира> и --output <файл результатов турнира>


import argparse
import os.path
from tournament import ProtocolProcessor as PP

def main():
    parser = argparse.ArgumentParser(description='Данные протокола турнира и желаемое имя файла с расчетом')
    parser.add_argument('--input', type=str, help='Файл с протоколом турнира')
    parser.add_argument('--output', type=str, help='Файл с расчетом результата (куда сохранить)')
    args = parser.parse_args()

    protocol = args.input.replace("'", "").strip() if args.input else 'tournament.txt'
    output = args.output.replace("'", "").strip() if args.output else 'protocol_output.txt'

    try:
        result = PP(protocol).get_result()
    except BaseException as exc:
        print(f'Произошла ошибка. Тип ошибки: {exc.__class__.__name__}, описание ошибки: {exc.args}')
        return

    if result:

        output = os.path.normpath(os.path.join(os.path.dirname(__file__), output))
        with open(output, mode='w', encoding='utf8') as output_handler:

            for tour, tour_results in result.items():

                tour_header_row = f'{PP.TOUR_ROW_START_SYMBOL}\t{PP.TOUR_HEADER} {tour}\n'
                output_handler.write(tour_header_row)

                for player, player_result in tour_results['points'].items():
                    player_row = f'{PP.TOUR_ROW_START_SYMBOL}\t{player:<15} {player_result[0]:<25} {player_result[1]}\n'
                    output_handler.write(player_row)

                tour_footer_row = f'{PP.TOUR_ROW_START_SYMBOL}\t{PP.TOUR_FOOTER} {tour_results["winner"]}\n\n'
                output_handler.write(tour_footer_row)

        print(f'Обработка протокола завершена. Результат сохранен в файл <{output}>')

if __name__ == '__main__':
    main()