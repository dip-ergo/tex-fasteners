odoo.define('smart_reordering.relational_fields', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');

relational_fields.FieldSelection.include({
    init: function (parent, name, record, options) {
        this._super.apply(this, arguments);
        this.show_all_options_readonly = this.nodeOptions.show_all_options_readonly || false;
    },
    _renderReadonly: function () {
        if (this.show_all_options_readonly) {
            this._renderEdit();
            this.$("input").prop("disabled", true);    
        }
        else {
            this._super.apply(this, arguments);
        }
    },
});

});