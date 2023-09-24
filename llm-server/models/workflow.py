import mongoengine as me

class Info(me.EmbeddedDocument):
    title = me.StringField(required=True)
    version = me.StringField(required=True)

class Step(me.EmbeddedDocument):
    stepId = me.StringField(required=True)
    operation = me.StringField(required=True) 
    open_api_operation_id = me.StringField(required=True)
    parameters = me.DictField()

class OnSuccess(me.EmbeddedDocument):
    handler = me.StringField(required=True)

class OnFailure(me.EmbeddedDocument):
    handler = me.StringField(required=True)
    
class Flow(me.EmbeddedDocument):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    requires_confirmation = me.BooleanField(required=True)
    steps = me.ListField(me.EmbeddedDocumentField(Step))
    on_success = me.ListField(me.EmbeddedDocumentField(OnSuccess))
    on_failure = me.ListField(me.EmbeddedDocumentField(OnFailure))

class Workflow(me.Document):
    opencopilot = me.StringField(regex=r"^\d+\.\d+$")
    info = me.EmbeddedDocumentField(Info, required=True)
    flows = me.ListField(me.EmbeddedDocumentField(Flow))