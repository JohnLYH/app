// odoo.define('basic_field_ext.AbstractField', function (require) {
//     'use strict';
//     var AbstractField = require('web.AbstractField');
//     AbstractField.include({
//         _render: function () {
//             if(this.recordData && this.recordData['readonly_all']) {
//                 this.mode = 'readonly';
//             }
//             return this._super.apply(this, arguments);
//         },
//     });
// });
