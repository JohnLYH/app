odoo.define('basic_view_ext.select_dialog', function (require) {
    'use strict';
    var core = require('web.core');
    var dialogs = require('web.view_dialogs');

    // 选择表单一对多字段的记录，然后对选中的行执行操作
    var SelectDialog = dialogs.SelectCreateDialog.extend({
        set_buttons: function (buttons) {
            // Dialog执行loadViews之后会执行set_buttons。此时使用find可以找到搜索视图
            var $searchview = this.$el.find('.o_searchview');
            if($searchview.length) {
                $searchview.addClass("hidden");
            }
            return this._super.apply(this, arguments);
        },
    });

    // 在client action的定义中声明了下列变量
    // open_model: 选择对话框列表展示的模型
    // domain: 记录的过滤
    // title: 弹出对话框的标题
    // method: 对选中记录执行的操作，结束一个选中记录的id数组作为参数
    // exec_model: method方法所属的model
    var select_dialog = function (parent, action) {
        new SelectDialog(parent, {
            res_model: action.context.open_model,
            domain: action.context.domain,
            context: action.context,
            title: action.context.title,
            no_create: true,
            readonly: true,
            on_selected: function (records) {
                // 列表选择对话框【选择】按钮的回调方法
                var ids = _.map(records, function(ele) {
                    return ele.id;
                });
                var args = action.context.args || [];
                args.unshift(ids);
                // 这里如果使用this._rpc调用将会无法执行then中的回调
                parent._rpc({
                    model: action.context.exec_model,
                    method: action.context.method,
                    args: args,
                }).then(function(res){
                    if(typeof(res) === 'object'&&res&&res.action_type === 'custom') {
                        parent.do_action(res.action);
                    } else {
                        // 未保存时执行选择调用reload动作将会导致数据不保存
                        // parent.do_action({
                        //     type: 'ir.actions.client',
                        //     tag: 'reload'
                        // });
                        // 直接使用parent.trigger_up('reload')无法刷新表单，必须找到表单组件对象执行才会进行刷新
                        // 事件是向上传递的
                        // parent.getChildren()[2].getChildren()[1].trigger_up('reload');
                        // 执行完方法后对表单视图进行刷新
                        parent.inner_widget.active_view.controller.trigger_up('reload');
                    }
                });
            }
        }).open();
    };
    core.action_registry.add("select_dialog", select_dialog);
});

