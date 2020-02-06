# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil import relativedelta
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec


class DiscrepancyModel(models.TransientModel):
    _name = 'mto.discrepancy.report'
    _description = 'Discrepancy Report'

    @api.model
    def get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        _logger.info("active_id.........................................................")
        _logger.info(active_id)
        _logger.info("active_model .......................................................")
        _logger.info(active_model)
        if active_id and active_model and active_model == "sale.order.line" :
            rcontext['so_parent_date'] = "Date Discrepancy Report " + self.get_so_information(active_id)
            rcontext['so_parent_q'] = "Quantity Discrepancy Report " + self.get_so_information(active_id)
            rcontext['lines'] = self.get_so_line_discrepancy_report("date", active_id)
            rcontext['lines'] = sorted(rcontext['lines'],
                                       key=lambda i: (i['discrepancy_start_status'], i['discrepancy_finish_status']),
                                       reverse=True)
            rcontext['qlines'] = self.get_so_line_discrepancy_report("quantity", active_id)
            rcontext['qlines'] = sorted(rcontext['qlines'], key=lambda i: i['discrepancy_status'], reverse=True)
            # _logger.info(rcontext['lines'])
            result['date_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view').render(rcontext)
            result['quantity_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_quantity').render(rcontext)
            result['html'] = result['date_html'] + result['quantity_html']
            return result
        elif active_id and active_model and active_model == "sale.order" :
            so_order_lines = self.env['sale.order.line'].search([('order_id', '=', active_id)])
            result['html'] = bytes('', 'utf-8')
            for so_line in so_order_lines:
                rcontext['so_parent_date'] = "Date Discrepancy Report " + self.get_so_information(so_line.id)
                rcontext['so_parent_q'] = "Quantity Discrepancy Report " + self.get_so_information(so_line.id)
                rcontext['lines'] = self.get_so_line_discrepancy_report("date", so_line.id)
                rcontext['lines'] = sorted(rcontext['lines'],
                                           key=lambda i: (
                                           i['discrepancy_start_status'], i['discrepancy_finish_status']),
                                           reverse=True)
                rcontext['qlines'] = self.get_so_line_discrepancy_report("quantity", so_line.id)
                rcontext['qlines'] = sorted(rcontext['qlines'], key=lambda i: i['discrepancy_status'], reverse=True)
                # _logger.info(rcontext['lines'])
                result['date_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_so').render(rcontext)
                result['quantity_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_quantity_so').render(rcontext)
                result['html'] += result['date_html'] + result['quantity_html']
            return result
        else:
            _logger.info("active_model .......................................................")
            result['html'] = bytes('', 'utf-8')
            rcontext['so_parent_date'] = "Date Discrepancy Report"
            rcontext['so_parent_q'] = "Quantity Discrepancy Report"
            rcontext['lines'] = self.get_sep_po_line_discrepancy("date")
            rcontext['lines'] = sorted(rcontext['lines'],
                                       key=lambda i: (
                                           i['discrepancy_start_status'], i['discrepancy_finish_status']),
                                       reverse=True)
            result['date_html'] = self.env.ref('syray_discrepancy_report.report_discrepancy_view_po').render(
                rcontext)
            rcontext['qlines'] = self.get_sep_po_line_discrepancy("quantity")
            rcontext['qlines'] = sorted(rcontext['qlines'], key=lambda i: i['discrepancy_status'], reverse=True)
            # _logger.info(rcontext['lines'])
            result['quantity_html'] = self.env.ref(
                'syray_discrepancy_report.report_discrepancy_view_quantity_po').render(rcontext)
            result['html'] = result['date_html'] + result['quantity_html']
            return result

    @api.model
    def get_sep_po_line_discrepancy(self, sector):
        discrepancy_list_data = []
        bom_plist = []
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")

        # all_po_records = self.env['purchase.order'].search([])
        # for po in all_po_records:
        #     if po.node_id:
        #         # context = dict(self.env.context)
        #         # active_id = context.get('active_id', False)
        #         # active_model = context.get('model', False)
        #         # po_line = self.env['purchase.order.line'].browse(id)
        #         po_node = po.node_id
        #         # _logger.info(node_id)
        #         nodes = po_node.parent_ids;
        #         for node in nodes:
        #             node_id = node.id
        #             _logger.info(node_id)
        #             res_model = node.res_model
        #             _logger.info(res_model)
        #             production_data = self.env[node.res_model].search([('id', '=', node.res_id)])
        #             bom_line_data = self.env['mrp.bom.line'].search([('bom_id', '=', production_data.bom_id.id)])
        #
        #             for bom_line in bom_line_data:
        #                 bom_plist.append(bom_line.product_id)
        #
        #             purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', po_node.res_id)])
        #             for line in purchase_order_line:
        #                 if line.product_id in bom_plist:
        #                     if sector == "date":
        #                         po_line_data = self._get_purchase_line_data(line.id, current_date_frmt, node, "sep")
        #                         if bool(po_line_data):
        #                             discrepancy_list_data.append(po_line_data)
        #                     else:
        #                         po_line_data = self._get_purchase_line_quantity_data(line.id, current_date_frmt, node,
        #                                                                              "sep")
        #                         if bool(po_line_data):
        #                             discrepancy_list_data.append(po_line_data)
        #
        #         # _logger.info(lines)

        all_po_line_records = self.env['purchase.order.line'].search([])
        for po_line in all_po_line_records:
            if po_line.node_id:
                # context = dict(self.env.context)
                # active_id = context.get('active_id', False)
                # active_model = context.get('model', False)
                # po_line = self.env['purchase.order.line'].browse(id)
                po_node = po_line.node_id
                # _logger.info(node_id)
                nodes = po_node.parent_ids;
                for node in nodes:
                    node_id = node.id
                    _logger.info(node_id)
                    res_model = node.res_model
                    _logger.info(res_model)
                    if sector == "date":
                        po_line_data = self._get_purchase_line_data(po_node.res_id, current_date_frmt, node, "sep")
                        if bool(po_line_data):
                            discrepancy_list_data.append(po_line_data)
                    else:
                        po_line_data = self._get_purchase_line_quantity_data(po_node.res_id, current_date_frmt, node, "sep")
                        if bool(po_line_data):
                            discrepancy_list_data.append(po_line_data)
                # _logger.info(lines)
        if sector == "date":
            lines = self._list_to_date_lines(discrepancy_list_data)
        else:
            lines = self._list_to_quantity_lines(discrepancy_list_data)
        return lines

    @api.model
    def get_so_information(self,id):
        discrepancy_list_data = []
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        so_data = self.env[active_model].browse(active_id)
        # _logger.info(so_data)
        name = so_data.name
        if active_model == "sale.order.line":
            name = "(" + so_data.order_id.name + ") - " + name
        elif active_model == "sale.order":
            so_line_data = self.env['sale.order.line'].browse(id)
            name = "(" + so_data.name + ") - " + so_line_data.name
        return name

    @api.model
    def get_so_line_discrepancy_report(self, sector, id):
        discrepancy_list_data = []
        production_list_data = []
        po_line_data = {}
        # context = dict(self.env.context)
        # active_id = context.get('active_id', False)
        # active_model = context.get('model', False)
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
        node_id = self.env['sale.order.line'].browse(id).node_id
        _logger.info("id.......................................................................")
        _logger.info(id)
        nodes = node_id.child_ids;
        for node in nodes:
            node_id = node.id
            # _logger.info(node_id)
            res_model = node.res_model
            # _logger.info(res_model)
            if res_model == "mrp.production" and sector == "date":
                discrepancy_list_data = self._recursive_node(node, discrepancy_list_data, id)
                #discrepancy_list_data.extend(production_list_data)
            elif res_model == "mrp.production" and sector == "quantity":
                discrepancy_list_data = self._quantity_recursive_node(node, discrepancy_list_data, id)
                #discrepancy_list_data.extend(production_list_data)
            elif res_model == "purchase.order.line" and sector == "date":
                po_line_data = self._get_purchase_line_data_so(node.res_id, current_date_frmt, id)
                if bool(po_line_data):
                    discrepancy_list_data.append(po_line_data)
            elif res_model == "purchase.order.line" and sector == "quantity":
                po_line_data = self._get_purchase_line_quantity_data_so(node.res_id, current_date_frmt, id)
                if bool(po_line_data):
                    discrepancy_list_data.append(po_line_data)
        # _logger.info(discrepancy_list_data)
        if sector == "date":
            lines = self._list_to_date_lines(discrepancy_list_data)
        else:
            lines = self._list_to_quantity_lines(discrepancy_list_data)
            # _logger.info(lines)
        return lines

    @api.model
    def _list_to_date_lines(self, discrepancy_list_data):
        lines = []
        # _logger.info("in _list_to_lines")
        for data in discrepancy_list_data:
            lines.append({
                'id': autoIncrement(),
                'model': data['res_model'],
                'model_id': data['res_id'],
                'source_doc_name': data['source_doc_name'],
                'work_center': data.get('work_center', False),
                'is_used': True,
                'discrepancy_message_start': data.get('discrepancy_message_start', False),
                'discrepancy_message_end': data.get('discrepancy_message_end', False),
                'discrepancy_start_status': data.get('discrepancy_start_status', False),
                'discrepancy_finish_status': data.get('discrepancy_finish_status', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            # data.get('source_doc_name', False),
                            data.get('work_center', False),
                            data.get('discrepancy_message_start', False),
                            data.get('discrepancy_message_end', False)],
                'level': 1,
                'unfoldable': True
            })

        # _logger.info("return _list_to_lines")
        return lines

    @api.model
    def _list_to_quantity_lines(self, discrepancy_list_data):
        lines = []
        # _logger.info("in _list_to_lines")
        for data in discrepancy_list_data:
            lines.append({
                'id': autoIncrement(),
                'model': data['res_model'],
                'model_id': data['res_id'],
                'source_doc_name': data['source_doc_name'],
                'work_center': data.get('work_center', False),
                'product_name': data.get('product_name', False),
                'is_used': True,
                'discrepancy_message': data.get('discrepancy_message', False),
                'discrepancy_status': data.get('discrepancy_status', False),
                'reference': data.get('reference_id', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            # data.get('source_doc_name', False),
                            data.get('work_center', False),
                            data.get('product_name', False),
                            data.get('discrepancy_message', False)],
                'level': 1,
                'unfoldable': True
            })

        # _logger.info("return _list_to_lines")
        return lines

    @api.model
    def _recursive_node(self, parent_node, discrepancy_list_data, so_line_id):
        # _logger.info("into recursive node")
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
        # _logger.info(current_date_frmt)
        mo_line = self._get_production_data(parent_node, current_date_frmt, so_line_id)
        if bool(mo_line):
            discrepancy_list_data.append(mo_line)
        res_id = parent_node.res_id
        # _logger.info(res_id)
        work_order_data = self.env['mrp.workorder'].search([('production_id', '=', res_id)])
        # _logger.info("work_order_data")
        # _logger.info(work_order_data)
        if work_order_data:
            for work_order in work_order_data:
                wo_line = self._get_wo_data(parent_node, work_order, current_date_frmt, so_line_id)
                if bool(wo_line):
                    discrepancy_list_data.append(wo_line)
        nodes = parent_node.child_ids;
        # _logger.info("check second node")
        # _logger.info(nodes)
        if nodes:
            for node in nodes:
                node_id = node.id
                # _logger.info(node_id)
                res_model = node.res_model
                if res_model == "mrp.production":
                    discrepancy_list_data = self._recursive_node(node, discrepancy_list_data, so_line_id)
                if res_model == "purchase.order":
                    po_line = self._get_purchase_data(node, current_date_frmt, parent_node, so_line_id)
                    discrepancy_list_data.extend(po_line)
                if res_model == "purchase.order.line":
                    po_line = self._get_purchase_line_data(node.res_id, current_date_frmt, parent_node, so_line_id)
                    if bool(po_line):
                        discrepancy_list_data.append(po_line)
        return discrepancy_list_data

    @api.model
    def _get_production_data(self, node, current_date_frmt, so_line_id):
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        sale_order_line_qty = self.env['sale.order.line'].browse(so_line_id).product_uom_qty
        list_data = {}
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        _logger.info("production_id")
        _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        if production_data.state == "confirmed":
            if current_date_frmt >= production_data.date_planned_start:
                discrepancy_message_start = production_data.name + " Missed scheduled start time of " + str(
                    production_data.date_planned_start.date()) + " date"
                discrepancy_start_status = True
            if current_date_frmt >= production_data.date_planned_finished:
                discrepancy_message_end = production_data.name + " Missed scheduled finish time of " + str(
                    production_data.date_planned_finished.date()) + " date"
                discrepancy_finish_status = True
        elif production_data.state == "planned":
            if production_data.date_planned_start_wo and production_data.date_planned_start.date() < production_data.date_planned_start_wo.date():
                discrepancy_message_start = production_data.name + " will fail to start work-order in time due to Work Center unavailability"
                discrepancy_start_status = True
            elif production_data.date_planned_start_wo and current_date_frmt >= production_data.date_planned_start_wo:
                discrepancy_message_start = production_data.name + " Missed work-order's scheduled start time of " + str(
                    production_data.date_planned_start_wo.date()) + " date"
                discrepancy_start_status = True
            if production_data.date_planned_finished_wo and production_data.date_planned_finished.date() < production_data.date_planned_finished_wo.date():
                discrepancy_message_end = production_data.name + " will fail to finish work-order in time due to Work Center unavailability"
                discrepancy_finish_status = True
            elif production_data.date_planned_finished_wo and current_date_frmt >= production_data.date_planned_finished_wo:
                discrepancy_message_end = production_data.name + " Missed work-order's scheduled finish time of " + str(
                    production_data.date_planned_finished_wo.date()) + " date"
                discrepancy_finish_status = True
        if production_data.state == "progress":
            if production_data.date_planned_start_wo and current_date_frmt >= production_data.date_planned_start_wo:
                discrepancy_message_start = production_data.name + " production started at " + str(
                    production_data.date_start.date()) + " date"
            if production_data.date_planned_finished_wo and current_date_frmt >= production_data.date_planned_finished_wo:
                discrepancy_message_end = production_data.name + " Missed work-order's scheduled finish time of " + str(
                    production_data.date_planned_finished.date()) + " date"
                discrepancy_finish_status = True
            elif not production_data.date_planned_finished_wo and current_date_frmt >= production_data.date_planned_finished:
                discrepancy_message_end = production_data.name + " Missed scheduled finish time of " + str(
                    production_data.date_planned_finished.date()) + " date"
                discrepancy_finish_status = True
        # if current_date_frmt >= production_data.date_planned_start and ((production_data.state == "planned" or production_data.state == "confirmed") and production_data.state != "cancel"):
        #     discrepancy_message_start = production_data.name + " Missed scheduled start time of " + str(
        #         production_data.date_planned_start) + " date"
        #     discrepancy_start_status = True
        # elif current_date_frmt >= production_data.date_planned_start and production_data.state == "progress":
        #     discrepancy_message_start = production_data.name + " production started at " + str(
        #         production_data.date_start) + " date"
        # if current_date_frmt >= production_data.date_planned_finished and (
        #         production_data.state != "done" and production_data.state != "cancel"):
        #     discrepancy_message_end = production_data.name + " Missed scheduled finish time of " + str(
        #         production_data.date_planned_finished) + " date"
        #     discrepancy_finish_status = True
        if production_data.state == "cancel":
            discrepancy_message_start = "Canceled"
            discrepancy_message_end = ""
        if production_data.state == "done":
            discrepancy_message_start = "Done"
            discrepancy_message_end = ""
            if sale_order_line_qty == 0:
                discrepancy_start_status = True


        name = production_data.name
        ref = self._get_reference(res_model, res_id, name)
        list_data = {
            "res_model": res_model,
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        _logger.info(list_data)
        if discrepancy_start_status or discrepancy_finish_status:
            return list_data
        else:
            return {}

    @api.model
    def _get_purchase_data(self, node, current_date_frmt, parent_node,so_line_id):
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        # _logger.info(res_id)
        bom_plist = []
        pq_list = []
        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])

        bom_line_data = self.env['mrp.bom.line'].search([('bom_id', '=', production_data.bom_id.id)])
        for bom_line in bom_line_data:
            bom_plist.append(bom_line.product_id)

        purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', res_id)])
        for line in purchase_order_line:
            if line.product_id in bom_plist:
                po_line_data = self._get_purchase_line_data(line.id, current_date_frmt, parent_node, "")
                if bool(po_line_data):
                    pq_list.append(po_line_data)

        return pq_list

    @api.model
    def _get_purchase_line_data_so(self, res_id, current_date_frmt, so_line_id):
        _logger.info(so_line_id)
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        purchase_data = self.env['purchase.order.line'].search([('id', '=', res_id)])

        sales_line = self.env['sale.order.line'].browse(so_line_id)
        name = sales_line.order_id.name + " - " + purchase_data.order_id.name + " - " + purchase_data.product_id.name
        ref = self._get_reference('purchase.order.line', res_id, name)

        # current_date_frmt = current_date_frmt.date()
        if sales_line.date_expected:
            if current_date_frmt <= sales_line.date_expected and purchase_data.date_planned > sales_line.date_expected:
                discrepancy_message_start = "Purchase order will miss parent SO's scheduled delivery date"
                discrepancy_message_end = ""
                discrepancy_start_status = True
                discrepancy_finish_status = True

            elif current_date_frmt > sales_line.date_expected and purchase_data.product_qty > purchase_data.qty_received:
                discrepancy_message_start = "Purchase order missed parent SO's scheduled delivery date"
                discrepancy_message_end = ""
                discrepancy_start_status = True
                discrepancy_finish_status = True

            else:
                discrepancy_message_start = "No Discrepancy"
                discrepancy_message_end = ""

        # _logger.info(ref)
        list_data = {
            "res_model": 'purchase.order.line',
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        if so_line_id != "sep":
            if discrepancy_start_status or discrepancy_finish_status:
                return list_data
            else:
                return {}
        else:
            return list_data
        # return list_data

    @api.model
    def _get_purchase_line_data(self, res_id, current_date_frmt, parent_node,so_line_id):
        # _logger.info(res_id)
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        purchase_data = self.env['purchase.order.line'].search([('id', '=', res_id)])

        if parent_node.res_model == "sale.order.line":
            sales_line = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
            name = sales_line.order_id.name + " - " + purchase_data.order_id.name + " - " + purchase_data.product_id.name
            ref = self._get_reference('purchase.order.line', res_id, name)
            # current_date_frmt = current_date_frmt.date()
            if sales_line.date_expected:
                if current_date_frmt <= sales_line.date_expected and purchase_data.date_planned > sales_line.date_expected:
                    discrepancy_message_start = "Purchase order will miss parent SO's scheduled delivery date"
                    discrepancy_message_end = ""
                    discrepancy_start_status = True
                    discrepancy_finish_status = True
                elif current_date_frmt > sales_line.date_expected and purchase_data.product_qty > purchase_data.qty_received:
                    discrepancy_message_start = "Purchase order missed parent SO's scheduled delivery date"
                    discrepancy_message_end = ""
                    discrepancy_start_status = True
                    discrepancy_finish_status = True
                else:
                    discrepancy_message_start = "No Discrepancy"
                    discrepancy_message_end = ""
        else:
            production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
            name = production_data.name + " - " + purchase_data.order_id.name + " - " + purchase_data.product_id.name
            ref = self._get_reference('purchase.order.line', res_id, name)

            # current_date_frmt = current_date_frmt.date()
            if current_date_frmt <= production_data.date_planned_start and purchase_data.date_planned > production_data.date_planned_start:
                discrepancy_message_start = "Purchase order will miss parent MO's scheduled start date"
                discrepancy_message_end = ""
                discrepancy_start_status = True
                discrepancy_finish_status = True
            elif current_date_frmt > production_data.date_planned_start and purchase_data.product_qty > purchase_data.qty_received:
                discrepancy_message_start = "Purchase order missed parent MO's scheduled start date"
                discrepancy_message_end = ""
                discrepancy_start_status = True
                discrepancy_finish_status = True
            else:
                discrepancy_message_start = "No Discrepancy"
                discrepancy_message_end = ""
        # _logger.info(ref)
        list_data = {
            "res_model": 'purchase.order.line',
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        if so_line_id != "sep":
            if discrepancy_start_status or discrepancy_finish_status:
                return list_data
            else:
                return {}
        else:
            return list_data
        # return list_data

    @api.model
    def _get_wo_data(self, node, work_order, current_date_frmt,so_line_id):
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        sale_order_line_qty = self.env['sale.order.line'].browse(so_line_id).product_uom_qty
        list_data = {}
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        # _logger.info("sale_order_line_qty")
        # _logger.info(sale_order_line_qty)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message_start = "Scheduled start time not reached"
        discrepancy_message_end = "Scheduled finish time not reached"
        discrepancy_start_status = False
        discrepancy_finish_status = False
        if work_order.date_planned_start and current_date_frmt >= work_order.date_planned_start and (
                (work_order.state == "ready" or work_order.state == "pending") and work_order.state != "cancel"):
            discrepancy_message_start = work_order.name + " Missed scheduled start time of " + str(
                work_order.date_planned_start) + " date"
            discrepancy_start_status = True
        # elif work_order.date_planned_start > production_data.date_planned_start and (
        #         (work_order.state == "ready" or work_order.state == "pending") and work_order.state != "cancel"):
        #     discrepancy_message_start = work_order.name + " will not start on time due to Work Center unavailability."
        #     discrepancy_start_status = True
        if work_order.date_planned_finished and current_date_frmt >= work_order.date_planned_finished and (
                work_order.state != "done" and work_order.state != "cancel"):
            discrepancy_message_end = work_order.name + " Missed scheduled finish time of " + str(
                work_order.date_planned_finished.date()) + " date"
            discrepancy_finish_status = True
        elif work_order.date_planned_finished and work_order.date_planned_finished > production_data.date_planned_finished and (
                work_order.state != "done" and work_order.state != "cancel"):
            discrepancy_message_end = work_order.name + " will not finish on time due to Work Center unavailability."
            discrepancy_finish_status = True
        if work_order.state == "cancel":
            discrepancy_message_start = "Canceled"
            discrepancy_message_end = ""
        if work_order.state == "done":
            discrepancy_message_start = "Done"
            discrepancy_message_end = ""
            if sale_order_line_qty == 0:
                discrepancy_start_status = True

        name = production_data.name + " - " + work_order.name
        ref = self._get_reference('mrp.workorder', work_order.id, name)
        list_data = {
            "res_model": 'mrp.workorder',
            "res_id": work_order.id,
            "source_doc_name": name,
            "work_center": work_order.workcenter_id.name,
            "discrepancy_message_start": discrepancy_message_start,
            "discrepancy_message_end": discrepancy_message_end,
            "discrepancy_start_status": discrepancy_start_status,
            "discrepancy_finish_status": discrepancy_finish_status,
            "reference_id": ref
        }
        if discrepancy_start_status or discrepancy_finish_status:
            return list_data
        else:
            return {}
        # return list_data

    @api.model
    def _quantity_recursive_node(self, parent_node, discrepancy_list_data, so_line_id):
        # _logger.info("into recursive node")
        current_date = datetime.now()
        current_date_str = datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S")
        current_date_frmt = datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
        # _logger.info(current_date_frmt)
        mo_line = self._get_production_quantity_data(parent_node, current_date_frmt)
        discrepancy_list_data.extend(mo_line)
        res_id = parent_node.res_id
        # _logger.info(res_id)
        work_order_data = self.env['mrp.workorder'].search([('production_id', '=', res_id)])
        # _logger.info("work_order_data")
        # _logger.info(work_order_data)
        if work_order_data:
            for work_order in work_order_data:
                wo_line = self._get_wo_quantity_data(parent_node, work_order, current_date_frmt, so_line_id)
                if bool(wo_line):
                    discrepancy_list_data.append(wo_line)
        nodes = parent_node.child_ids;
        # _logger.info("check second node")
        # _logger.info(nodes)
        if nodes:
            for node in nodes:
                node_id = node.id
                # _logger.info(node_id)
                res_model = node.res_model
                # _logger.info(res_model)
                if res_model == "mrp.production":
                    discrepancy_list_data = self._quantity_recursive_node(node, discrepancy_list_data, so_line_id)
                if res_model == "purchase.order":
                    po_line = self._get_purchase_quantity_data(node, current_date_frmt, parent_node, so_line_id)
                    discrepancy_list_data.extend(po_line)
                if res_model == "purchase.order.line":
                    po_line = self._get_purchase_line_quantity_data(node.res_id, current_date_frmt, parent_node, so_line_id)
                    if bool(po_line):
                        discrepancy_list_data.append(po_line)
        return discrepancy_list_data

    @api.model
    def _get_production_quantity_data(self, node, current_date_frmt):
        moq_list = []
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        active_model = context.get('model', False)
        list_data = {}
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        _logger.info("production_id")
        _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message = "No discrepancy"
        discrepancy_status = False
        name = production_data.name
        stock_picking = self.env["stock.picking"].search([('origin', '=', name),('location_dest_id', '=', 18)])
        if stock_picking:
            for picking in stock_picking:
                stock_picking_move_line = self.env["stock.move.line"].search([('picking_id', '=', picking.id)])
                for move_line in stock_picking_move_line:
                    if production_data.state == "confirmed":
                        if move_line.qty_done == 0.0 and move_line.product_uom_qty != 0.0:
                            discrepancy_message = production_data.name + " - " + move_line.product_id.name + " - <b> required quantity still not reserved. MO planned start date: </b>" + str(
                                production_data.date_planned_start.date())
                            discrepancy_status = True
                    if production_data.state == "planned":
                        if move_line.qty_done == 0.0 and move_line.product_uom_qty != 0.0:
                            discrepancy_message = production_data.name + " - " + move_line.product_id.name + " - <b> required quantity still not reserved. MO planned work-order start date: </b>" + str(
                                production_data.date_planned_start_wo.date())
                            discrepancy_status = True
                    ref = self._get_reference(res_model, res_id, name)
                    list_data = {
                        "res_model": res_model,
                        "res_id": res_id,
                        "source_doc_name": name,
                        "work_center": "",
                        "product_name": move_line.product_id.name,
                        "discrepancy_message": discrepancy_message,
                        "discrepancy_status": discrepancy_status,
                        "reference_id": ref
                    }
                    if discrepancy_status:
                        moq_list.append(list_data)
        return moq_list

    @api.model
    def _get_wo_quantity_data(self, node, work_order, current_date_frmt,so_line_id):
        list_data = {}
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        # _logger.info(res_id)
        production_data = self.env[res_model].search([('id', '=', res_id)])
        discrepancy_message = "No discrepancy"
        discrepancy_status = False
        product_name = work_order.product_id.name
        if work_order.date_planned_finished and current_date_frmt >= work_order.date_planned_finished and work_order.state != "cancel" and work_order.qty_produced < work_order.qty_producing:
            discrepancy_message = work_order.name + " failed to produce required quantity. Current status " + str(work_order.qty_produced) + " / " + str(work_order.qty_producing)
            discrepancy_status = True
        if work_order.date_planned_finished and current_date_frmt >= work_order.date_planned_finished and work_order.state != "cancel" and work_order.qty_produced > work_order.qty_producing:
            discrepancy_message = work_order.name + " produced extra than required quantity. Current status " + str(work_order.qty_produced) + " / " + str(work_order.qty_producing)
            discrepancy_status = True
        if work_order.state == "cancel":
            discrepancy_message = "Canceled"

        name = production_data.name + " - " + work_order.name
        ref = self._get_reference('mrp.workorder', work_order.id, name)
        list_data = {
            "res_model": 'mrp.workorder',
            "res_id": work_order.id,
            "source_doc_name": name,
            "work_center": work_order.workcenter_id.name,
            "product_name": product_name,
            "discrepancy_message": discrepancy_message,
            "discrepancy_status": discrepancy_status,
            "reference_id": ref
        }
        if discrepancy_status:
            return list_data
        else:
            return {}

    @api.model
    def _get_purchase_quantity_data(self, node, current_date_frmt, parent_node,so_line_id):
        pq_list = []
        res_model = node.res_model
        # _logger.info(res_model)
        res_id = node.res_id
        # _logger.info(res_id)
        bom_plist = []

        production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
        bom_line_data = self.env['mrp.bom.line'].search([('bom_id', '=', production_data.bom_id.id)])

        for bom_line in bom_line_data:
            bom_plist.append(bom_line.product_id)

        purchase_order_line = self.env['purchase.order.line'].search([('order_id', '=', res_id)])
        for line in purchase_order_line:
            if line.product_id in bom_plist:
                po_line_data = self._get_purchase_line_quantity_data(line.id, current_date_frmt, parent_node, "")
                if bool(po_line_data):
                    pq_list.append(po_line_data)

        return pq_list

    @api.model
    def _get_purchase_line_quantity_data(self, res_id, current_date_frmt, parent_node, so_line_id):
        # _logger.info(res_id)
        discrepancy_message = "No Discrepancy"
        discrepancy_status = False
        purchase_data = self.env['purchase.order.line'].search([('id', '=', res_id)])

        if parent_node.res_model == "sale.order.line":
            sale_line = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
            name = sale_line.order_id.name + " - " + purchase_data.order_id.name
            ref = self._get_reference('purchase.order.line', res_id, name)
            # current_date_frmt = current_date_frmt.date()
            if sale_line.date_expected:
                if current_date_frmt >= sale_line.date_expected and purchase_data.product_qty > purchase_data.qty_received:
                    discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " failed to receive required quantity. Current status " + str(
                        purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                    discrepancy_status = True
                if current_date_frmt >= sale_line.date_expected and purchase_data.product_qty < purchase_data.qty_received:
                    discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " received extra quantity. Current status " + str(
                        purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                    discrepancy_status = True
        else:
            production_data = self.env[parent_node.res_model].search([('id', '=', parent_node.res_id)])
            name = production_data.name + " - " + purchase_data.order_id.name
            ref = self._get_reference('purchase.order.line', res_id, name)

            # current_date_frmt = current_date_frmt.date()
            if current_date_frmt >= production_data.date_planned_start and purchase_data.product_qty > purchase_data.qty_received:
                discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " failed to receive required quantity. Current status " + str(
                    purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                discrepancy_status = True
            if current_date_frmt >= production_data.date_planned_start and purchase_data.product_qty < purchase_data.qty_received:
                discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " received extra quantity. Current status " + str(
                    purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                discrepancy_status = True
        # _logger.info(ref)
        list_data = {
            "res_model": 'purchase.order.line',
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "product_name": purchase_data.name,
            "discrepancy_message": discrepancy_message,
            "discrepancy_status": discrepancy_status,
            "reference_id": ref
        }

        if so_line_id != "sep":
            if discrepancy_status:
                return list_data
            else:
                return {}
        else:
            return list_data

    @api.model
    def _get_purchase_line_quantity_data_so(self, res_id, current_date_frmt, so_line_id):
        # _logger.info(res_id)
        discrepancy_message = "No Discrepancy"
        discrepancy_status = False
        purchase_data = self.env['purchase.order.line'].search([('id', '=', res_id)])

        sales_line = self.env['sale.order.line'].browse(so_line_id)
        name = sales_line.order_id.name + " - " + purchase_data.order_id.name + " - " + purchase_data.product_id.name
        ref = self._get_reference('purchase.order.line', res_id, name)

        # current_date_frmt = current_date_frmt.date()
        if sales_line.date_expected:
            if current_date_frmt >= sales_line.date_expected and purchase_data.product_qty > purchase_data.qty_received:
                discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " failed to receive required quantity. Current status " + str(
                    purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                discrepancy_status = True
            if current_date_frmt >= sales_line.date_expected and purchase_data.product_qty < purchase_data.qty_received:
                discrepancy_message = purchase_data.order_id.name + " - " + purchase_data.name + " received extra quantity. Current status " + str(
                    purchase_data.qty_received) + " / " + str(purchase_data.product_qty)
                discrepancy_status = True

        # _logger.info(ref)
        list_data = {
            "res_model": 'purchase.order.line',
            "res_id": res_id,
            "source_doc_name": name,
            "work_center": "",
            "product_name": purchase_data.name,
            "discrepancy_message": discrepancy_message,
            "discrepancy_status": discrepancy_status,
            "reference_id": ref
        }

        if so_line_id != "sep":
            if discrepancy_status:
                return list_data
            else:
                return {}
        else:
            return list_data


    @api.model
    def _get_reference(self, res_model, res_id, name):
        res_model = res_model
        res_id = res_id
        ref = name
        return ref


