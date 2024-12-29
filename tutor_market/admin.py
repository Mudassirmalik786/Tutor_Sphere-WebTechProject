from django.contrib import admin

from tutor_market.models import Rating, Student, Subject, Tutor, Value,Message,Conversation


admin.site.site_header = 'Tutor Sphere Administration'
admin.site.site_title = 'Tutor Sphere Admin'
admin.site.index_title = 'Tutor Sphere Administration'

admin.site.register(Tutor)
admin.site.register(Rating)
admin.site.register(Subject)
admin.site.register(Value)
admin.site.register(Student)
admin.site.register(Conversation)
admin.site.register(Message)
