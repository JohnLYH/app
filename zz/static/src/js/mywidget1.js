odoo.define('zz.mywidgets', function (require) {

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var FieldMany2OneButtons = AbstractField.extend({

        //与原始版本最大不同 dom元素在模板中已经写好
        template: 'FieldMany2OneButtons',


        //初始化 参考类初始化
        init: function () {
            this._super.apply(this, arguments);
            this.user_list = {
                1: {name: '张三',},
                4: {name: '李四',},
            };
        },

        //事件选择器 映射以下定义的回调函数
        events: {'click .btn': '_button_clicked',},

        //重写render  渲染dom元素
        _render: function () {
            this.renderElement();
        },

        _button_clicked: function (e) {
            this._setValue(parseInt(jQuery(e.target).attr('data-id')));
        },


    });
    registry.add('many2one_buttons', FieldMany2OneButtons);
    return {FieldMany2OneButtons: FieldMany2OneButtons,}
});