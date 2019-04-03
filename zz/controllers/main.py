# import logging

from odoo import http
from odoo import modules
from odoo.http import request, local_redirect,content_disposition
import base64
import io
import json,odoo,werkzeug
from urllib.parse import quote,urlencode

# 学生相关--------------------

class ZZpeople(http.Controller):
    # url匹配规则 遵循werkzeug 也可写成<string:page_name>    默认string 或者str
    @http.route('/zz/<int:id>', type='http', auth="public", website=True, )
    # id为本地变量-局部变量 函数参数中要存在
    def sd(self, id, **kw):
        people1 = request.env['zz.peoples'].search([('id', '=', id)])
        vals = {'people': people1}

        # print(request.csrf_token())
        # print(request.session)
        # print(request.context)
        # print(request.uid)
        # print(request.httprequest.cookies.get('session_id'))
        # print(request.httprequest.cookies.get('zz'))
        # print(request.httprequest.method)
        # print(request.httprequest.form)
        # print(request.httprequest.session)
        # print(request.httprequest.headers)

        a = kw.get('firstname')
        b = kw.get('lastname')
        if (a == 'a') and (b == 'b'):
            # 跳转
            return local_redirect('http://www.baidu.com.cn')
            # 退出
            # request.session.logout()
            # request.httprequest.session.logout()
            # return request.not_found(description='bye')

        response = request.render('zz.detail1', vals)
        response.set_cookie('zz', '1')
        # print(response.headers)
        return response

    # Odoo提供了一个特殊的转换器名为model，它在给定ID时直接提供记录 /zz/<model("zz.peoples"):p> 与/zz/<int:id>结果相同 相冲突
    @http.route('/<model("zz.peoples"):p>', type='http', auth="public", website=True)
    def sd1(self, p, **kw):
        vals = {'person': p,}
        return request.render('zz.detail2', vals)


# 老师相关------------------

class ZZteacher(http.Controller):
    # 基本情况
    @http.route('/tp/<name>', type='http', auth="public", website=True)
    def sd1(self, name, **kw):
        teacher = request.env['people.teacher'].search([('name', '=', name)])
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('res_model', '=', 'people.teacher'), ('res_id', '=', teacher.id)], )
        vals = {'fj': attachment, 't': teacher}
        # return request.render('zz.detail3',{'t':teacher})
        return request.render('zz.detail3', vals)

    #json格式请求
    @http.route('/teacher/json', type='json', auth='none')
    def teacher_json(self):
        records = request.env['people.teacher'].sudo().search([])
        return records.read(['name'])


    # 附件查询页
    # @http.route('/down/', type='http', auth="public", website=True,csrf=False)
    # def fj(self,**kw):
    #     tid=kw.get('tid')
    #     attachment= request.env['ir.attachment'].sudo().search_read( [('res_model', '=', 'people.teacher'), ('res_id', '=', tid)], )
    #     # data = attachment[0]["datas"]
    #     vals = {'fj': attachment,}
    #     return request.render('zz.detail4',vals)

    # 已知id时直接展示附件
    @http.route('/zs/<id>', type='http', auth="public", website=True, csrf=False)
    def fj1(self, id, **kw):
        attachment = request.env['ir.attachment'].sudo().search_read([('res_model', '=', 'people.teacher'), ('res_id', '=', id)], )
        vals = {'fj': attachment, }
        return request.render('zz.detail4', vals)

    # 附件下载代码
    @http.route('/td/<id>', type='http', auth="public", website=True, csrf=False)
    def fj2(self, id, **kw):
        attachment = request.env['ir.attachment'].sudo().search_read([('id', '=', int(id))],["name", "datas", "res_model", "res_id", "type","url"])
        if attachment:
            attachment = attachment[0]
        else:
            return local_redirect('/td/<id>')

        if attachment["type"] == "url":
            if attachment["url"]:
                return local_redirect(attachment["url"])
            else:
                return request.not_found()

        elif attachment["datas"]:
            # 不加byteio 报错'bytes' object has no attribute 'seek'
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            # return http.send_file(data, filename=attachment['name'], as_attachment=True)
            return http.send_file(data, filename=quote((attachment['name']), 'utf-8'), as_attachment=True)

            # 名称中文问题解决方法---quote更彻底
            # return http.send_file(data, filename=content_disposition(attachment['name']), as_attachment=True)
            #return http.send_file(data, filename=quote((attachment['name']), 'utf-8'), as_attachment=True)
        else:
            return request.not_found( description='ByeBye')

    # 上传
    @http.route('/up', type='http', auth="public", methods=['POST'], csrf=False)
    def addevent(self, redirect=None, **kw):
        Attachments = request.env['ir.attachment']  # ir.attachment 附件表名
        # data=request.httprequest.files.getlist('up')
        file = request.httprequest.files['up']
        data = file.read()

        attachment = Attachments.create({
            'name': file.filename,
            'datas': base64.b64encode(data),
            'datas_fname': file.filename,
            'public': True,
            'res_model': 'people.teacher'
        })

        return 'OK'

# ------------------------------------
# make_response测试代码
class ZZresponse(http.Controller):
    @http.route('/t1/', type='http', auth='public', csrf=False)
    def avatar(self):
        #至少要有Content-Type
        headers = [('Content-Type', 'image/png')]
        status = 200
        img_path = modules.get_resource_path('zz', 'static/img', 'fj0.png')
        with open(img_path, 'rb') as f:
            image = f.read()
        content = base64.b64encode(image)
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response


#send_file测试代码
class ZZsendfile(http.Controller):
    @http.route('/t2/', type='http', auth='public', csrf=False)
    def export_tmp2(self,**kw):
        img_path = modules.get_resource_path('zz', 'static/img', 'fj0.png')
        #sendfile第一个参数可以为数据 也可以为文件路径
        # with open(img_path, 'rb') as f:
        #     image = f.read()
        # content = base64.b64encode(image)
        # image_path = base64.b64decode(content)
        return http.send_file(img_path, filename='fj0.png')


# 继承修改 qcontext上下文  要有super
from odoo.addons.website.controllers.main import Website

class ZZwebsiteinfo(Website):
    @http.route()
    def website_info(self):
        result = super(ZZwebsiteinfo, self).website_info()
        result.qcontext['apps'] = result.qcontext['apps'].filtered(lambda x: x.name != 'website')
        return result





