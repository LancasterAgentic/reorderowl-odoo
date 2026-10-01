# Run inside `odoo shell`: opens the readiness screen and every button as the demo user, a Purchase user
# without admin rights. Catches a missing access rule or a broken button, which an install alone does not.
buyer = env.ref("base.user_demo")
assert buyer.has_group("purchase.group_purchase_user") and not buyer.has_group("base.group_system")
screen = env["reorderowl.readiness"].with_user(buyer).action_open_readiness()
record = env["reorderowl.readiness"].with_user(buyer).browse(screen["res_id"])
counts = record.read(["unusable_code_count", "no_vendor_count", "zero_lead_time_count", "reorderowl_po_count"])[0]
for method in ("action_open_unusable_codes", "action_open_no_vendor", "action_open_zero_lead_time",
               "action_open_reorderowl_pos", "action_open_profile"):
    action = getattr(record, method)()
    env[action["res_model"]].with_user(buyer).search(action.get("domain") or [])
print("SCREEN_OK", counts)
