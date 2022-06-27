import pandas as pd
from pandas import DataFrame


class Football:

    def __init__(self, file: str) -> None:
        self.data = pd.read_csv(file)

        # счёт команд
        self.score = list(map(lambda number: list(map(int, number[:3].split(":"))), self.data["счёт"].to_list()))
        # команды, играющие друг против друга
        self.teams = [self.data["Команда_1"], self.data["Команда_2"]]

    def final_table(self) -> DataFrame:
        # первичная таблица
        table: DataFrame = self.__count_games()

        # таблица с забитыми и пропущенными голами
        goals: DataFrame = self.__calculate_goals()

        # таблица с вычисленными победами, ничьими и поражениями
        game_scores: DataFrame = self.__calculate_game_scores()

        # таблица с вычисленными итоговыми очками
        final_scores: DataFrame = self.__calcultate_final_scores()

        scores = game_scores.join(goals).join(final_scores)
        table = table.join(scores)

        table = table.sort_values(by=["О"], ascending=False).reset_index().rename(columns={"index": "Команда"})
        table.index = list(range(1, table.shape[0] + 1))

        return table

    def __count_games(self) -> DataFrame:
        return DataFrame({
            "Игры": self.data["Команда_1"].value_counts() + self.data["Команда_2"].value_counts()})

    def __calculate_goals(self) -> DataFrame:
        goals_1 = DataFrame({
            "Команда": self.teams[0],
            "ЗГ": map(lambda x: x[0], self.score),
            "ПГ": map(lambda x: x[1], self.score)
        }).groupby("Команда").sum()

        goals_2 = DataFrame({
            "Команда": self.teams[1],
            "ЗГ": map(lambda x: x[1], self.score),
            "ПГ": map(lambda x: x[0], self.score)
        }).groupby("Команда").sum()

        return goals_1[["ЗГ", "ПГ"]].add(goals_2[["ЗГ", "ПГ"]])

    def __calculate_game_scores(self) -> DataFrame:
        results_1 = DataFrame({
            "Команда": self.teams[0],
            "В": list(map(lambda x: 1 if x[0] > x[1] else 0, self.score)),
            "Н": list(map(lambda x: 1 if x[0] == x[1] else 0, self.score)),
            "П": list(map(lambda x: 1 if x[0] < x[1] else 0, self.score))
        }).groupby("Команда").sum()

        results_2 = DataFrame({
            "Команда": self.teams[1],
            "В": list(map(lambda x: 1 if x[1] > x[0] else 0, self.score)),
            "Н": list(map(lambda x: 1 if x[1] == x[0] else 0, self.score)),
            "П": list(map(lambda x: 1 if x[1] < x[0] else 0, self.score))
        }).groupby("Команда").sum()

        return results_1[["В", "Н", "П"]].add(results_2[["В", "Н", "П"]])

    def __calcultate_final_scores(self) -> DataFrame:
        table: DataFrame = self.__calculate_game_scores()

        return DataFrame({"О": table["В"] * 3 + table["Н"]})


if __name__ == "__main__":
    championat = Football("csv\\rpl\\13-14.csv")
    # championat.final_table().to_csv("output.csv")
    print(championat.final_table())
