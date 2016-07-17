# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime
from hashlib import md5
import logging
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi


class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            desc = item.get('description') or ''
            if word in desc.lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item


class RequiredFieldsPipeline(object):
    """A pipeline to ensure the item have the required fields."""

    required_fields = ('name', 'description', 'url')

    def process_item(self, item, spider):
        for field in self.required_fields:
            if not item.get(field):
                raise DropItem("Field '%s' missing: %r" % (field, item))
        return item


class MySQLStorePipeline(object):
    """A pipeline to store the item in a MySQL database.

    This implementation uses Twisted's asynchronous database API.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        pid = item['pid']
        # now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM products WHERE product_id = %s
        )""", (pid, ))
        ret = conn.fetchone()[0]

        if ret:
            conn.execute("""
                UPDATE products
                SET product_name=%s, product_description=%s, product_default_image=%s, product_sizes=%s, sku=%s, date_added=%s, colors=%s, price=%s, category_id=%s, classification=%s
                WHERE product_id=%s
            """, (item['pname'], item['pdesc'], item['pimage'], item['psize'], item['psku'], item['pdate'], item['pcolor'], item['pprice'] , item['pgid'], item['pclass'], item['pid']))
            logging.log(logging.ERROR, "Item updated in db: %s %r" % (pid, item))
        else:
            conn.execute("""
                INSERT INTO products (product_id, product_name, product_description, product_default_image, product_sizes, sku, date_added, colors, price, category_id, classification)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (pid, item['pname'], item['pdesc'], item['pimage'], item['psize'], item['psku'], item['pdate'], item['pcolor'], item['pprice'] , item['pgid'], item['pclass']))
            logging.log(logging.ERROR, "Item stored in db: %r" % (item))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        logging.log(logging.ERROR, failure)

    def _get_guid(self, item):
        """Generates an unique identifier for a given item."""
        # hash based solely in the url field
        return md5(item['url']).hexdigest()


class ShoppingPipeline(object):

    def process_item(self, item, spider):
        return item
