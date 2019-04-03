odoo.define('form_no_edit.form_no_edit', function(require){
    var FormController = require('web.FormController');
    var Domain = require('web.Domain');

    FormController.include({
        _onBounceEdit: function () {
            // FormRender中的_onclick方法会触发该事件
            // 当表单处于查看状态时，点击字段所在的tr标签，触发编辑按钮的弹跳动作
            if(this._isHideEditButton()) {
                return;
            }
            // this.$buttons.find('.o_form_button_edit').odooBounce();
            return this._super.apply(this, arguments);
        },
        _isHideEditButton: function() {
            var record = this.model.get(this.handle),
            actionCtx = record.getContext(),
            evalContext = record.evalContext;
            var isHidden = false;
            if (actionCtx.form_no_edit){
                isHidden = new Domain(actionCtx.form_no_edit).compute(evalContext);
            }
            return isHidden;
        },
        toggleEditButtons: function(){
            // 从表单中进入一个关系字段的form视图时，this.$buttons为undefined
            if (this._isHideEditButton() && this.$buttons) {
                if (this.mode === 'edit') {
                    // 本条可编辑，进入编辑状态后，通过pager切换时，取消编辑状态（界面的放弃按钮）
                    // form视图的mode
                    // * edit：进入编辑状态
                    // * readonly：查看状态，未点击编辑按钮
                    this.$buttons.find('.o_form_button_cancel').trigger('click');                    
                }                
                this.$buttons.find('.o_form_button_edit').hide();
            } else {
                if (this.mode === 'readonly' && this.$buttons) {
                    this.$buttons.find('.o_form_button_edit').show();
                }
            }
        },
        renderButtons: function(){
            // 从别的menu item访问到这边, 并且进入到form view
            // console.log('render buttons');
            this._super.apply(this, arguments);
            this.toggleEditButtons();
        },
        reload: function(){
            // 1. 从tree视图中点击一行数据进入form时
            // 2. form view 下，通过pager切换上一条，下一条时
            var self = this;
            // console.log('reload record');
            return this._super.apply(this, arguments).then(function(res){
                self.toggleEditButtons();
                return res;
            });
        },
        saveRecord: function() {
            // 保存记录时会调用该方法
            var self = this;
            return this._super.apply(this, arguments).then(function(res){
                self.toggleEditButtons();
                return res;
            });
        }
    });
});
