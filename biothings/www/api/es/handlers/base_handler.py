from biothings.www.api.helper import BaseHandler
from biothings.utils.common import dotdict, is_str
import re
import logging

class BaseESRequestHandler(BaseHandler):
    # override these in child class
    control_kwargs = {}
    es_kwargs = {}
    esqb_kwargs = {}
    transform_kwargs = {}

    def initialize(self, web_settings):
        ''' Initializations common to all ES Request Handlers here '''
        super(BaseESRequestHandler, self).initialize(web_settings)

    def _return_data_and_track(self, data, ga_event_data={}, rawquery=False):
        ''' Small function to return a chunk of data and send a google analytics tracking request.'''
        if rawquery:
            self.return_raw_query_json(data)
        else:
            self.return_json(data)
        self.ga_track(event=self.ga_event_object(ga_event_data))
        return

    def return_raw_query_json(self, query):
        _ret = query.get('body', {'GET': query.get('bid')})
        if is_str(_ret) and len(_ret.split('\n')) > 1:
            self.return_json({'body': _ret})
        else:
            self.return_json(_ret)  

    def _should_sanitize(self, param, kwargs):
        return ((param in kwargs) and (param in self.kwarg_settings))

    def _sanitize_source_param(self, kwargs):
        if self._should_sanitize('_source', kwargs):
            if len(kwargs['_source']) == 1 and kwargs['_source'][0].lower() == 'all':
                kwargs['_source'] = True
        return kwargs

    def _sanitize_sort_param(self, kwargs):
        if self._should_sanitize('sort', kwargs):
            dirty_sort = kwargs['sort']
            kwargs['sort'] = [{field[1:]:{"order":"desc"}} if field.startswith('-') 
                else {field:{"order":"asc"}} for field in dirty_sort]
        return kwargs

    def _sanitize_size_param(self, kwargs):
        # cap size
        if self._should_sanitize('size', kwargs):
            kwargs['size'] = kwargs['size'] if (kwargs['size'] < 
                self.web_settings.ES_SIZE_CAP) else self.web_settings.ES_SIZE_CAP
        return kwargs

    def get_cleaned_options(self, kwargs):
        ''' Get options for handlers using ES requests '''
        options = dotdict()

        # split kwargs into one (or more) of 4 categories:
        #   * control_kwargs:  kwargs that control aspects of the handler's pipeline (e.g. raw, rawquery)
        #   * es_kwargs: kwargs that go directly to the ES query (e.g. fields, size, ...)
        #   * esqb_kwargs: kwargs that go directly to the ESQueryBuilder instance
        #   * transform_kwargs: kwargs that go directly to the response transformer (e.g. jsonld, dotfield)

        for kwarg_category in ["control_kwargs", "es_kwargs", "esqb_kwargs", "transform_kwargs"]:
            options.setdefault(kwarg_category, dotdict())
            for option, settings in getattr(self, kwarg_category, {}).items():
                if kwargs.get(option, None) or settings.get('default', None) is not None:
                    options.get(kwarg_category).setdefault(option, kwargs.get(option, settings['default']))
        return options

    def _sanitize_params(self, kwargs):
        kwargs = super(BaseESRequestHandler, self)._sanitize_params(kwargs)
        kwargs = self._sanitize_source_param(kwargs)
        kwargs = self._sanitize_size_param(kwargs)
        kwargs = self._sanitize_sort_param(kwargs)
        return kwargs
    
    def _get_es_index(self, options):
        ''' Override to change query index for this request. '''
        return self.web_settings.ES_INDEX

    def _get_es_doc_type(self, options):
        ''' Override to change doc_type for this request. '''
        return self.web_settings.ES_DOC_TYPE

    def _pre_query_builder_GET_hook(self, options):
        ''' Override me. '''
        return options

    def _pre_query_GET_hook(self, options, query):
        ''' Override me. '''
        return query

    def _pre_transform_GET_hook(self, options, res):
        ''' Override me. '''
        return res

    def _pre_finish_GET_hook(self, options, res):
        ''' Override me. '''
        return res
    
    def _pre_query_builder_POST_hook(self, options):
        ''' Override me. '''
        return options

    def _pre_query_POST_hook(self, options, query):
        ''' Override me. '''
        return query

    def _pre_transform_POST_hook(self, options, res):
        ''' Override me. '''
        return res

    def _pre_finish_POST_hook(self, options, res):
        ''' Override me. '''
        return res