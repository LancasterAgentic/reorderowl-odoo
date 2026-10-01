from collections import Counter

from odoo import _, api, fields, models

# The item-code rule mirrors ReorderOwl's hosted Odoo connector (connectors/odoo.py ``_usable`` and
# ``_codes``, item width 24). Change both together. A product whose Internal Reference fails it is
# shown in ReorderOwl as ODOO-<product id>.
CODE_WIDTH = 24
PO_ORIGIN = "ReorderOwl"


def _usable(code):
    return (isinstance(code, str) and 0 < len(code) <= CODE_WIDTH and code == code.strip()
            and not code.startswith("($)"))


class ReorderowlReadiness(models.TransientModel):
    _name = "reorderowl.readiness"
    _description = "ReorderOwl Readiness"

    base_url = fields.Char("Odoo URL", compute="_compute_readiness")
    database = fields.Char("Database", compute="_compute_readiness")
    company_name = fields.Char("Company", compute="_compute_readiness")
    unusable_code_count = fields.Integer("Products without a usable Internal Reference",
                                         compute="_compute_readiness")
    no_vendor_count = fields.Integer("Products without a current vendor", compute="_compute_readiness")
    zero_lead_time_count = fields.Integer("Vendor lines with no lead time", compute="_compute_readiness")
    reorderowl_po_count = fields.Integer("Purchase orders created by ReorderOwl", compute="_compute_readiness")

    # The records ReorderOwl reads: storable products of the current company or shared, and current
    # vendor lines of active vendors for those products.
    def _products(self):
        return self.env["product.product"].search(
            [("is_storable", "=", True), ("company_id", "in", [self.env.company.id, False])])

    def _seller_domain(self, products):
        return [("product_tmpl_id", "in", products.product_tmpl_id.ids),
                ("company_id", "in", [self.env.company.id, False]),
                ("partner_id.active", "=", True),
                "|", ("date_end", "=", False), ("date_end", ">=", fields.Date.context_today(self))]

    def _unusable_code_products(self):
        products = self._products()
        seen = Counter(p.default_code for p in products if _usable(p.default_code))
        return products.filtered(lambda p: not (_usable(p.default_code) and seen[p.default_code] == 1))

    def _no_vendor_products(self):
        products = self._products()
        covered = set()
        for line in self.env["product.supplierinfo"].search(self._seller_domain(products)):
            covered.update(line.product_id.ids or line.product_tmpl_id.product_variant_ids.ids)
        return products.filtered(lambda p: p.id not in covered)

    def _zero_lead_time_lines(self):
        return self.env["product.supplierinfo"].search(self._seller_domain(self._products()) + [("delay", "=", 0)])

    def _po_domain(self):
        return [("origin", "=", PO_ORIGIN), ("company_id", "=", self.env.company.id)]

    def _compute_readiness(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        unusable = len(self._unusable_code_products())
        no_vendor = len(self._no_vendor_products())
        zero_lead = len(self._zero_lead_time_lines())
        pos = self.env["purchase.order"].search_count(self._po_domain())
        for rec in self:
            rec.base_url = base_url
            rec.database = self.env.cr.dbname
            rec.company_name = self.env.company.name
            rec.unusable_code_count = unusable
            rec.no_vendor_count = no_vendor
            rec.zero_lead_time_count = zero_lead
            rec.reorderowl_po_count = pos

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = _("ReorderOwl Readiness")

    @api.model
    def action_open_readiness(self):
        """Menu entry: open a saved record, so the counts compute when the form reads it."""
        return {"type": "ir.actions.act_window", "name": _("ReorderOwl Readiness"), "res_model": self._name,
                "res_id": self.create({}).id, "view_mode": "form", "target": "current"}

    def _open(self, name, model, domain):
        return {"type": "ir.actions.act_window", "name": name, "res_model": model,
                "view_mode": "list,form", "domain": domain, "context": {"create": False}}

    def action_open_unusable_codes(self):
        return self._open(_("Products without a usable Internal Reference"), "product.product",
                          [("id", "in", self._unusable_code_products().ids)])

    def action_open_no_vendor(self):
        return self._open(_("Products without a current vendor"), "product.product",
                          [("id", "in", self._no_vendor_products().ids)])

    def action_open_zero_lead_time(self):
        return self._open(_("Vendor lines with no lead time"), "product.supplierinfo",
                          [("id", "in", self._zero_lead_time_lines().ids)])

    def action_open_reorderowl_pos(self):
        return self._open(_("Purchase orders created by ReorderOwl"), "purchase.order", self._po_domain())

    def action_open_profile(self):
        action = self.env.user.action_get()
        action["res_id"] = self.env.user.id  # the stored action has no record; Odoo's own menu adds it the same way
        return action
