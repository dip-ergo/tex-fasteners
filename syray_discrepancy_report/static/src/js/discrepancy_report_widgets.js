odoo.define('syray_discrepancy_report.ReportWidget', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');

var QWeb = core.qweb;

var _t = core._t;

var ReportWidget = Widget.extend({
    events: {
        // 'click span.o_discrepancy_report_foldable': 'fold',
        // 'click span.o_discrepancy_report_unfoldable': 'unfold',
        'click .o_discrepancy_reports_web_action': 'boundLink',
    },
    init: function(parent) {
        this._super.apply(this, arguments);
    },
    start: function() {
        QWeb.add_template("/syray_discrepancy_report/static/src/xml/discrepancy_report_line.xml");
        return this._super.apply(this, arguments);
    },
    boundLink: function(e) {
        e.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(e.target).data('res-model'),
            res_id: $(e.target).data('active-id'),
            views: [[false, 'form']],
            target: 'new'
        });
    },
    // actionOpenLot: function(e) {
    //     e.preventDefault();
    //     var $el = $(e.target).parents('tr');
    //     this.do_action({
    //         type: 'ir.actions.client',
    //         tag: 'discrepancy_report_generic',
    //         name: $el.data('lot_name') !== undefined && $el.data('lot_name').toString(),
    //         context: {
    //             active_id : $el.data('lot_id'),
    //             active_model : 'stock.production.lot',
    //             url: '/stock/output_format/stock/active_id'
    //         },
    //     });
    // },
    // updownStream: function(e) {
    //     var $el = $(e.target).parents('tr');
    //     this.do_action({
    //         type: "ir.actions.client",
    //         tag: 'discrepancy_report_generic',
    //         name: _t("Traceability Report"),
    //         context: {
    //             active_id : $el.data('model_id'),
    //             active_model : $el.data('model'),
    //             auto_unfold: true,
    //             lot_name: $el.data('lot_name') !== undefined && $el.data('lot_name').toString(),
    //             url: '/stock/output_format/stock/active_id'
    //         },
    //     });
    // },
    // removeLine: function(element) {
    //     var self = this;
    //     var el, $el;
    //     var rec_id = element.data('id');
    //     var $stockEl = element.nextAll('tr[data-parent_id=' + rec_id + ']')
    //     for (el in $stockEl) {
    //         $el = $($stockEl[el]).find(".o_discrepancy_report_domain_line_0, .o_discrepancy_report_domain_line_1");
    //         if ($el.length === 0) {
    //             break;
    //         }
    //         else {
    //             var $nextEls = $($el[0]).parents("tr");
    //             self.removeLine($nextEls);
    //             $nextEls.remove();
    //         }
    //         $el.remove();
    //     }
    //     return true;
    // },
    // fold: function(e) {
    //     this.removeLine($(e.target).parents('tr'));
    //     var active_id = $(e.target).parents('tr').find('td.o_discrepancy_report_foldable').data('id');
    //     $(e.target).parents('tr').find('td.o_discrepancy_report_foldable').attr('class', 'o_discrepancy_report_unfoldable ' + active_id); // Change the class, rendering, and remove line from model
    //     $(e.target).parents('tr').find('span.o_discrepancy_report_foldable').replaceWith(QWeb.render("unfoldable", {lineId: active_id}));
    //     $(e.target).parents('tr').toggleClass('o_discrepancy_report_unfolded');
    // },
    autounfold: function(target, source_doc_name) {
        var self = this;
        var $CurretElement;
        $CurretElement = $(target).parents('tr').find('td.o_discrepancy_report_unfoldable');
        var active_id = $CurretElement.data('id');
        var active_model_name = $CurretElement.data('model');
        var active_model_id = $CurretElement.data('model_id');
        var row_level = $CurretElement.data('level');
        var $cursor = $(target).parents('tr');
        this._rpc({
                model: 'mto.discrepancy.report',
                method: 'get_lines',
                args: [parseInt(active_id, 10)],
                kwargs: {
                    'model_id': active_model_id,
                    'model_name': active_model_name,
                    'level': parseInt(row_level) + 30 || 1
                },
            })
            .then(function (lines) {// After loading the line
                _.each(lines, function (line) { // Render each line
                    $cursor.after(QWeb.render("report_discrepancy_line", {l: line}));
                    $cursor = $cursor.next();
                    if ($cursor && line.unfoldable && line.source_doc_name == source_doc_name) {
                        self.autounfold($cursor.find(".fa-caret-right"), source_doc_name);
                    }
                });
            });
        $CurretElement.attr('class', 'o_discrepancy_report_foldable ' + active_id); // Change the class, and rendering of the unfolded line
        $(target).parents('tr').find('span.o_discrepancy_report_unfoldable').replaceWith(QWeb.render("foldable", {lineId: active_id}));
        $(target).parents('tr').toggleClass('o_discrepancy_report_unfolded');
    },
    // unfold: function(e) {
    //     this.autounfold($(e.target));
    // },

});

return ReportWidget;

});
