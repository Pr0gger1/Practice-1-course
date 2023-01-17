import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
# from sys import argv


class Football:
    def __init__(self, filename: str):
        self.data = pd.read_csv(filename)
        self.score = self.data["счёт"].apply(lambda s: list(map(int, s[:3].split(":"))))

    def get_scores(self):
        # подсчёт забитых мячей для столбца "Команда_1"
        goals1 = DataFrame({
            "Команда": self.data["Команда_1"],
            "Забито": self.score.apply(lambda count: count[0])
        }).groupby("Команда").sum()

        # подсчёт забитых мячей для столбца "Команда_2"
        goals2 = DataFrame({
            "Команда": self.data["Команда_2"],
            "Забито": self.score.apply(lambda count: count[1])
        }).groupby("Команда").sum()

        return (goals1.add(goals2)).reset_index().rename(columns={"index": "Команда"})


class DrawPlot:
    def __init__(self, datatable: DataFrame):
        self.datatable = datatable

    def create_plot(self):
        # абсцисса графика
        teams: pd.Series = self.datatable["Команда"]
        # ордината графика
        balls: pd.Series = self.datatable["Забито"]

        # Подписи и размер холста
        plt.figure(figsize=(25, 5))
        plt.xlabel("Команды")
        plt.ylabel("Кол-во мячей")
        plt.title(f"Общее кол-во заброшенных мячей командами (сезон {years})", fontsize=24)

        # вычисление цвета для каждого столбика в зависимости от кол-ва заброшенных мячей
        def compute_color(value: int) -> str:
            color = "#4de94d"
            if value <= balls.min() + 5:
                color = "#ff464d"
            elif balls.min() + 5 < value <= balls.mean():
                color = "#ffff00"
            return color

        colors: pd.Series = balls.apply(compute_color)

        # инициализируем гистограмму
        bars = plt.bar(
            teams, balls, width=0.6,
            color=colors, edgecolor="black",
            alpha=0.7, linewidth=2
        )

        # метка с кол-вом мячей на каждый столбик
        plt.bar_label(bars, balls, fontsize=12)

        return plt.show()


directory = "csv\\rpl"
years = input("Введите годы сезона (пример: 14-15): ")
# years = argv[1]
file = f"{directory}\\{years}.csv"

try:
    championship = Football(file)
    table = championship.get_scores()
    # print(table)
    count_of_balls_graphic = DrawPlot(table).create_plot()
except FileNotFoundError:
    print("Файл не существует!")
