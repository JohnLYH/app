odoo.define('mrp_bom_hierarchy.mrp_bom_hierarchy', function (require) {
'use strict';

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;

var mrp_bom_hierarchy = Widget.extend(ControlPanelMixin, {
    events: {
        'click .o_bom_hierarchy_unfoldable': 'fold',
        'click .o_bom_hierarchy_foldable': 'unfold',
        'click .o_bom_hierarchy_web_action': 'boundLink'
    },
    init: function(parent, action) {
        this.actionManager = parent;
        this.given_context = {};
        this.given_context.active_id = action.context.active_id;
        return this._super.apply(this, arguments);
    },
    willStart: function() {
        return this.get_html();
    },
    start: function() {
        //this.set_html();
        this.$el.html(this.html);
        return this._super();
    },
    update_cp: function() {
        var status = {
            // 面包屑导航
            breadcrumbs: this.actionManager.get_breadcrumbs()
        };
        return this.update_control_panel(status);
    },
    // 点击控制面板回到该部件时会触发该方法
    do_show: function() {
        this._super();
        this.update_cp();
    },
    get_html: function() {
        var self = this;
        var defs = [];
        return this._rpc({
                model: 'mrp.bom',
                method: 'get_bom_hierarchy_html',
                args: [self.given_context],
            })
            .then(function (res) {
                self.html = res.html;
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
    },
    fold: function(e) {
        function bom_line_fold(child_line_ids) {
            _.each(child_line_ids, function(child_id){
                var $cur_tr = $("#tr_"+child_id);
                $cur_tr.css('display', 'none');
                // 改变箭头方向(下->右),
                $cur_tr.find('span.o_bom_hierarchy_unfoldable').replaceWith(QWeb.render("bom_hierarchy_foldable"));
                var _child_line_ids = $cur_tr.data('child-line-ids');
                bom_line_fold(_child_line_ids);
            })
        }
        var child_line_ids = $(e.target).parents('tr').data('child-line-ids');
        bom_line_fold(child_line_ids);
        // 更改箭头方向
        $(e.target).parents('tr').find('span.o_bom_hierarchy_unfoldable').replaceWith(QWeb.render("bom_hierarchy_foldable"));
    },
    unfold: function(e) {
        var child_line_ids = $(e.target).parents('tr').data('child-line-ids');
        _.each(child_line_ids, function(child_id) {
            var $cur_tr = $("#tr_"+child_id);
            // 这里不能使用block, 会破坏tr的样式
            $cur_tr.css('display', '');
        })
        $(e.target).parents('tr').find('span.o_bom_hierarchy_foldable').replaceWith(QWeb.render("bom_hierarchy_unfoldable"));
    },
    boundLink: function(e) {
        var res_model = $(e.target).parents('a').data('res-model');
        var active_id = $(e.target).parents('a').data('active-id');
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: res_model,
            res_id: active_id,
            views: [[false, 'form']],
            target: 'current'
        });
    },
})


core.action_registry.add("mrp_bom_hierarchy", mrp_bom_hierarchy);
return mrp_bom_hierarchy;
});