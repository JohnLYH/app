odoo.define('zz.PreviewDialog', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var framework = require('web.framework');

var Widget = require('web.Widget');

var PreviewHandler = require('zz.PreviewHandler');
var PreviewGenerator = require('zz.PreviewGenerator');

var QWeb = core.qweb;
var _t = core._t;

var PreviewDialog = Widget.extend({
	cssLibs: [
    ],
    jsLibs: [
        '/zz/static/lib/printThis/printThis.js',
    ],
	init: function(parent, generator, url, mimetype, extension, title) {
		this._super(parent);
        this._opened = $.Deferred();
        this.title = title || _t('Preview');
        this.url = url;
        this.mimetype = mimetype;
        this.extension = extension;
		this.generator = generator;
		this.generator.widget = this;
	},
	 willStart: function() {
		var self = this; 
		return $.when(ajax.loadLibs(this), this._super()).then(function() {
    		self.$modal = $(QWeb.render('PreviewDialog', {title: self.title, url: self.url}));
		});
    },
    start: function() {
    	var self = this;
        return this._super().then(function() {
        	self.$modal.on('hidden.bs.modal', _.bind(self.destroy, self));
        	self.$modal.find('.preview-maximize').on('click', _.bind(self.maximize, self));
        	self.$modal.find('.preview-minimize').on('click', _.bind(self.minimize, self));
        	self.$modal.find('.preview-print').on('click', _.bind(self.print, self));
        });
    },
    renderElement: function() {
        this._super();
        var self = this;
        this.generator.createPreview(this.url, this.mimetype,
        		this.extension, this.title).then(function($content) {
        	self.$el.replaceWith($content);        	
        	self.setElement($content);
        	self.$modal.find('.preview-print').toggle($content.hasClass('printable'));
        });
	},
    open: function() {
        var self = this;
        $('.tooltip').remove();
        this.appendTo($('<div/>')).then(function() {
        	self.$modal.find(".modal-body").append(self.$el);
            self.$modal.modal('show');
            self._opened.resolve();
        });
        return self;
    },
    maximize: function(e) {
    	this.$modal.find('.preview-maximize').toggle();
    	this.$modal.find('.preview-minimize').toggle();
    	this.$modal.addClass("modal-fullscreen");
    	
    },
    minimize: function(e) {
    	this.$modal.find('.preview-maximize').toggle();
    	this.$modal.find('.preview-minimize').toggle();
    	this.$modal.removeClass("modal-fullscreen");
    },
    print: function(e) {
    	var $printable = this.$modal.find('.printable');
    	framework.blockUI();
    	setTimeout(function() {
    		framework.unblockUI();
    	}, ($printable.data('print-delay') || 333) * 0.95);
    	if(this.$modal.find('.print-content').length) {
    		this.$modal.find('.print-content').printThis({
    			importCSS: true,
    			importStyle: true,
    			printDelay: $printable.data('print-delay') || 333,
    			loadCSS: $printable.data('print-css') || "",
    		});
    	} else {
    		this.$modal.find('.printable').printThis({
    			importCSS: true,
    			importStyle: true,
    			printDelay: $printable.data('print-delay') || 333,
    			loadCSS: $printable.data('print-css') || "",
    		});
    	}
    },
    opened: function (handler) {
        return (handler)? this._opened.then(handler) : this._opened;
    },
    close: function() {
    	this.destroy();
    },
    destroy: function (reason) {
        if (!this.__closed) {
            this.__closed = true;
            this.trigger("closed", reason);
        }
        if (this.isDestroyed()) {
            return;
        }
        this._super();

        $('.tooltip').remove();
        if (this.$modal) {
            this.$modal.modal('hide');
            this.$modal.remove();
        }
        var modals = $('body > .modal').filter(':visible');
        if (modals.length) {
            modals.last().focus();
            $('body').addClass('modal-open');
        }
    }
});

PreviewDialog.createPreviewDialog = function (parent, url, mimetype, extension, title) {
    return new PreviewDialog(parent, new PreviewGenerator(parent, {}), url, mimetype, extension, title).open();
};

return PreviewDialog;

});