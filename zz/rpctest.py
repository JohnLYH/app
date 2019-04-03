# odoorpc测试 前提需要一个odoo服务启动
# 查询数据  需要登录

import odoorpc

# 登录前准备--创建实例
A = odoorpc.ODOO('localhost', port=8069)

# 检查可用数据库列表
print(A.db.list())
# odoo版本号
print(A.version)

# 登录----接下来所有操作的前提
A.login('o1', 'zz', 'zz')

# 查看
print(A.env.context)
print(A.env.lang)
print(A.env.uid)
print(A.env)

# 所有可用报表--按模型分类---然后下载  字节码
print(A.report.list())
r1 = A.report.download('zz.report2', [1])
with open('r1.pdf', 'wb') as report_file:
    report_file.write(r1.read())

# 用户
user = A.env.user
# print(user.name)
# print(user.company_id.name)

# 取得模型代理
people = A.env['zz.peoples']

# 利用模型代理使用模型的方法--查询
p1 = people.browse(1)
print(p1.name)
# 多对多字段结果查询
for sp in p1.petosp:
    print(sp.name)
# 通过外部Id获取某条记录
print(A.env.ref('zz.t1'))

# teacher = A.env['people.teacher']
# ids = teacher.search([])
# for order in teacher.browse(ids):
#     print(order.name,end='--')
#     print(order.age)

# 创建新纪录
# print(people.create({'name':'小屁孩','age':1}))

# 更改某条记录--id为3
people.write([3], {'name': '孙悟空'})

# 多对多字段更改----数据库id 非外部id
p1.petosp = [(6, 0, [2, 3])]

# 另一种查询方式read search create unlink等皆可
user_data = A.execute('zz.peoples', 'read', [user.id])
user_data2 = A.execute('zz.peoples', 'read', [2])
user_data3 = A.execute('zz.peoples', 'read', [2], ['name', 'age'])
# 返回所有字段以及属性  最好过滤
# user_data4= A.execute('zz.peoples', 'fields_get', [])
# 过滤属性
user_data5 = A.execute('zz.peoples', 'fields_get', [], ['string', 'type'])
print(user_data)
print(user_data2[0]['name'])
print(user_data3)
# print(user_data4)
print(user_data5)
