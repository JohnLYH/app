// import_export_excel 该模块名称
// export_excel_tmpl 功能名称(没有实际意义)
odoo.define('biote_hr.export_hr_employee_tmpl', function (require) {
    "use strict";
    var core = require('web.core');  // odoo前端框架的核心模块，自定义的客户端动作需要添加到模块的动作注册表中
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');
    var session = require('web.session');

    var export_hr_employee_tmpl = function () {
        // 下载过程中使当前界面不可操作
        framework.blockUI();
        session.get_file({
            url: '/get_biote_hr_employee_template',
            complete: framework.unblockUI,
            error: crash_manager.rpc_error.bind(crash_manager),
        });
    }
// 将动作注册到odoo前端框架中，第一个参数对应xml文件中的tag, 第二个value是var声明的方法
    core.action_registry.add("export_hr_employee_tmpl", export_hr_employee_tmpl);
});
