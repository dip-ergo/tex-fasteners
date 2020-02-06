odoo.define('mto_chain.mto_chain_action', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var session = require('web.session');
    var ReportWidget = require('stock.ReportWidget');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');

    var QWeb = core.qweb;

    var mto_chain_action = AbstractAction.extend(ControlPanelMixin, {
        // Stores all the parameters of the action.
        events: {
            'click .button_plan': 'planMtoManufactures',
        },
        init: function (parent, action) {
            this.actionManager = parent;
            this.given_context = session.user_context;
            if (action.context.context) {
                this.given_context = action.context.context;
            }
            this.given_context.active_id = action.context.active_id || action.params.active_id;
            this.given_context.model = action.context.active_model || false;
            this.given_context.ttype = action.context.ttype || false;
            return this._super.apply(this, arguments);
        },
        willStart: function () {
            return this.get_html();
        },
        set_html: function () {
            var self = this;
            var def = $.when();
            if (!this.report_widget) {
                this.report_widget = new ReportWidget(this, this.given_context);
                def = this.report_widget.appendTo(this.$el);
            }
            return def.then(function () {
                self.report_widget.$el.html(self.html);
                // self.report_widget.$el.find('.o_report_heading').html('<h1>MTO Chain</h1>');
                var mto_tree = $('#mto_tree', self.report_widget.$el)
                mto_tree.jstree({
                    "core": {
                        "themes": {
                            "stripes": false,
                            "variant": "large",
                            "icons": false
                        }
                    },
                    "plugins": []
                });
                mto_tree.on('ready.jstree', function() {
                    mto_tree.jstree("open_all");          
                });
                mto_tree.on("select_node.jstree", function (node, selected, event) {
                    var node_attr = selected.node.li_attr;
                    return self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: node_attr['res-model'],
                        res_id: parseInt(node_attr['res-id']),
                        views: [
                            [false, 'form']
                        ],
                        target: 'current'
                    });
                });
            });
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.set_html();
                self.update_control_panel();
            });
        },
        get_html: function () {
            var self = this;
            var defs = [];
            return this._rpc({
                    model: 'mto.chain',
                    method: 'get_html',
                    args: [self.given_context],
                })
                .then(function (result) {
                    self.html = result.html;
                    return $.when.apply($, defs);
                });
        },
        planMtoManufactures: function (e) {
            e.preventDefault();
            this.given_context.default_function = $(e.target).data('function') || '';
            let self = this
            this._rpc({
                route: '/web/action/load',
                params: {
                    action_id: 'mto_chain.plan_unplan_wizard_ation',
                },
            })
            .then(function(r) {
                r.context = self.given_context
                return self.do_action(r);
            });
        },
        do_show: function() {
            this._super();
            this.update_control_panel();
        },
    });

    core.action_registry.add("mto_chain_action", mto_chain_action);
    return mto_chain_action;
});