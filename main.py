import numpy as np
import pandas as pd
from pandas import DataFrame


# основной класс
class Footbal:

    def __init__(self, file: str):
        self.data = pd.read_csv(file)

        # счёт команд
        self.score = self.data["счёт"]

        # команды, играющие друг против друга
        self.teams = [self.data["Команда_1"], self.data["Команда_2"]]

    def final_table(self) -> DataFrame:
        table = self.__count_games()
        goals = self.__calculate_goals()
        game_scores = self.__calculate_game_scores()
        final_scores = self.__calcultate_final_scores()

        scores = game_scores.join(goals).join(final_scores)

        table = table.join(scores)

        table = table.sort_values(by=["О"], ascending=False)
        table.index = list(range(1, table.shape[0] + 1))
        return table

    def __count_games(self) -> DataFrame:
        return pd.DataFrame({
            "Игры": self.data["Команда_1"].value_counts() + self.data[
                "Команда_2"].value_counts()}).reset_index().rename(
            columns={"index": "Команда"})

    def __calculate_goals(self):
        mask: list = list(map(lambda number: list(map(int, number[:3].split(":"))), self.score.to_list()))

        goals_1 = DataFrame({
            "Команда": self.teams[0],
            "ЗГ": map(lambda x: x[0], mask),
            "ПГ": map(lambda x: x[1], mask)
        }).groupby("Команда").sum().reset_index()

        goals_2 = DataFrame({
            "Команда": self.teams[1],
            "ЗГ": map(lambda x: x[1], mask),
            "ПГ": map(lambda x: x[0], mask)
        }).groupby("Команда").sum().reset_index()

        return goals_1[["ЗГ", "ПГ"]].add(goals_2[["ЗГ", "ПГ"]])

    def __calculate_game_scores(self) -> DataFrame:
        # маска для парсинга счета
        mask: list = list(map(lambda number: list(map(int, number[:3].split(":"))), self.score.to_list()))

        results_1 = DataFrame({
            "Команда": self.teams[0],
            "В": list(map(lambda x: 1 if x[0] > x[1] else 0, mask)),
            "Н": list(map(lambda x: 1 if x[0] == x[1] else 0, mask)),
            "П": list(map(lambda x: 1 if x[0] < x[1] else 0, mask))
        }).groupby("Команда").sum().reset_index()

        results_2 = DataFrame({
            "Команда": self.teams[1],
            "В": list(map(lambda x: 1 if x[1] > x[0] else 0, mask)),
            "Н": list(map(lambda x: 1 if x[1] == x[0] else 0, mask)),
            "П": list(map(lambda x: 1 if x[1] < x[0] else 0, mask))
        }).groupby("Команда").sum().reset_index()

        results = results_1[["В", "Н", "П"]].add(results_2[["В", "Н", "П"]])

        return results

    def __calcultate_final_scores(self) -> DataFrame:
        table: DataFrame = self.__calculate_game_scores()

        final_scores = DataFrame({
            "О": table["В"] * 3 + table["Н"]
        })

        return final_scores


if __name__ == "__main__":
    
    def font_color_table(value):
        color_value = "black"
        if value > 50:
            color_value = "green"
        elif value < 30:
            color_value = "red"

        return f"color: {color_value}"


    championat = Footbal("csv\\rpl\\13-14.csv")

    championat_font_mod = championat.final_table().style.applymap(font_color_table)
    # print(championat_font_mod)
    print(championat.final_table())
