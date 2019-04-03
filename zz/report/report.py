from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.zz.report2'

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['people.teacher'].browse(docids)

        # 传入报表中一个词典 键值对以qweb形式在报表中渲染
        # fields_get无参数则获取所有字段名称及属性 参数为字段名列表
        fields = self.env['people.teacher'].fields_get(['age'])

        # 原始sql查询--env后不要跟任何model名
        query = "SELECT name FROM people_teacher"
        self.env.cr.execute(query)
        res = self.env.cr.dictfetchall()

        mystr = '这是用来测试自定义报表内容的一句话'

        return {'docs': docs,
                'mystr': mystr,
                'fields': fields,
                'res': res}
