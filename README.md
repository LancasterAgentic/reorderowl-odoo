# ReorderOwl Readiness for Odoo

A free, read-only Odoo module from Lancaster Agentic. It adds **Purchase > Products > ReorderOwl Readiness**, a screen that counts the data problems that weaken reorder suggestions and opens each list so you can fix it:

- products without a usable Internal Reference (blank, longer than 24 characters, leading or trailing space, starting with "($)", or shared with another product)
- storable products without a current vendor
- vendor lines with a lead time of 0 days

It also shows the Odoo URL, database and company that [ReorderOwl](https://reorderowl.com) needs. ReorderOwl itself is a separate hosted service, set up after a booked demo, that reads Odoo through an API key you create and can revoke. This module changes none of your data and makes no outside connections.

## Versions

One branch per Odoo series. `18.0` is the only one so far, tested on Odoo 18 Community.

## Install

Copy `reorderowl_readiness` into your addons path, update the apps list and install **ReorderOwl Readiness**. It depends on `purchase_stock`. The menu is visible to Purchase users.

## Development

The Internal Reference rule mirrors ReorderOwl's hosted Odoo connector (`connectors/odoo.py`, `_usable` and `_codes`, item width 24). Change both together.

CI installs the module on a fresh Odoo 18 database. Every merge to `18.0` is picked up by the Odoo Apps store, so `18.0` takes changes only through reviewed pull requests.

License: LGPL-3.
