import sqlite3

class Timechanger:
    def __init__(self):
        # self.conn = sqlite3.connect(r'ebn_bot/db.db')
        # self.cursor = self.conn.cursor()
        pass

    def change_reminde_time_a(self, remind_time, user_id):
        self.conn = sqlite3.connect(r'ebn_bot/db.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"UPDATE remind_table SET time = '{remind_time}' WHERE id = '{user_id}'")
        
        self.conn.commit()
        self.conn.close()


