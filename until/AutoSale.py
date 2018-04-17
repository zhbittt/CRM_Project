import redis
from redis import Redis


from crm import models

print("redis")
POOL=redis.ConnectionPool(host='127.0.0.1', port=6379)
CONN=redis.Redis(connection_pool=POOL)
class AutoSale(object):
    @classmethod
    def fetch_users(cls):
        [obj(销售顾问id,num),obj(销售顾问id,num),obj(销售顾问id,num),obj(销售顾问id,num),]
        sales = models.SaleRank.objects.all().order_by('-weight')
        sale_list=[]
        n = 0
        for sale in sales:
            num = sale.num
            if num > n:
                n = num
            sale_list.append([sale.user_id,num])
        v = []
        for i in range(n):
            for sale in sale_list:
                if sale[1]>0:
                    v.append(sale[0])
                    sale[1] -= 1

        if v:
            CONN.rpush('lmw_list',*v) #把列表发送的服务器的Redis上
            CONN.rpush('lmw_origin',*v)

            return True
        return False

    @classmethod
    def get_sale_id(cls):
        sale_id_origin_count = CONN.llen("lmw_origin")
        if not sale_id_origin_count:
            status=cls.fetch_users()
            if not status:
                return None
        user_id = CONN.lpop("lmw_list")
        if user_id:
            return int(user_id)
        reset = CONN.get("lmw_reset")

        if reset:
            CONN.delete("lmw_origin")
            status=cls.fetch_users()
            if status:
                return None
            CONN.delete("lmw_reset")
            return CONN.lpop("lmw_list")
        else:
            for i in range(sale_id_origin_count):
                v = CONN.lindex("lmw_origin",i)
                CONN.rpush("lmw_list",v)
            return CONN.lpop("lmw_list")

    @classmethod
    def reset(cls):
        CONN.set("lmw_reset",1)

    @classmethod
    def rollback(cls,pid):
        CONN.lpush("lmw_list",pid)


