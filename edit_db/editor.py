import sqlite3


class Editor():
    def __init__(self, dbname):
        self.dbname = dbname

    def add_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('INSERT INTO progress_data(user_id) values("{}")'.format(user_id))
        conn.commit()
        conn.close()
        return

    def set_date(self, user_id, initial_date, end_date):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE progress_data SET initial_date=date("{}") WHERE user_id="{}"'.format(initial_date, user_id))
        cur.execute('UPDATE progress_data SET end_date=date("{}") WHERE user_id="{}"'.format(end_date, user_id))
        conn.commit()
        conn.close()
        return

    def set_target(self, user_id, num):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE progress_data SET target={} WHERE user_id="{}"'.format(num, user_id))
        conn.commit()
        conn.close()
        return

    def set_per_day_target(self, user_id, num):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE progress_data SET per_day_target={} WHERE user_id="{}"'.format(num, user_id))
        conn.commit()
        conn.close()
        return

    def set_notification(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE progress_data SET notification=TRUE WHERE user_id="{}"'.format(user_id))
        conn.commit()
        conn.close()
        return

    def check_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM progress_data WHERE user_id="{}"'.format(user_id))
        if (cur.fetchone() is None):
            conn.commit()
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True

    def check_target(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT target FROM progress_data WHERE user_id="{}"'.format(user_id))
        if (cur.fetchone() is None):
            conn.commit()
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True

    def check_per_day_target(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT per_day_target FROM progress_data WHERE user_id="{}"'.format(user_id))
        if (cur.fetchone() is None):
            conn.commit()
            conn.close()
            return False
        conn.commit()
        conn.close()
        return True

    def del_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('DELETE FROM progress_data WHERE user_id="{}"'.format(user_id))
        conn.commit()
        conn.close()
        return

    def get_data(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM progress_data WHERE user_id="{}"'.format(user_id))
        data = cur.fetchone()
        conn.commit()
        conn.close()
        return data
