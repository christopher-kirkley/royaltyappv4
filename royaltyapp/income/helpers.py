import pandas as pd
import numpy as np

from royaltyapp.models import db, IncomePending, Version

from sqlalchemy import cast

class Statement:
    def __init__(self, file):
        self.file = file
        self.columns_for_db = [
            'statement',
            'distributor',
            'date',
            'order_id',
            'upc_id',
            'isrc_id',
            'version_number',
            'catalog_id',
            'album_name',
            'track_name',
            'quantity',
            'amount',
            'customer',
            'city',
            'region',
            'country',
            'type',
            'medium',
            'product',
            'description']

    def create_df(self):
        self.df = pd.read_csv(self.file, encoding=self.encoding, dtype=self.dtype)

    def modify_columns(self):
        self.df['statement'] = self.file.filename
        self.df['distributor'] = self.name
        self.df = self.df.reindex(columns=self.columns_for_db)  # Add needed columns, drop extraneous columns

    def insert_to_db(self):
        self.df.to_sql('income_pending', con=db.engine, if_exists='append', index=False)

    def add_missing_version_number(self):
        """album"""
        db.engine.execute("""
        UPDATE
        income_pending
        SET
        version_number = version.version_number
        FROM
        version
        WHERE
        income_pending.upc_id = version.upc
        AND
        income_pending.version_number IS NULL
        """)

class BandcampStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'bandcamp'
        self.encoding = 'utf_16'
        self.dtype = { 'catalog number': 'string', 'sku': 'string' }

    def clean(self):
        self.df.drop(self.df[self.df['item type'] == 'payout'].index, inplace=True)
        types_to_change = ['refund', 'reversal']
        self.df['type'] = np.where(self.df['item type'] == 'track', 'track', self.df['item type'])
        self.df['type'] = np.where(self.df['item type'] != 'track', 'album', self.df['item type'])

        self.df.loc[self.df['item type'].isin(types_to_change), 'net amount'] = self.df['item total']

        self.df.loc[self.df['item type'] == 'refund', 'item type'] = 'physical'
        self.df.loc[self.df['item type'] == 'reversal', 'item type'] = 'physical'
        self.df.loc[self.df['item type'] == 'album', 'item type'] = 'digital'
        self.df.loc[self.df['item type'] == 'track', 'item type'] = 'digital'
        self.df.loc[self.df['item type'] == 'package', 'item type'] = 'physical'


        catalog_df = pd.read_sql_table('catalog', db.engine)
        self.df = self.df.join(catalog_df.set_index('catalog_name'), on='item name')

        # self.df['sku'] = np.where(self.df['item type'] == 'digital', self.df['catalog number'] + 'digi', self.df['sku'])
        # self.df['sku'] = np.where((self.df['item type'] == 'digital') & (self.df['catalog number'].isnull()), self.df['catalog_number'] + 'digi', self.df['sku'])
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['date'] = self.df['date'].dt.strftime('%Y-%m-%d')
        self.df['upc'] = self.df['upc'].astype(str)
        self.df['upc'] = self.df['upc'].str.replace(' ', '')
        self.df['upc'] = self.df['upc'].str.replace('.0', '')
        self.df['catalog number'] = self.df['catalog number'].str.replace(' ', '')


        self.df.rename(columns={'date': 'date',
                                'bandcamp transaction id': 'order_id',
                                'upc': 'upc_id',
                                'isrc': 'isrc_id',
                                'sku': 'version_number',
                                'catalog number': 'catalog_id',
                                'quantity': 'quantity',
                                'net amount': 'amount',
                                'city': 'city',
                                'region/state': 'region',
                                'country': '_country',
                                'country code': 'country',
                                'item type': 'medium',
                                'type': 'type',
                                'item name': 'album_name',
                                'package': 'description',
                                },
                       inplace=True)


class SDSStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'sds'
        self.encoding = 'utf-8'

    def clean(self):
        self.df.drop(self.df[self.df['Period'] == 'Totals'].index, inplace=True)
        self.df['Period'] = '20' + self.df['Period'].str[4:6] + '-' + self.df['Period'].str[1:3] + '-01'
        # self.df['Sales Description'] = np.where(self.df['ISRC'].notnull(), 'track', self.df['ISRC'])
        # self.df['Sales Description'] = np.where(self.df['ISRC'].isnull(), 'album', self.df['ISRC'])
        self.df['medium'] = 'digital'
        self.df['Asset Type'] = np.where(self.df['ISRC'].isnull(), 'album', self.df['Asset Type'])
        self.df['Asset Type'] = self.df['Asset Type'].str.lower()
        # self.df['UPC/EAN'] = self.df['UPC/EAN'].astype(int)

        self.df['Product / Catalog #'] = self.df['Product / Catalog #'].str.replace(' ', '') + 'digi'

        self.df.rename(columns={'Period': 'date',
                                'UPC/EAN': 'upc_id',
                                'ISRC': 'isrc_id',
                                'Quantity Net': 'quantity',
                                'US$ After Fees': 'amount',
                                'Territory': 'country',
                                'Retailer': 'customer',
                                'Sales Description': 'description',
                                'Song':'track_name',
                                'Album': 'album_name',
                                'Asset Type': 'type',
                                'Product / Catalog #': 'version_number'
                                },
                       inplace=True)

class ShopifyStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'shopify'
        self.encoding = 'utf-8'

    def clean(self):
        self.df.drop(self.df[self.df['Transaction type'] == 'shipping'].index, inplace=True)
        self.df['Date'] = self.df['Date'].str[:10]
        self.df['medium'] = 'physical'
        self.df['type'] = 'album'
        self.df.rename(columns={'Date': 'date',
                                'Order ID': 'order_id',
                                'upc': 'upc_id',
                                'isrc': 'isrc_id',
                                'Variant SKU': 'version_number',
                                'catalog number': 'catalog_id',
                                'Net quantity': 'quantity',
                                'Total sales': 'amount',
                                'Shipping city': 'city',
                                'Shipping region': 'region',
                                'Shipping country': 'country',
                                'Product': 'album_name',
                                'Variant': 'description'
                                },
                       inplace=True)


class SDPhysicalStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'sdphysical'
        self.encoding = 'unicode_escape'

    def clean(self):
        """SELECT DESCRIPTION, WHERE Version is SS-000, clip the first characters of Description and MOVE INTO version."""
        self.index_to_put_dash = index_where_to_put_dash(self.df['Catalog Number'][1])
        self.df['Catalog Number'] = np.where(self.df['Catalog Number'].str[-3:] == '000',
                                             self.df['Title_Description'].str.split(' ', expand=True)[0],
                                             self.df['Catalog Number'])

        """This only works with two letter catalog numbers, very specific to Sahel Sounds."""
        self.df['Catalog Number'] = self.df['Catalog Number'].str.upper().str[:2] + '-' + self.df['Catalog Number'].str.lower().str[2:]


        self.df['datePaidlast'] = pd.to_datetime(self.df['datePaidlast'])
        self.df['medium'] = 'physical'
        self.df['type'] = 'album'
        self.df.rename(columns={'datePaidlast': 'date',
                                'Internal Invoice Number': 'order_id',
                                'UPC': 'upc_id',
                                'isrc': 'isrc_id',
                                'Catalog Number': 'version_number',
                                'signedQuantity': 'quantity',
                                'Label Net Total': 'amount',
                                'Customer': 'customer',
                                'Country Code': 'country',
                                'Title_Description': 'description',
                                },
                       inplace=True)


class SDDigitalStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'sddigital'
        self.encoding = 'unicode_escape'

    def clean(self):
        self.df['datePaidlast'] = pd.to_datetime(self.df['datePaidlast'])
        # self.df['UPC'] = np.where(self.df['Product ID'].notnull(), np.nan, self.df['Product ID'])
        self.df['Transaction Type'] = np.where(self.df['Product ID'].isnull(), 'album', self.df['Transaction Type'])
        self.df['Transaction Type'] = np.where(self.df['Product ID'].notnull(), 'track', self.df['Transaction Type'])
        self.df['medium'] = 'digital'
        self.df['UPC'] = self.df['UPC'].apply(str)
        self.df['UPC'] = np.where(self.df['UPC'].notnull(), self.df['UPC'].str.replace('SCDD.', ''), self.df['UPC'])
        self.df.rename(columns={'datePaidlast': 'date',
                                'Internal Invoice Number': 'order_id',
                                'UPC': 'upc_id',
                                'Product ID': 'isrc_id',
                                'Quantity': 'quantity',
                                'Label Net Total': 'amount',
                                'Customer': 'customer',
                                'Country Code': 'country',
                                'Transaction Type': 'type',
                                'Title_Description': 'description',
                                },
                       inplace=True)


class QuickbooksStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'quickbooks'
        self.encoding = 'utf-8'

    def clean(self):
        self.df['medium'] = 'physical'
        self.df['type'] = 'album'

class StatementFactory:
    def get_statement(file, type):
        if type == 'bandcamp':
            return BandcampStatement(file)
        if type == 'shopify':
            return ShopifyStatement(file)
        if type == 'sds':
            return SDSStatement(file)
        if type == 'sdphysical':
            return SDPhysicalStatement(file)
        if type == 'sddigital':
            return SDDigitalStatement(file)
        if type == 'quickbooks':
            return QuickbooksStatement(file)


def insert_initial_values():
    """Initialize distributor table."""
    statements_to_insert = [
        IncomeDistributor(distributor_statement='bandcamp_statement',
                          distributor_name='bandcamp'),
        IncomeDistributor(distributor_statement='shopify_statement',
                          distributor_name = 'shopify'),
        IncomeDistributor(distributor_statement='sdphysical_statement',
                          distributor_name = 'sdphysical'),
        IncomeDistributor(distributor_statement='sddigital_statement',
                          distributor_name='sddigital'),
        IncomeDistributor(distributor_statement='quickbooks_statement',
                          distributor_name='quickbooks'),
        IncomeDistributor(distributor_statement='sds_statement',
                          distributor_name='sds'),
    ]
    db.session.bulk_save_objects(statements_to_insert)
    db.session.commit()

def find_distinct_matching_errors():
    sel = db.session.query(IncomePending.catalog_id,
        IncomePending.distributor,
        IncomePending.upc_id,
        IncomePending.isrc_id,
        IncomePending.version_number,
        IncomePending.catalog_id,
        IncomePending.album_name,
        IncomePending.track_name,
        IncomePending.type,
        IncomePending.medium,
        IncomePending.description,
        cast(IncomePending.amount, db.Numeric(8, 2)).label('amount'),
        IncomePending.id,
        )
    sel = sel.outerjoin(Version, Version.upc == IncomePending.upc_id)
    # sel = sel.outerjoin(Bundle, Bundle.bundle_number == IncomePending.version_number)
    # sel = sel.filter(Version.upc == None).order_by(IncomePending.catalog_id)
    return sel

def process_pending_statements():
    return 's'





