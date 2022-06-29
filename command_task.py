from sys import argv
import numpy as np
import pandas as pd
from pandas import DataFrame


class Football:

    def __init__(self, file: str):
        # извлечение таблицы из csv файла
        self.data = pd.read_csv(file)
        # счёт команд
        self.score = self.data["счёт"].apply(lambda s: list(map(int, s[:3].split(":"))))
        # команды, играющие друг против друга
        self.teams = [self.data["Команда_1"], self.data["Команда_2"]]

    def final_table(self):
        # первичная таблица
        table: DataFrame = self.__count_games()
        # таблица с забитыми и пропущенными голами
        goals: DataFrame = self.__calculate_goals()
        # таблица с вычисленными победами, ничьими и поражениями
        game_scores: DataFrame = self.__calculate_game_scores()
        # таблица с вычисленными итоговыми очками
        final_scores: DataFrame = self.__calcultate_final_scores(game_scores)

        # склеиваем все таблицы в одну
        table = table.join([game_scores, goals, final_scores])
        # сортируем таблицу по результирующим очкам
        table = table.sort_values(by=["О"], ascending=False).reset_index().rename(columns={"index": "Команда"})
        # переопределяем индекс
        table.index = np.arange(1, table.shape[0] + 1)

        return table

    def __count_games(self):
        # возвращается таблица с кол-вом игр
        return DataFrame({
            "Игры": self.data["Команда_1"].value_counts() + self.data["Команда_2"].value_counts()})

    def __calculate_goals(self):
        # возвращается таблица с кол-вом забитых и пропущенных голов на команду

        # таблица для столбца "Команда_1"
        goals_1 = DataFrame({
            "Команда": self.teams[0],
            "ЗГ": self.score.apply(lambda x: x[0]),
            "ПГ": self.score.apply(lambda x: x[1])
        }).groupby("Команда").sum()

        # таблица для столбца "Команда_2"
        goals_2 = DataFrame({
            "Команда": self.teams[1],
            "ЗГ": self.score.apply(lambda x: x[1]),
            "ПГ": self.score.apply(lambda x: x[0])
        }).groupby("Команда").sum()

        return goals_1.add(goals_2)

    def __calculate_game_scores(self):
        # возвращается таблица с вычисленными выигрышами, проигрышами, ничьими

        # таблица для столбца "Команда_1"
        results_1 = DataFrame({
            "Команда": self.teams[0],
            "В": self.score.apply(lambda x: 1 if x[0] > x[1] else 0),
            "Н": self.score.apply(lambda x: 1 if x[0] == x[1] else 0),
            "П": self.score.apply(lambda x: 1 if x[0] < x[1] else 0)
        }).groupby("Команда").sum()

        # таблица для столбца "Команда_2"
        results_2 = DataFrame({
            "Команда": self.teams[1],
            "В": self.score.apply(lambda x: 1 if x[1] > x[0] else 0),
            "Н": self.score.apply(lambda x: 1 if x[1] == x[0] else 0),
            "П": self.score.apply(lambda x: 1 if x[1] < x[0] else 0)
        }).groupby("Команда").sum()

        return results_1.add(results_2)

    def __calcultate_final_scores(self, game_scores: DataFrame):
        # вычисление итоговых очков: на 1 победу - +3 очка, на ничью - +1 очко
        return DataFrame({"О": game_scores["В"] * 3 + game_scores["Н"]})


# filename = input("Введите имя файла (пример: 15-16): ")
filename = argv[1]
path = f"csv\\rpl\\{filename}.csv"

try:
    championat = Football(path)
    # championat.final_table().to_csv("output.csv")
    print(championat.final_table())
except FileNotFoundError:
    print("Файл не существует!")
