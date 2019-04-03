odoo.define('biote_partner.customer_excel_tmpl_export', function (require) {
'use strict';
//引入web.core的类,赋值给core这个变量
var core = require('web.core');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var customer_excel_tmpl_export = function() {
    // 下载过程中使当前界面不可操作
    framework.blockUI();
    session.get_file({
        url: '/customer/export_tmpl',
        complete: framework.unblockUI,
        error: crash_manager.rpc_error.bind(crash_manager),
    });
}

core.action_registry.add("customer_excel_tmpl_export", customer_excel_tmpl_export);

});