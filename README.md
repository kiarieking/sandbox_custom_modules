
## Quatrix ERP

The codebase contains all modules that have either been built or customized to achieve the purpose of the project.


## Tech Stack

**Client:** XML, HTML, Javascript, CSS

**Reporting:** QWeb Templating Engine

**Server:** Odoo Framework, Python 3, PostgreSQL


## Features

- Standard & PO - Driven Dispatch Management
- Fuel Management
- Billing Management
- Sale Management
- Purchase Management
- Fleet Management
- Invoicing & Other Accounting Processes
- API Integrations


## User Documentation

Kindly refer to our [Quatrix Wiki](https://wiki.quatrixglobal.com) to view the user documentation.

## 
## Installation

Install Odoo 13 CE using aptitude on debian 10/11


### Install Dependencies


```bash
sudo apt update

sudo apt -y upgrade

sudo apt install postgresql postgresql-contrib

wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb

sudo apt install ./wkhtmltox_0.12.6-1.buster_amd64.deb

sudo apt update

sudo apt install gnupg2

sudo pip3 install cloudinary

sudo pip3 install python-dotenv

sudo pip3 install phonenumbers

sudo pip3 install Werkzeug==0.11.15 (Odoo comes with Werkzeug==1.0.1 or higher, which does not have the Werkzeug.Contrib module)

```


### Install Odoo 13 CE
```bash
wget https://nightly.odoo.com/odoo.key

cat odoo.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/odoo.gpg  >/dev/null

echo "deb http://nightly.odoo.com/13.0/nightly/deb/ ./" | sudo tee /etc/apt/sources.list.d/odoo.list

sudo apt update

sudo apt install odoo

sudo systemctl enable --now odoo

```

Access server through http://[ServerIP_Hostname]:8069

### Odoo Configuration and Nginx setup

Kindly refer to [quatrix-erp-config-files](quatrix-erp-config-files)


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file


`cloudinary_api_key`

`cloudinary_api_secret`

`cloudinary_name`


## Modules Deployment

See [docs/deployment.md](docs/deployment.md) for ways to get started.

Please adhere to this project's [code of conduct](docs/code-of-conduct.md).

## Configurations (Before addition of any data)

### Install The Following Modules

- `Sales`
- `Purchase`
- `Fleet`
- `Accounting (Community Edition by  Odoo Mates)`
- `Inventory`
- `Expenses`
- `Audit Log`
- `Dispatch Management`
- `Partner Statement`
- `Account Partner Ledger Filter`
- `MUK Backend Theme`
- `Window Title`
- `Carrier Orders`
- `Quatrix Auth`
- `Quatrix Billing`
- `Fuel Management`
- `Quatrix Modifications`

If one encounters an issue with the installation of any of the modules, Kindly retry or reach out to [Phyllis](mailto:phyllis.mbugua@quatrixglobal.com) for assistance.


### Kindly do the following before adding any data to the system

- `Settings --> Activate Debug Mode`
- `Settings --> General Settings --> Companies --> Update Company Info`
- `Settings --> General Settings --> Business Documents --> Configure Business Documents`
- `Settings --> General Settings --> Window--> Add Window Title in the title field`
- `Settings --> General Settings --> Backend Theme --> Theme colors (Setup theme colors; Brand(#000000), Primary(#000000), Required remains the same)`
- `Settings --> General Settings --> Backend Theme --> Favicon --> Add quatrix favicon`
- `Settings --> General Settings --> Backend Theme --> Background Image --> Add quatrix branded background image`
- `Settings --> General Settings --> Discuss --> External Email Servers --> Enable and setup outgoing email servers`
- `Settings --> General Settings --> Users --> Customer Account --> On Invitation!`
- `Settings --> Accounting Settings  --> Taxes --> Configure taxes`
- `Settings --> Accounting Settings  --> Currencies --> Update Default Currency to KES`
- `Settings --> Accounting Settings  --> Currencies --> Enable Multi Currencies`
- `Settings --> Accounting Settings  --> Enable OCA Outstanding Statements`
- `Settings --> Accounting Settings  --> Enable OCA Activity Statements`
- `Settings --> Accounting Settings  --> Enable OCA Activity Statements --> Show Aging Brackets` 
- `Settings --> Sales Settings  --> Quotations and orders --> Enable Proforma Invoices`
- `Settings --> Sales Settings  --> Pricing --> Enable Multiple Pricelists (Click on pricelists and ensure the default pricelist is KES, it sometimes defaults to USD)`
- `Settings --> Purchase Settings  --> Invoicing --> Bill Control --> Enable Ordered Quantities`


## API Reference


See  [docs/api-docs.md](docs/api-docs.md) for ways to get started.

Please adhere to this project's  [code of conduct](docs/code-of-conduct.md).


## Optimizations

See [docs/optimizations.md](docs/optimizations.md)



## Demo And Testing

Please use the following environments for all testing and demonstrations.

- [Development Environment](https://dev.erp.quatrixglobal.com)

- [Testing Environment](https://test.erp.quatrixglobal.com)

- [Staging Environment](https://stage.erp.quatrixglobal.com)


## Existing Bugs

- Duplicates of fuel orders on deduction lines on vendor bill creation. (Reported on 2 vendor bills only.)


## Roadmap

- Upgrade from odoo community version to odoo enterprise /Add Cashflow report

- Add HR modules

- Add more Integrations

- Existing bugs resolution


## Contributing

Contributions are always welcome!

See [docs/contributing.md](docs/contributing.md) for ways to get started.

Please adhere to this project's [code of conduct](docs/code-of-conduct.md)


## Acknowledgements

 - [Odoo Mates](https://apps.odoo.com/apps/modules/13.0/om_account_accountant/)
 - [OCA](https://github.com/OCA/account-financial-reporting/tree/13.0/partner_statement)


## Authors

- [@murungakibaara](https://www.gitlab.com/murungakibaara)
- [@wilsonndirnagu](https://github.com/wilgrim-dev)
- [@kelvinkiarie](https://github.com/kiarieking)

