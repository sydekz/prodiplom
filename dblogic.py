import sqlalchemy
import settings

class VkDB:
    dbuser = settings.VK_TINDER_DB_USER
    dbpass = settings.VK_TINDER_DB_PASS
    ip = settings.VK_TINDER_DB_IP
    port = settings.VK_TINDER_DB_PORT
    dbname = settings.VK_TINDER_DB_NAME

    def __init__(self):
        db = f'postgresql://{self.dbuser}:{self.dbpass}@{self.ip}:{self.port}/{self.dbname}'
        engine = sqlalchemy.create_engine(db)
        self.connection = engine.connect()

        ss = self.create_tbl()

    def create_tbl(self):
        ss = self.connection.execute("""
        create table if not exists VkIdUsers3 (
        	Id serial primary key,
        	VkId integer not null,
        	VkUserId integer not null
        );
        """)

        return ss

    def get_users_list(self, vkid):
        '''Возвращает массив с ID пользователей, которые уже показывались пользователю'''
        ss = self.connection.execute(f"""
        SELECT * from vkidusers3
        WHERE vkid = {vkid}
        """).fetchall()

        users_list = list()
        for element in ss:
            users_list.append(element[2])

        return list(set(users_list))

    def insert_users_list(self, vkid, *args):
        '''Добавляет в базу список людей, которые уже показывались данном vkid'''
        for num in args:
            ss = self.connection.execute(f"""
            INSERT INTO VkIdUsers3(VkId, VkUserId)
            VALUES
            ({vkid}, {num});
                                        """)

    def clear(self):
        ss = self.connection.execute("""
            DROP TABLE IF EXISTS vkidusers3
        """)

        ss = self.create_tbl()

        return ss





