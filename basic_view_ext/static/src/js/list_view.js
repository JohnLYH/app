odoo.define('basic_view_ext.ListView', function (require) {
    'use strict';
    var ListRenderer = require('web.ListRenderer');
    ListRenderer.include({
        // init: function (parent, state, params) {
        //     this._super.apply(this, arguments);
        //     var o2m_tree_selectable = this.state.getContext().selectable;
        //     var tree_selectable = this.arch.attrs.selectable;
        //     // this.hasSelectors = o2m_tree_selectable || tree_selectable;
        //     if (o2m_tree_selectable || tree_selectable) {
        //         this.hasSelectors = true;
        //     }
        // },
        _onRowClicked: function (event) {
            var self = this;
            var o2m_field_disable = self.state.getContext().disable_open;
            var tree_disable = self.arch.attrs.disable_open;
            // 有一个为真，则禁止点击
            if(!(tree_disable || o2m_field_disable)){
                self._super.apply(self, arguments);
            }
        }
    });
});