import redis
from crm import models

POOL=redis.ConnectionPool(host='127.0.0.1', port=6379)
CONN=redis.Redis(connection_pool=POOL)
class AutoSale(object):
    @classmethod
    def fetch_users(cls):
        # [obj(销售顾问id,num),obj(销售顾问id,num),obj(销售顾问id,num),obj(销售顾问id,num),]
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
            CONN.set('lmwlist',v) #把列表发送的服务器的Redis上
            CONN.set('lmworigin',v)
            print("v",v)
            return True
        return False

    @classmethod
    def get_sale_id(cls):
        sale_id_origin_count = CONN.llen("lmworigin")
        print("sale_id_origin_count",sale_id_origin_count)
        if not sale_id_origin_count:
            status=cls.fetch_users()
            if not status:
                return None
        user_id = CONN.lpop("lmwlist")
        if user_id:
            return user_id
        reset = CONN.get("lmwreset")

        if reset:
            CONN.delete("lmworigin")
            status=cls.fetch_users()
            if status:
                return None
            CONN.delete("lmwreset")
            return CONN.lpop("lmwlist")
        else:
            for i in range(sale_id_origin_count):
                v = CONN.lindex("lmworigin",i)
                CONN.rpush("lmwlist",v)
            return CONN.lpop("lmwlist")

    @classmethod
    def reset(cls):
        CONN.set("lmwreset",1)

    @classmethod
    def rollback(cls,pid):
        CONN.lpush("lmwlist",pid)

