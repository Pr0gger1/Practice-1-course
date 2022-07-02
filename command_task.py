from sys import argv
import numpy as np
import pandas as pd
from pandas import DataFrame, Series


class Football:
    def __init__(self, file: str):
        # извлечение таблицы из csv файла
        self.data = pd.read_csv(file)

    def final_table(self):
        # вытаскиваем счет с первичной таблицы
        origin_score = self.data["счёт"].apply(self.__parsing_score)
        # команды, играющие друг против друга
        teams = [self.data["Команда_1"], self.data["Команда_2"]]

        # таблица с кол-вом игр
        table: DataFrame = self.__count_games()
        # таблица с забитыми и пропущенными голами
        goals: DataFrame = self.__calculate_goals(tables=teams, scores=origin_score)
        # таблица с вычисленными победами, ничьими и поражениями
        game_scores: DataFrame = self.__calculate_game_scores(tables=teams, scores=origin_score)
        # таблица с вычисленными итоговыми очками
        final_scores: DataFrame = self.__calcultate_final_scores(game_scores)

        # склеиваем все таблицы в одну
        table = table.join([game_scores, goals, final_scores])

        # сортируем таблицу по результирующим очкам
        table = table.sort_values(by=["О"], ascending=False).reset_index().rename(
            columns={"index": "Команда"})

        # создаем объект с количеством вхождений очков
        repeated_scores = table['О'].value_counts()

        # если есть команды с равными очками
        if not repeated_scores[repeated_scores > 1].empty:
            # таблица с личными встречами команд
            private_meetings_table = self.__private_meetings(table, repeated_scores[repeated_scores > 1])
            # выполняем слияние основной таблицы с таблицей личных встреч
            table = pd.merge(table, private_meetings_table, how="outer")
            # сортируем по столбцам обоих таблиц
            table = table.sort_values(by=["О", "Выигр", "Заб", "Разн", "В", "ЗГ"], ascending=False)

            # переопределяем индекс
            table.index = np.arange(1, table.shape[0] + 1)

            # удаляем ненужные столбцы
            table.drop(columns=["Выигр", "Заб", "Разн"], inplace=True)

        return table

    # парсинг счёта
    def __parsing_score(self, s: str) -> list:
        return list(map(int, s[:3].split(":")))

    def __count_games(self):
        # возвращается таблица с кол-вом игр
        return DataFrame({
            "Игры": self.data["Команда_1"].value_counts() + self.data["Команда_2"].value_counts()})

    def __calculate_goals(self, tables: list, scores: Series):
        # возвращается таблица с кол-вом забитых и пропущенных голов на команду

        # таблица для столбца "Команда_1"
        goals_1 = DataFrame({
            "Команда": tables[0],
            "ЗГ": scores.apply(lambda x: x[0]),
            "ПГ": scores.apply(lambda x: x[1])
        }).groupby("Команда").sum()

        # таблица для столбца "Команда_2"
        goals_2 = DataFrame({
            "Команда": tables[1],
            "ЗГ": scores.apply(lambda x: x[1]),
            "ПГ": scores.apply(lambda x: x[0])
        }).groupby("Команда").sum()

        return goals_1.add(goals_2)

    def __calculate_game_scores(self, tables: list, scores: Series):
        # возвращается таблица с вычисленными выигрышами, проигрышами, ничьими

        # таблица для столбца "Команда_1"
        results_1 = DataFrame({
            "Команда": tables[0],
            "В": scores.apply(lambda x: 1 if x[0] > x[1] else 0),
            "Н": scores.apply(lambda x: 1 if x[0] == x[1] else 0),
            "П": scores.apply(lambda x: 1 if x[0] < x[1] else 0)
        }).groupby("Команда").sum()

        # таблица для столбца "Команда_2"
        results_2 = DataFrame({
            "Команда": tables[1],
            "В": scores.apply(lambda x: 1 if x[1] > x[0] else 0),
            "Н": scores.apply(lambda x: 1 if x[1] == x[0] else 0),
            "П": scores.apply(lambda x: 1 if x[1] < x[0] else 0)
        }).groupby("Команда").sum()

        return results_1.add(results_2)

    def __calcultate_final_scores(self, game_scores: DataFrame):
        # вычисление итоговых очков: на 1 победу - +3 очка, на ничью - +1 очко
        return DataFrame({"О": game_scores["В"] * 3 + game_scores["Н"]})

    def __private_meetings(self, table: DataFrame, scores: Series):
        # поиск команд, у которых кол-во очков совпадает
        teams_equal = map(lambda score: table.loc[table['О'] == score]['Команда'], scores.index)

        # поиск команд из первичной таблицы
        origin_table_func = lambda teams: self.data[
            (self.data['Команда_1'].isin(teams)) & (self.data['Команда_2'].isin(teams))
        ]

        # склеиваем команды с одинаковыми очками
        private_matches = pd.concat(map(origin_table_func, teams_equal))

        # парсинг счета из таблицы private_matches
        meeting_scores = private_matches["счёт"].apply(self.__parsing_score)

        # подсчет кол-ва выигрышей ничьих и поражений
        meeting_game_scores = self.__calculate_game_scores(
            tables=[private_matches["Команда_1"], private_matches["Команда_2"]], scores=meeting_scores
        )
        # подсчет кол-ва забитых голов
        meeting_goals = self.__calculate_goals(
            tables=[private_matches["Команда_1"], private_matches["Команда_2"]], scores=meeting_scores
        )
        # подсчет разницы забитых и пропущенных голов
        goal_difference = meeting_goals["ЗГ"] - meeting_goals["ПГ"]

        # сортировка по забитым мячам и разности между забитыми и пропущенными
        teams_meetings_table = meeting_goals.join([meeting_game_scores, goal_difference]).rename(columns={
            0: "Разн",
            "В": "Выигр",
            "ЗГ": "Заб",
        }).reset_index()

        # удаляем ненужные столбцы
        teams_meetings_table.drop(columns=["ПГ", "Н", "П"], inplace=True)

        return teams_meetings_table


filename = input("Введите имя файла (пример: 15-16): ")
# filename = argv[1]
# filename = "18-19"
path = f"csv\\rpl\\{filename}.csv"

try:
    championat = Football(path)
    # championat.final_table().to_csv("output.csv")
    print(championat.final_table())
except FileNotFoundError:
    print("Файл не существует!")
