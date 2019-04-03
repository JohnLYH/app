import base64
import re
import string
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import xlrd

RE_DATE = re.compile(r"(\d{4}-\d{1,2}-\d{1,2})")


class ImportData(models.TransientModel):
    # 信息导入
    _name = 'import.data'
    import_file = fields.Binary(string='请选择要导入的文件', required=True)

    def import_data(self, res_dict, *args):
        model_str = res_dict['model_name']
        verify_dict = res_dict['verify_dict']
        error_msg = res_dict['error_msg']
        default_fields = res_dict['default_fields']
        import_fields = res_dict['import_fields']
        verify_function = res_dict['verify_function']
        res_model = self.env[model_str]
        sh = args[0]
        start_row = 2

        for row_index in range(start_row, sh.nrows):
            row_value = sh.row_values(row_index)
            values = {}
            for field, val in zip(import_fields, row_value):
                if isinstance(val, str):
                    val = val.strip()
                func_name = verify_function.get(field)
                if func_name:
                    func_val = getattr(self, func_name)
                    val = func_val(field, val, row_index + 1, verify_dict, error_msg)
                values.update({field: val})
            res = res_model.default_get(default_fields)
            res.update(values)
            self.create_data(res_model, res)

        return True

    @staticmethod
    def create_data(res_model, resource):
        res = res_model.sudo().search([('id', '=', int(resource.pop('id')))], limit=1)
        if res:
            print('更新', resource)
            res.update(resource)
        else:
            print('创建', resource)
            res_model.create(resource)

    @staticmethod
    def val_verify(field, value, row_index, verify_dict, error_msg, *args):
        if not value:
            return value
        valid_dict = verify_dict.get(field)
        if value not in valid_dict:
            print(field, value)
            raise UserError('第{0}行{1}'.format(row_index, error_msg.get(value)))
        return valid_dict.get(value)

    @staticmethod
    def re_verify(field, value, row_index, verify_dict, error_msg, *args):
        if not value:
            return value
        re_expression = verify_dict.get(field)
        if not re.match(re_expression, str(value)):
            print(field, value)
            raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
        return value

    @staticmethod
    def require_verify(field, value, row_index, verify_dict, error_msg, *args):
        if not value:
            raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
        return value

    def id_verify(self, field, value, row_index, verify_dict, error_msg, *args):
        value = self.require_verify(field, value, row_index, verify_dict, error_msg, args)
        try:
            value = int(value)
        except Exception:
            raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
        return value

    # 关联字段 name 不可能出现重复时，返回ID
    def related_verify(self, field, value, row_index, verify_dict, error_msg, *args):
        if not value:
            return value
        related_model = verify_dict.get(field)
        value_id = self.env[related_model].search([('name', '=', value)], limit=1).id
        if not value_id:
            raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
        return value_id

    # 如果所关联字段 name 可能出现重复名称时,先搜索名称再验证id
    def repeat_related_verify(self, field, value, row_index, verify_dict, error_msg, *args):
        if not value:
            return value
        related_model = verify_dict.get(field)
        value_str, value_id = value.split('-')
        values = self.env[related_model].search([('name', '=', value_str)]).id
        if not values:
            raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
        if len(values) > 1:
            tmp_id = None
            for val in values:
                if val == value_id:
                    tmp_id = value_id
                    break
            if not tmp_id:
                raise UserError('第【{0}】行，{1}'.format(row_index, error_msg.get(field)))
            return tmp_id
        else:
            return values


hr_employee_res = {
    'model_name': 'hr.employee',
    'verify_dict': {
        'department_id': 'hr.department',
        'birthday': RE_DATE,
        'hire_date': RE_DATE,
        'trial_end_date': RE_DATE,
        'trial_start_date': RE_DATE,
        'residence_zip_code': re.compile(r'\d{6}'),
        'home_zip_code': re.compile(r'\d{6}'),
        'mobile_phone': re.compile(r"0?(1|13|14|15|17|18|19)[0-9]{9}"),
        'work_email': re.compile(
            r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"),
        'identification_id': re.compile(r'^(\d{6})(\d{4})(\d{2})(\d{2})(\d{3})([0-9]|X)$'),
        'marital': {
            '单身': 'single',
            '已婚': 'married',
            '非单身': 'cohabitant',
        },
        'political_status': {
            '群众': '0',
            '中共党员': '1',
            '中共预备党员': '2',
            '共青团员': '3',
            '民革党员': '4',
            '民盟盟员': '5',
            '民建会员': '6',
            '民进会员': '7',
            '农工党党员': '8',
            '致公党党员': '9',
            '九三学社社员': '10',
            '台盟盟员': '11',
            '无党派人士': '12',
        },
        'gender': {
            '男': 'male',
            '女': 'female',
        },
        'job_title': {
            '高级': 'senior',
            '中级': 'intermediate',
            '初级': 'junior',
            '无': 'normal',
        },
        'degree': {
            '小学': '0',
            '初中': '1',
            '高中': '2',
            '中专': '3',
            '职校': '4',
            '中技': '5',
            '专科': '6',
            '本科': '7',
            '硕士': '8',
            '博士': '9',
            '无': '10',
        },
        'native_place_type': {
            '非农业户口': '1',
            '农业户口': '0',
        },
    },
    'error_msg': {
        'id': '部门id错误类型填写错误',
        'name': '名字没有填写',
        'marital': '婚姻状况输入错误',
        'gender': '性别输入错误',
        'political_status': '政治面貌输入错误',
        'degree': '最高学历输入错误',
        'native_place_type': '户籍性质输入错误',
        'mobile_phone': '移动电话输入错误',
        'date': '日期格式输入错误',
        'birthday': '出生日期输入错误',
        'department_id': '系统内无该部门名称',
        'job_title': '职称填写错误',
        'work_email': '邮箱填写错误',
        'trial_start_date': '试用期开始日期填写错误',
        'residence_zip_code': '户籍邮编格式输入错误',
    },
    'default_fields': [
        "gender",
        "marital",
        "trial_type",
    ],
    'import_fields': [
        'id',
        'name',
        'birthday',
        'marital',
        'political_status',
        'gender',
        'job_title',
        'identification_id',
        'native_place',
        'degree',
        'ethnic',
        'criminal_record',
        'medical_history',
        'mobile_phone',
        'work_email',
        'emergency_contact',
        'kinship',
        'emergency_tel',
        'native_place_type',
        'residence_address',
        'residence_zip_code',
        'residence_tel',
        'address_home',
        'home_zip_code',
        'home_tel',
        'department_id',
        'trial_start_date',
        'trial_length',
        'trial_end_date',
        'hire_date',
    ],
    'verify_function': {
        'id': 'id_verify',
        'department_id': 'related_verify',
        'name': 'require_verify',
        'birthday': 're_verify',
        'marital': 'val_verify',
        'political_status': 'val_verify',
        'gender': 'val_verify',
        'job_title': 'val_verify',
        'identification_id': 're_verify',
        'degree': 'val_verify',
        'mobile_phone': 're_verify',
        'work_email': 're_verify',
        'native_place_type': 'val_verify',
        'residence_zip_code': 're_verify',
        'home_zip_code': 're_verify',
        'trial_start_date': 're_verify',
        'trial_end_date': 're_verify',
        'hire_date': 're_verify',
    }
}

hr_department_res = {
    'model_name': 'hr.department',
    'verify_dict': {
        'parent_id': 'hr.department',
        'department_type': {
            '管理部门': 'management',
            '仓储中心': 'warehousing',
            '采购': 'Purchasing',
            '销售': 'sales',
            '生产中心': 'Production',
        }
    },
    'error_msg': {
        'id': '部门id错误类型填写错误',
        'name': '部门名字没有填写',
        'parent_id': '系统内无上级部门名称',
        'department_type': '部门属性没有填写'
    },
    'default_fields': [
        'active',
        'company_id',
        'status',
    ],
    'import_fields': [
        'id',
        'name',
        'department_type',
        'parent_id',
    ],
    'verify_function': {
        'id': 'id_verify',
        'name': 'require_verify',
        'department_type': 'val_verify',
        'parent_id': 'related_verify',
    },
    'import_data_name': [],
    'depends': 'hr.department'
}

hr_education_res = {
    'model_name': 'biote.hr.education',
    'verify_dict': {
        'start_date': RE_DATE,
        'end_date': RE_DATE,
        'full_time_school': {
            "全日制": "1",
            "非全日制": "2",
        },
        'degree': {
            '小学': '0',
            '初中': '1',
            '高中': '2',
            '中专': '3',
            '职校': '4',
            '中技': '5',
            '专科': '6',
            '本科': '7',
            '硕士': '8',
            '博士': '9',
            '无': '10',
        },
        'employee_id': 'hr.employee'
    },
    'error_msg': {
        'start_date': '结束日期输入错误',
        'end_date': '结束日期输入错误',
        'degree': '学历输入错误'
    },
    'default_fields': [
    ],
    'import_fields': [
    ],
    'verify_function': {
    },
}
hr_training_res = {
    'model_name': 'biote.hr.training',
    'verify_dict': {
    },
    'error_msg': {
    },
    'default_fields': [
    ],
    'import_fields': [
    ],
    'verify_function': {
    },

}
hr_work_exp_res = {
    'model_name': 'biote.hr.work.exp',
    'verify_dict': {
    },
    'error_msg': {
    },
    'default_fields': [
    ],
    'import_fields': [
    ],
    'verify_function': {
    },
}
hr_family_res = {
    'model_name': 'biote.hr.family',
    'verify_dict': {
    },
    'error_msg': {
    },
    'default_fields': [
    ],
    'import_fields': [
    ],
    'verify_function': {
    },
}
model_res = {
    '部门数据': hr_department_res,
    '员工数据': hr_employee_res,
    '教育经历': hr_education_res,
    '培训经历': hr_training_res,
    '工作履历': hr_work_exp_res,
    '直系亲属情况': hr_family_res,
}


class ImportHrData(ImportData):
    # 信息导入
    _name = 'import.hr.data'

    @api.one
    def import_hr_employee(self):
        self.import_date(hr_employee_res)

    @api.one
    def import_hr_department(self):
        self.import_date(hr_department_res)

    @api.one
    def import_unicorn_data(self):
        file_contents = base64.decodebytes(self.import_file)
        wb = xlrd.open_workbook(file_contents=file_contents)
        sheets = wb.sheets()
        print([x.name for x in sheets])
        for sh in sheets:
            res_dict = model_res.get(sh.name)
            if not res_dict:
                raise UserError('导入表格【sheet:{0}】名称有误'.format(sh.name))
            self.import_data(res_dict, sh)
