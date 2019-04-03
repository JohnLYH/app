odoo.define('mrp_bom_hierarchy.BomHierarchyWidget', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');

var QWeb = core.qweb;

var _t = core._t;

var BomHierarchyWidget = Widget.extend({
    init: function(parent) {
        this._super.apply(this, arguments);
    },
    start: function() {
        QWeb.add_template("/stock/static/src/xml/stock_traceability_report_line.xml");
        return this._super.apply(this, arguments);
    },
});

return BomHierarchyWidget;

});
