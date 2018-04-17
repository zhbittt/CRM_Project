import redis

print("redis")
POOL=redis.ConnectionPool(host='127.0.0.1', port=6379)
CONN=redis.Redis(connection_pool=POOL)
class AutoSale(object):
    @classmethod
    def fetch_users(cls):
        if 1:
            CONN.rpush('aa',*[7,1,2,9,3,3,5])
            CONN.rpush('aaorigin',*[7,1,2,9,3,3,5])

            return True
        return False

    @classmethod
    def get_sale_id(cls):
        sale_id_origin_count = CONN.llen("aaorigin")
        if not sale_id_origin_count:
            status=cls.fetch_users()
            if not status:
                return None
        user_id = CONN.lpop("aa")
        if user_id:
            return user_id
        reset = CONN.get("cc")

        if reset:
            CONN.delete("aaorigin")
            status=cls.fetch_users()
            if status:
                return None
            CONN.delete("cc")
            return CONN.lpop("aa")
        else:
            for i in range(sale_id_origin_count):
                v = CONN.lindex("aaorigin",i)
                CONN.rpush("aa",v)
            return CONN.lpop("aa")

    @classmethod
    def reset(cls):
        CONN.set("cc",1)

    @classmethod
    def rollback(cls,pid):
        CONN.lpush("aa",pid)


for x in range(6):
    val=AutoSale.get_sale_id()
    print(val,type(val))
    numid = int(val)
    print(numid ,type(numid))
