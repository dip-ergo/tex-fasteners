odoo.define('dragonfly.quality', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var core = require('web.core');

var QWeb = core.qweb;


var WorkorderIframeUrl = AbstractField.extend({
    supportedFieldTypes: ['char'],

    isSet: function() {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;
        if (!this.value) {
            this.$el.html('');
            return;
        }
        this.$el.html(QWeb.render('WorkorderIframeUrl', {
            url: self.value,
        }));
    },
});

field_registry.add('WorkorderIframeUrl', WorkorderIframeUrl);

return {
    WorkorderIframeUrl: WorkorderIframeUrl
}
    
});
