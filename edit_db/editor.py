import sqlite3


class Editor():
    def __init__(self, dbname, data_table, work_table):
        self.dbname = dbname
        self.data_table = data_table
        self.work_table = work_table

    def add_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('INSERT INTO {}(user_id) values("{}")'.format(self.data_table, user_id))
        cur.execute('INSERT INTO {}(user_id) values("{}")'.format(self.work_table, user_id))
        conn.commit()
        conn.close()
        return

    def set_date(self, user_id, initial_date, end_date):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE {} SET initial_date=date("{}") WHERE user_id="{}"'.format(self.data_table, initial_date, user_id))
        cur.execute('UPDATE {} SET end_date=date("{}") WHERE user_id="{}"'.format(self.data_table, end_date, user_id))
        conn.commit()
        conn.close()
        return

    def set_target(self, user_id, num):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE {} SET target={} WHERE user_id="{}"'.format(self.data_table, num, user_id))
        conn.commit()
        conn.close()
        return

    def set_notification(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE {} SET notification=TRUE WHERE user_id="{}"'.format(self.data_table, user_id))
        conn.commit()
        conn.close()
        return

    def unset_notification(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE {} SET notification=FALSE WHERE user_id="{}"'.format(self.data_table, user_id))
        conn.commit()
        conn.close()
        return

    def check_date(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT initial_date, end_date FROM {} WHERE user_id="{}"'.format(self.data_table, user_id))
        is_in = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
        if (is_in == (None, None)):
            return False
        return True

    def check_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM {} WHERE user_id="{}"'.format(self.data_table, user_id))
        is_in = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
        if (is_in is None):
            return False
        return True

    def check_target(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT target FROM {} WHERE user_id="{}"'.format(self.data_table, user_id))
        is_in = cur.fetchone()[0]
        cur.close()
        conn.commit()
        conn.close()
        if (is_in == 'NONE'):
            return False
        return True

    def del_user(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('DELETE FROM {} WHERE user_id="{}"'.format(self.data_table, user_id))
        conn.commit()
        conn.close()
        return

    def get_data(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT * FROM {} WHERE user_id="{}"'.format(self.data_table, user_id))
        data = cur.fetchone()
        conn.commit()
        conn.close()
        return data

    def set_work_target(self, user_id, cum):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('UPDATE {} SET target="{}" WHERE user_id="{}"'.format(self.work_table, cum, user_id))
        conn.commit()
        conn.close()
        return

    def set_work(self, user_id, days):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        default = ','.join(map(str, [0]*days))
        cur.execute('UPDATE {} SET day_work="{}" WHERE user_id="{}"'.format(self.work_table, default, user_id))
        cur.execute('UPDATE {} SET cumulative="{}" WHERE user_id="{}"'.format(self.work_table, default, user_id))
        conn.commit()
        conn.close()
        return

    def update(self, user_id, num_work, index):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT day_work, cumulative FROM {} WHERE user_id="{}"'.format(self.work_table, user_id))
        data = cur.fetchone()
        day_work = list(map(float, data[0].split(',')))
        day_work[index] = num_work
        cum = list(map(float, data[1].split(',')))
        if index == 0:
            cum[0] = num_work
        else:
            cum[index] = cum[index - 1] + num_work
        cum[index:] = [cum[index]]*(len(cum) - index)
        str_day_work = ','.join(map(str, day_work))
        str_cum = ','.join(map(str, cum))
        cur.execute('UPDATE {} SET day_work="{}" WHERE user_id="{}"'.format(self.work_table, str_day_work, user_id))
        cur.execute('UPDATE {} SET cumulative="{}" WHERE user_id="{}"'.format(self.work_table, str_cum, user_id))
        conn.commit()
        conn.close()
        return day_work, cum

    def get_work_target(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT target FROM {} WHERE user_id="{}"'.format(self.work_table, user_id))
        data = cur.fetchone()
        conn.commit()
        conn.close()
        return list(map(float, data[0].split(',')))

    def get_work_cumulative(self, user_id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute('SELECT cumulative FROM {} WHERE user_id="{}"'.format(self.work_table, user_id))
        data = cur.fetchone()
        conn.commit()
        conn.close()
        return list(map(float, data[0].split(',')))
