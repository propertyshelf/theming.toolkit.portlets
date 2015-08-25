# -*- coding: utf-8 -*-
"""View with Results of AjaxSearch"""

from plone.memoize.view import memoize
from Products.Five.browser import BrowserView, pagetemplatefile
# from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.traversing.browser.absoluteurl import absoluteURL

# plone.mls.listing imports
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.api import search

PRICE_SALE_VALUES = {
    'all': {"min": None, "max": None},
    '250k': {"min": 250000, "max": 500000},
    '500k': {"min": 500000, "max": 750000},
    '750k': {"min": 750000, "max": 1000000},
    '1000k': {"min": 1000000, "max": None}
}

PRICE_RENT_VALUES = {
    'all': {"min": None, "max": None},
    '150': {"min": 150 * 30, "max": 300 * 30},
    '300': {"min": 300 * 30, "max": 500 * 30},
    '500': {"min": 500 * 30, "max": 750 * 30},
    '750': {"min": 750 * 30, "max": 1000 * 30},
    '1000': {"min": 1000 * 30, "max": None}
}


def encode_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict


def get_minmax(beds):
    """Set Min&Max value for beds"""
    out_dict = {}
    min_beds = 0
    max_beds = 0

    for v in beds:
        value = int(v)

        if value > 0 and min_beds < 1 and max_beds < 1:
            min_beds = value
            max_beds = value

        if value < min_beds:
            min_beds = value

        if value > max_beds:
            max_beds = value

    out_dict['Min'] = min_beds
    out_dict['Max'] = max_beds

    return out_dict


class AjaxSearch(BrowserView):
    """Deliver search results for ajax calls"""
    index = pagetemplatefile.ViewPageTemplateFile('templates/ajax_template.pt')  # noqa

    _listings = None
    _batching = None
    _isRental = None
    _isSale = None
    _isLot = None
    _limit = None
    _agency_listings = None

    def __init__(self, context, request):
        super(AjaxSearch, self).__init__(context, request)
        self.context = context
        self.request = request
        self.update()

    def __call__(self):
        return self.render()

    def update(self):
        self.portal_state = queryMultiAdapter((self.context, self.request), name='plone_portal_state')  # noqa
        self.context_state = queryMultiAdapter((self.context, self.request), name='plone_context_state')  # noqa

        self.request.form = encode_dict(self.request.form)
        request_params = self._get_params
        self._get_listings(request_params)

    @property
    def limit(self):
        """get a limit from the request or set 12"""
        if self._limit is not None:
            return self._limit
        return 16

    @property
    def agency_exclusive(self):
        """show only agenty listings?"""
        if self._agency_listings is not None:
            return self._agency_listings
        return True

    def render(self):
        """Prepare view related data."""
        return self.index()

    def __listing_type(self, raw):
        lt = ''

        if not isinstance(raw, (list, tuple, )):
            return lt

        if 'sale' in raw:
            lt += 'rs, cs,'
            self._isSale = True

        # land listings
        if 'lot' in raw:
            lt = 'll,'

            self._isSale = True
            self._isLot = True

        elif self._isSale:
            # also show land listings if only "Sale" is selected
            lt += 'll,'
            self._isLot = False

        if 'rental' in raw:
            lt += 'rl, cl'
            self._isRental = True

        return lt

    def __object_type(self, raw):
        ot = ''
        # condo? no problem.
        if 'condo' in raw:
            ot += 'condominium,'
        # if "home" is set, objecttype is house
        if 'home' in raw:
            ot += 'house'

        return ot

    def __view_type(self, raw):
        viewtype = ''

        if 'ocean_view' in raw:
            viewtype += 'ocean_view'

        if 'garden_view' in raw:
            if len(viewtype) > 0:
                viewtype += ','
            viewtype += 'garden_view'

        if 'oceanfront' in raw:
            if len(viewtype) > 0:
                viewtype += ','
            viewtype += 'other'

        return viewtype

    def __price(self, mode, params):
        min_max = self._pricerange(params)

        if min_max is not None and mode == 'min':
            params['price_min'] = min_max.get('min', None)
            if params['price_min'] is not None:
                try:
                    return int(params['price_min'])
                except Exception:
                    """"""
                    return None
            return None

        if min_max is not None and mode == 'max':
            params['price_max'] = min_max.get('max', None)
            if params['price_max'] is not None and params['price_max'] != '':
                try:
                    return int(params['price_max'])

                except Exception:
                    """"""
                    return None
            return None

    def prepare_search_params(self, data):
        """Prepare search params."""
        params = {}

        for item in data:
            raw = data[item]

            # map the custom listing types to the mls search
            if item == 'form.widgets.listing_type':
                params['listing_type'] = self.__listing_type(raw)
                # special object types?
                params['object_type'] = self.__object_type(raw)

            # pool: add only if Yes or No is selected (get all otherwise)
            # new feature: disable pool when land listing
            if item == 'form.widgets.pool' and raw != '--NOVALUE--' and not self._isLot:  # noqa
                params['pool'] = raw

            if item == 'form.widgets.beds' and not self._isLot:
                raw_min_max = get_minmax(raw)
                params['beds_min'] = raw_min_max['Min']
                params['beds_max'] = raw_min_max['Max']

            # reset form.widgets.view_type
            if item == 'form.widgets.view_type' and isinstance(raw, (list, tuple,)):  # noqa
                params['view_type'] = self.__view_type(raw)

            # Remove all None-Type values.
            if raw is not None or raw == '--NOVALUE--':
                if isinstance(raw, unicode):
                    raw = raw.encode('utf-8')
                params[item] = raw

        # detect min/max price
        params['price_min'] = self.__price('min', params)
        params['price_max'] = self.__price('max', params)

        return params

    def _pricerange(self, params):
        """Determine which Min and Max prices to use"""
        price_range = {}
        price_range['min'] = None
        price_range['max'] = None

        # if its a Rental&Sales Search OR neither one of these:
        # price range is empty
        if (self._isRental and self._isSale) or not(self._isRental or self._isSale):  # noqa
            return price_range
        # only rentals: use rental Price ranges
        elif self._isRental:
            range_key = params.get('form.widgets.price_rent', None)

            if range_key is not None:
                range_price = PRICE_RENT_VALUES.get(range_key, None)
            else:
                return price_range

            if range_price is not None:
                price_range['min'] = range_price.get('min', None)
                price_range['max'] = range_price.get('max', None)
                return price_range
            else:
                return price_range

        # only sales: use Sales Price ranges
        elif self._isSale:
            range_key = params.get('form.widgets.price_sale', None)
            range_price = None

            if range_key is not None:
                range_price = PRICE_SALE_VALUES.get(range_key, None)

            if range_price is not None:
                price_range['min'] = range_price.get('min', None)
                price_range['max'] = range_price.get('max', None)
                return price_range
            else:
                return price_range

        else:
            return price_range

    @property
    def _get_params(self):
        """map MLS search with custom UI"""
        params = self.request.form
        return self.prepare_search_params(params)

    def _get_listings(self, params):
        """Query the recent listings from the MLS."""

        search_params = {
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
            'lang': self.portal_state.language(),
            'agency_listings': self.agency_exclusive
        }
        search_params.update(params)

        results, batching = search(search_params, context=self.context)

        if len(results) < 1:
            # Retry search
            results, batching = search(search_params, context=self.context)

        self._listings = results
        self._batching = batching

    @property
    @memoize
    def listings(self):
        """Return listing results."""
        return self._listings

    @memoize
    def view_url(self):
        """Generate view url."""
        if self.context_state.is_view_template():
            my_url = absoluteURL(self.context, self.request) + '/'
        else:
            my_url = self.context_state.current_base_url()

        # remove @@ params from the url
        my_split = my_url.split('@@')
        my_url = my_split[0]

        return my_url

    @property
    def batching(self):
        return ListingBatch(self.listings, self.limit,
                            self.request.get('b_start', 0), orphan=1,
                            batch_data=self._batching)
