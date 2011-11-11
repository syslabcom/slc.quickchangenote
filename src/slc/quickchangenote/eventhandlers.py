from Acquisition import aq_inner
from zope.interface import implements 
from zope.component import adapts, queryUtility
from zope.annotation.interfaces import IAnnotations
from plone.registry.interfaces import IRegistry
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.Archetypes.interfaces import IBaseContent
from Products.CMFCore.utils import getToolByName
from slc.quickchangenote.utils import changenoteRequired
from slc.quickchangenote import MessageFactory as _

def isVersionable(ob):
    try:
        pr = getToolByName(ob, 'portal_repository')
    except AttributeError:
        return None
    return pr.isVersionable(ob);

class ValidateChangenote(object):
    """ Validate that the user has provided a change note. """
    implements(IObjectPostValidation)
    adapts(IBaseContent)
    field_name = 'cmfeditions_version_comment'

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        # Archetypes will call us three times, and that complicates things.
        # Either the change note is there or it isn't. If its there the first
        # time, its not about to disappear during the processing of the
        # request. Therefore annotate the return value on the request.
        cache_key = "validate_changenote_result"
        _marker = object()
        cache = IAnnotations(request)
        data = cache.get(cache_key, _marker)
        if data is not _marker:
            return data

        context = aq_inner(self.context)
        if changenoteRequired(context):
            if isVersionable(context):
                value = request.form.get(self.field_name,
                    request.get(self.field_name, ''))
                if len(value) == 0:
                    errors = {self.field_name: _(
                        u'A change note must be provided')}
                    cache[cache_key] = errors
                    return errors
        cache[cache_key] = None
        return None