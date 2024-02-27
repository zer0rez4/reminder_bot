import matplotlib.pyplot as plt
import sqlite3

from numpy import average

class Graph():
    def __init__(self) -> None:
        pass

    def draw_graph_all_time(self, user_id):
        day = []
        stat_list = []
    
        self.connection = sqlite3.connect(r"ebn_bot/db.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(f"SELECT * FROM t_{user_id}")
        all_stat = self.cursor.fetchall()

        self.connection.close()

        for i in all_stat:
            day.append(i[0][5::])
            stat_list.append(i[1])

        plt.xlabel("Дата")
        plt.ylabel("Длительность занятий")
        plt.title("Статистика за всё время")

        plt.bar(day, stat_list)
        plt.axhline(round(average(stat_list), 1), color = 'green')
        plt.savefig(f'g_{user_id}')
        plt.close()


    def draw_graph(self, user_id, days):
        day = []
        month_stat_list = []

        self.connection = sqlite3.connect(r"ebn_bot/db.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(f"SELECT * FROM t_{user_id} ORDER BY day DESC LIMIT {days}")
        result = self.cursor.fetchall()

        self.connection.close()

        for i in result:
            day.append(i[0][5::])
            month_stat_list.append(i[1])

        plt.xlabel("Дата")
        plt.ylabel("Длительность занятий")
        if days == 7:
            plt.title("Статистика на неделю")
        elif days == 30:
            plt.title("Статистика на месяц")

        plt.bar(day, month_stat_list)
        plt.axhline(y=round(average(month_stat_list), 1), color = 'green')
        plt.savefig(f'g_{user_id}')
        plt.close()