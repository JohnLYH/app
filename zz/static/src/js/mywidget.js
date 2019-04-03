odoo.define('zz.mywidgets', function (require) {
    // 原始版本
    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var FieldMany2OneButtons = AbstractField.extend({

        //为小部件的根div元素设置CSS类: widget.tagname api属性-id,classname,attributes等
        className: 'oe_form_field_many2one_buttons',

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
            var self = this;

            //Widget.$el仅在启动生命周期方法后可用
            this.$el.empty();
            //迭代用户列表
            _.each(this.user_list, function (description, id) {
                self.$el.append(jQuery('<button>').attr({
                        'data-id': id,
                        'class': 'btn btn-default btn-sm',
                    })
                        .text(description.name)
                        .toggleClass(
                            'btn-primary',
                            self.value ? self.value.res_id == id : false
                        )
                );
            });
            this.$el.find('button').prop('disabled', this.mode == 'readonly');
        },

        _button_clicked: function (e) {
            this._setValue(parseInt(jQuery(e.target).attr('data-id')));
        },


    });
    //注册
    registry.add('many2one_buttons', FieldMany2OneButtons);
    return {FieldMany2OneButtons: FieldMany2OneButtons,}
});