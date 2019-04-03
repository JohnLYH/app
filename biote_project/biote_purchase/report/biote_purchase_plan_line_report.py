from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.biote_purchase.report_purchaseplanline'

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['biote.purchase.plan.line'].browse(docids)
        res = sum([i.budget_amount for i in docs])
        return {'docs': docs, 'res': res}
