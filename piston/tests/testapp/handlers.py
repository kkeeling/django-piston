from django.core.paginator import Paginator

from piston.handler import BaseHandler
from piston.utils import rc, validate

from piston.tests.testapp.models import TestModel, IntegerTestModel, ExpressiveTestModel, Comment, InheritedModel, PlainOldObject, Issue58Model, ListFieldsModel
from piston.tests.testapp.forms import EchoForm
from piston.tests.testapp import signals

class EntryHandler(BaseHandler):
    model = TestModel
    allowed_methods = ['GET', 'PUT', 'POST']

    def read(self, request, pk=None):
        signals.entry_request_started.send(sender=self, request=request)
        if pk is not None:
            return TestModel.objects.get(pk=int(pk))
        paginator = Paginator(TestModel.objects.all(), 25)
        return paginator.page(int(request.GET.get('page', 1))).object_list

    def update(self, request, pk):
        signals.entry_request_started.send(sender=self, request=request)

    def create(self, request):
        signals.entry_request_started.send(sender=self, request=request)

class ExpressiveHandler(BaseHandler):
    model = ExpressiveTestModel
    fields = ('title', 'content', ('comments', ('content',)))

    @classmethod
    def comments(cls, em):
        return em.comments.all()

    def read(self, request):
        inst = ExpressiveTestModel.objects.all()
        
        return inst
        
    def create(self, request):
        if request.content_type and request.data:
            data = request.data
            
            em = self.model(title=data['title'], content=data['content'])
            em.save()
            
            for comment in data['comments']:
                Comment(parent=em, content=comment['content']).save()
                
            return rc.CREATED
        else:
            super(ExpressiveHandler, self).create(request)
            
class NullZeroIntegerHandler(BaseHandler):
    """
    Handler should return all keys of the object, regardless of its value.
    """
    fields = ('id', 'name', 'offices_count')
    model = IntegerTestModel

    def read(self, request):
        return IntegerTestModel.objects.all()

class AbstractHandler(BaseHandler):
    fields = ('id', 'some_other', 'some_field')
    model = InheritedModel
    
    def read(self, request, id_=None):
        if id_:
            return self.model.objects.get(pk=id_)
        else:
            return super(AbstractHandler, self).read(request)

class PlainOldObjectHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('type', 'field')
    model = PlainOldObject
    
    def read(self, request):
        return self.model()

class EchoHandler(BaseHandler):
    allowed_methods = ('GET', 'HEAD')

    @validate(EchoForm, 'GET')
    def read(self, request):
        return {'msg': request.form.cleaned_data['msg']}

class ListFieldsHandler(BaseHandler):
    model = ListFieldsModel
    fields = ('id','kind','variety','color')
    list_fields = ('id','variety')

class Issue58Handler(BaseHandler):
    model = Issue58Model

    def read(self, request):
        return Issue58Model.objects.all()
                
    def create(self, request):
        if request.content_type:
            data = request.data
            em = self.model(read=data['read'], model=data['model'])
            em.save()
            return rc.CREATED
        else:
            super(Issue58Model, self).create(request)
