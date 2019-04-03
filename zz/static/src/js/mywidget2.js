odoo.define('zz.mywidgets', function (require) {

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');

    var FieldMany2OneButtons = AbstractField.extend({

        template: 'FieldMany2OneButtons',


        //rpc查询服务器中的数据  而非硬编码
        willStart: function () {
            var deferred = $.Deferred();
            var self = this;
            self.user_list = {};
            this._rpc({
                //也可model:this.field.relation,
                model: 'people.teacher',
                method: 'search_read',
                fields: ['display_name'],
                domain: this.field.domain,
            }).then(function (records) {
                _.each(records, function (record) {
                    self.user_list[record.id] = record;
                    self.user_list[record.id].name = record.display_name;
                });
                deferred.resolve();
            });
            return jQuery.when(this._super.apply(this, arguments), deferred
            );
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