from odoo import http
from odoo.http import request, local_redirect,content_disposition
import base64
import io
from odoo import modules
from urllib.parse import quote,urlencode
from odoo.addons.web.controllers.main import ensure_db
import json,odoo,werkzeug

#主页登录---  主父类 ----两种皆可
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import Home
from odoo.addons.bus.controllers.main import BusController

#web.Home-----portal.Home-------website.Website------层层继承

# class Home(Website):
class ZHome(Home):
    # 网站首页登录页面替换为zz.home
    @http.route()
    def index(self, **kw):
        # context = {'session_info': json.dumps(request.env['ir.http'].session_info())}
        # print(context)
        a=request.env['ir.http'].session_info()
        print(a)
        return request.render('zz.home' )


   # 登录逻辑
    @http.route('/web/login', type='http', auth='public')
    def web_login(self, redirect=None, **kw):
        # 验证有无数据库
        ensure_db()

        # 两种方式获取参数
        # values = {}
        values = request.params.copy()

        # POST登录逻辑
        if request.httprequest.method == 'POST':
              # 根据用户名和密码获取uid ---authenticate 参考http.py---返回uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            print('uid:',uid)
            ajax_flag = 'ajax_request' in kw
            if uid is not False:
                if ajax_flag:
                    return json.dumps({'res': 'success'})
               #顺利登录
                print('1', values,kw)
                '''
                def _login_redirect(self, uid, redirect=None):
                    return redirect if redirect else '/web' 形参中redirec >web>web/login
               '''
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                # return http.redirect_with_hash('/')

            #错误登录
            values.update({'err_msg': '&nbsp;* 错误的用户名或者密码！'})
            print('2', values)
            old_active_user = request.env['res.users'].sudo().search([('login', '=', kw['login'])])

            if not old_active_user:
                # 判断用户名是否是已注册未激活
                not_active_user = request.env['res.users'].sudo().with_context(active_test=False).search([('login', '=', request.params['login'])])
                if not_active_user:
                    values.update({'err_msg': '&nbsp;* 邮箱已注册，请登录邮箱进行激活！'})
            if ajax_flag:
                return json.dumps(values)
        if 'confirm' in kw:
            values.update({'msg': '&nbsp;* 激活成功，请输入账户密码进行登录'})

        if redirect == 'http://localhost:8069/zz/signup':
            return request.render('zz.signup')

        #GET请求下默认渲染登录页 返回
        else:
            print('3', values)
            response = request.render('zz.login', values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response


#---------------------------注册验证
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError

class ZZAuthSignupHome(AuthSignupHome):
    # 将odoo注册页跳转到新版注册页
    @http.route('/web/signup')
    def osignup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        return local_redirect('/zz/signup')


    @http.route(['/my', '/my/home'])
    def home(self, **kw):
        return local_redirect('/')


    def _singup_with_confirmation(self, **kw):
        res_users = request.env['res.users']
        values = {
            'login': kw['login'],
            'email': kw['login'],
            'password': kw['password'],
            'name': kw['name']
        }
        new_user = res_users.sudo()._signup_create_user(values)
        new_user.active = True
        new_partner = new_user.partner_id

        # 拼接邮箱确认地址中的重定向参数
        # redirect_url = werkzeug.url_encode({'redirect': kw.get('redirect') or ''})
        # # 为partner准备token
        # new_partner.signup_prepare()
        # signup_url = new_partner.with_context(
        #     signup_force_type_in_url='signup/confirm', signup_valid=True).signup_url
        # if redirect_url != 'redirect=':
        #     signup_url += '&%s' % redirect_url
        # template = request.env.ref('saas_portal_website.email_registration', raise_if_not_found=True)
        # new_partner.with_context(link=signup_url).message_post_with_template(template.id, composition_mode='comment')
        u={'partner_id': new_partner.id, 'user_id': new_user.id}
        return {'partner_id': new_partner.id, 'user_id': new_user.id}

    @http.route('/zz/signup', type='http', auth='public', csrf=False)
    def web_auth_signup(self, *args, **kw):
        # qcontext = self.get_auth_signup_qcontext()
        #
        # if not qcontext.get('token') and not qcontext.get('signup_enabled'):
        #     raise werkzeug.exceptions.NotFound()
        #
        # if 'error' not in qcontext and request.httprequest.method == 'POST':
        #     try:
        #         self.do_signup(qcontext)
        #         # self._singup_with_confirmation(**kw)
        #
        #         # Send an account creation confirmation email
        #         if qcontext.get('token'):
        #             user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
        #             template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
        #                                        raise_if_not_found=False)
        #             if user_sudo and template:
        #                 template.sudo().with_context(
        #                     lang=user_sudo.lang,
        #                     auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
        #                 ).send_mail(user_sudo.id, force_send=True)
        #         return http.redirect_with_hash('/')
        #
        #     except UserError as e:
        #         qcontext['error'] = e.name or e.value
        #     except (SignupError, AssertionError) as e:
        #         if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
        #             qcontext["error"] = _("Another user is already registered using this email address.")
        #         else:
        #             qcontext['error'] = _("Could not create a new account.")

        response = request.render('zz.signup')
        # response = request.render('zz.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # @http.route('/web/signup/confirm', type='http', auth='public')
    # def singnup_using_generated_link(self, *args, **kw):
    #     user = request.env['res.users'].sudo().with_context(active_test=False).search([
    #         ('partner_id.signup_token', '=', kw['token'])])
    #     if user.active:
    #         pass
    #     else:
    #         user.active = True
    #     user.partner_id.email_confirmation = 'done'
    #     # 跳转并触发提示激活成功
    #     return werkzeug.utils.redirect('/web/login?confirm')
