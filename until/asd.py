# import re
# n=int(input())
# for x in range(n):
# 	a=input()
# 	if (not re.search(r'[^PAT]',a)) and re.search(r'[A]*P[A]{1}T[A]*',a):
# 		print("YES")
# 	else:
# 		print("NO")



# lists=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# lists = list(map(lambda x:int(x),lists))
# print(lists[1],type(lists[1]))

# n = int(input())
# n_list = input().split()
# n_list = list(map(lambda x:int(x),n_list))
#
# callatz_list = set()
# v =[]
# if n < 100 and n > 0:
#     for i in range(n):
#         x=n_list.pop(0)
#         num = x
#         if num in callatz_list or (num >100 or num <=1):
#             continue
#         v.append(x)
#         while num >1:
#             if num % 2 == 0:
#                 num =num/2
#             else:
#                 num = (3 * num + 1) / 2
#             if num in callatz_list:
#                 break
#             callatz_list.add(num)
#
# for x in v:
#     if x in callatz_list:
#         v.remove(x)
# v.sort(reverse=True)
# v = list(map(lambda x: str(x), v))
# print(' '.join(v))
#5, 8, 4, 2 ,3 ,11, 17, 26, 13, 20, 10
# 6
# 3 5 6 7 8 11
# [[3, 5, 8, 4, 2, 1], [5, 8, 4, 2, 1], [6, 3, 5, 8, 4, 2, 1], [7, 11, 17, 26, 13, 20, 10, 5, 8, 4, 2, 1], [8, 4, 2, 1], [11, 17, 26, 13, 20, 10, 5, 8, 4, 2, 1]]


#
# class FOO(object):
#     def __init__(self):
#         self.name="luo"
#         self.age="123"
#
#     def __str__(self):
#         return self.name
#
#     def  __repr__(self):
#         return self.age
#
# obj=FOO()
# print(obj)
# 有 __str__  和 __repr__  输出 __str__的内容 luo
# 只有 __repr__   输出 __repr__  的内容  123


# F:\Django_project\CRM_Project\stark\static\ExcelTemplate.xlsx
# ExcelTemplate.xlsx
# import os
# print("1",os.path.abspath("ExcelTemplate.xlsx"))
import redis
print("redis")
POOL=redis.ConnectionPool(host='127.0.0.1', port=6379)
CONN=redis.Redis(connection_pool=POOL)

print(CONN.llen("luo"))
print(CONN.set)


# print(1,CONN.llen("lwm"))
# # CONN.delete('lwm')
# CONN.set('lwm',[1,2,3,4,5])
# print(2,CONN.llen("lwm"))
# val=CONN.lpop('lwm')
# print(val)


# print(CONN.llen("lmw_list"))