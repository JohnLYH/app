odoo.define('zz.PreviewHandler', function (require) {
"use strict";

var core = require('web.core');

var QWeb = core.qweb;
var _t = core._t;

var BaseHandler = core.Class.extend({
	init: function(widget) {
		this.widget = widget;
	},
	checkExtension: function(extension) {
		return false;
	},
    checkType: function(mimetype) {
		return false;
	},
    createHtml: function(url, mimetype, extension, title) {
    	return $.when();
    },
});

var PDFHandler = BaseHandler.extend({
	checkExtension: function(extension) {
		return ['.pdf', 'pdf'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/pdf'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();	
    	var viewerUrlTempalte = _.template('/zz/static/lib/PDFjs/web/viewer.html?file=<%= url %>');
		result.resolve($(QWeb.render('ViewerJSFrame', {url: viewerUrlTempalte({url})})));
		return result;
	},    
});

var OpenOfficeHandler = BaseHandler.extend({
	checkExtension: function(extension) {
		return ['.odt', '.odp', '.ods', '.fodt', '.ott', '.fodp', '.otp', '.fods', '.ots',
			'odt', 'odp', 'ods', 'fodt', 'ott', 'fodp', 'otp', 'fods', 'ots'].includes(extension);
    },
    checkType: function(mimetype) {
		return ['application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.presentation',
				'application/vnd.oasis.opendocument.spreadsheet'].includes(mimetype);
    },
    createHtml: function(url, mimetype, extension, title) {
    	var result = $.Deferred();	
    	var viewerUrlTempalte = _.template('/zz/static/lib/ViewerJS/index.html#<%= url %>');
		result.resolve($(QWeb.render('ViewerJSFrame', {url: viewerUrlTempalte({url})})));
		return result;
    },
});

return {
	BaseHandler: BaseHandler,
	PDFHandler: PDFHandler,
	OpenOfficeHandler: OpenOfficeHandler,
};

});