import numpy as np
import pandas as pd

#основной класс
class Footbal:
    def __init__(self, file: str):
        self.data = pd.read_csv(file)
        self.data.to_html("legacy.html")
        self.table = self.__calcultate_final_scores()
        
    def __count_games(self):
        return pd.DataFrame({
            "Игры": self.data["Команда_1"].value_counts() + self.data["Команда_2"].value_counts()}).reset_index().rename(columns={"index": "Команда"
                    })
    
    def __calculate_game_scores(self):
        #Команды, играющие друг против друга
        team_1, team_2 = self.data["Команда_1"], self.data["Команда_2"]

        #Счёт команд
        score = self.data["счёт"]

        #маска для парсинга счета
        mask: list = list(map(lambda number: list(map(int, number[:3].split(":"))), score.to_list()))

        goals_1 = pd.DataFrame({
            "Команда": team_1,
            "Забито": map(lambda x: x[0], mask),
            "Пропущено":  map(lambda x: x[1], mask)
        }).groupby("Команда").sum().reset_index()
        
        # print(goals_1.head(15))
        

        goals_2 = pd.DataFrame({
            "Команда": team_2,
            "Забито": map(lambda x: x[1], mask),
            "Пропущено":  map(lambda x: x[0], mask)
        }).groupby("Команда").sum().reset_index()

        results_1 = pd.DataFrame({
        "Команда": team_1,
        "В": list(map(lambda x: 1 if x[0] > x[1] else 0, mask)),
        "Н": list(map(lambda x: 1 if x[0] == x[1] else 0, mask)),
        "П": list(map(lambda x: 1 if x[0] < x[1] else 0, mask))
        }).groupby("Команда").sum().reset_index()

        results_2 = pd.DataFrame({
            "Команда": team_2,
            "В": list(map(lambda x: 1 if x[1] > x[0] else 0, mask)),
            "Н": list(map(lambda x: 1 if x[1] == x[0] else 0, mask)),
            "П": list(map(lambda x: 1 if x[1] < x[0] else 0, mask))
        }).groupby("Команда").sum().reset_index()
        
        results = results_1[["В", "Н", "П"]].add(results_2[["В", "Н", "П"]])
        goals = goals_1[["Забито", "Пропущено"]].add(goals_2[["Забито", "Пропущено"]])
        
        table = self.__count_games()
        scores = results.join(goals)
        
        return table.join(scores)
        
    def final_table(self):
        self.table = self.table.sort_values(by=["О"], ascending=False)
        self.table.index = list(range(1, self.table.shape[0] + 1))
        return self.table
    
    
    def __calcultate_final_scores(self):
        table: pd.DataFrame = self.__calculate_game_scores()
        
        final_scores = pd.DataFrame({
            "О": table["В"] * 3 + table["Н"]
        })
        
        return table.join(final_scores)
    

if __name__ == "__main__":
    final = Footbal("csv\\rpl\\13-14.csv")
    
    # final.final_table().to_html("test.html")
    print(final.final_table())