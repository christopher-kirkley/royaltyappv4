import pandas as pd
import numpy as np

from royaltyapp.models import db, IncomePending, Version, Track, Bundle

from sqlalchemy import cast, or_, update

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
            'artist_name',
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
        
        """Method works for working CSV, but for larger df will timeout"""
        """Better method to convert to StringIO or temporary CSV then use bulk insert."""
        self.df.to_sql('income_pending', chunksize=1000, method='multi', con=db.engine, if_exists='append', index=False)



    def find_imported_records(self):
        res = len(db.session.query(IncomePending)
                .filter(IncomePending.statement == self.file.filename)
                .all()
                )
        return res

    

class BandcampStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'bandcamp'
        self.encoding = 'utf_16'
        self.dtype = { 'catalog number': 'string', 'sku': 'string', 'upc': 'string' }

    def clean(self):
        self.df.drop(self.df[self.df['item type'] == 'payout'].index, inplace=True)
        self.df.drop(self.df[self.df['item type'] == 'adjustment'].index, inplace=True)
        types_to_change = ['refund', 'reversal']
        self.df['type'] = np.where(self.df['item type'] == 'track', 'track', self.df['item type'])
        self.df['type'] = np.where(self.df['item type'] != 'track', 'album', self.df['item type'])

        # self.df.loc[self.df['item type'].isin(types_to_change), 'net amount'] = self.df['item total']

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

        self.df['upc'] = self.df['upc'].str.replace(' ', '')

        """Zero out upc column for physical items, these are inconsitent for matching."""
        self.df['upc'] = np.where(self.df['item type'] == 'physical', '', self.df['upc'])

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

        self.df['track_name'] = self.df['album_name']


class SDSStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'sds'
        self.encoding = 'utf-8'
        self.dtype = { 'UPC/EAN': 'string'}

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
        self.dtype = {}

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
        self.dtype = { 'UPC': 'string' }

    def clean(self):
        self.df['Catalog Number'] = np.where(
                self.df['Artist'].str.contains('Label Credit'),
                self.df['Title_Description'].str.split(' ', expand=True)[0],
                self.df['Catalog Number'])


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
                                'Artist': 'artist_name',
                                },
                       inplace=True)


class SDDigitalStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'sddigital'
        self.encoding = 'unicode_escape'
        self.dtype = { 'UPC': 'string' }
        
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
                                'Product Title': 'track_name',
                                },
                       inplace=True)

        print('clean sd')

class QuickbooksStatement(Statement):
    def __init__(self, file):
        super().__init__(file)
        self.name = 'quickbooks'
        self.encoding = 'utf-8'
        self.dtype = {}

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

def find_distinct_version_matching_errors():
    version_error = db.session.query(
            IncomePending.catalog_id,
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
    version_error = version_error.filter(IncomePending.type == 'album')
    version_error = version_error.outerjoin(Version, Version.upc == IncomePending.upc_id)
    version_error = version_error.filter(Version.upc == None)
    version_error = version_error.outerjoin(Bundle, Bundle.upc == IncomePending.upc_id)
    version_error = version_error.filter(Bundle.upc == None)

    return version_error


def find_distinct_track_matching_errors():

    track_error = db.session.query(
            IncomePending.catalog_id,
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
    track_error = track_error.filter(IncomePending.type == 'track')
    track_error = track_error.outerjoin(Track, Track.isrc == IncomePending.isrc_id)
    track_error = track_error.filter(Track.isrc == None)

    return track_error


def process_pending_statements():
    return 's'


def find_distinct_refund_matching_errors():

    query = (db.session.query(
            IncomePending.order_id)
            .filter(IncomePending.amount == None)
            .all())
    order_ids = [ order.order_id for order in query ]

    refund_error = db.session.query(
            IncomePending.catalog_id,
            IncomePending.order_id,
            IncomePending.distributor,
            IncomePending.amount,
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
    refund_error = refund_error.filter(IncomePending.order_id.in_(order_ids))

    return refund_error






