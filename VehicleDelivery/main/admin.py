from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Department)
admin.site.register(Person)
admin.site.register(ClaimModel)
admin.site.register(TransportModel)
admin.site.register(PreparationModel)
admin.site.register(CommunicationModel)
admin.site.register(OtherModel)
admin.site.register(ActionLog)