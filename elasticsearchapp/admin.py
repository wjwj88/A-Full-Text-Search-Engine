from django.contrib import admin
from .models import BlogPost, TargetStatus

# Register your models here.

# Need to register my BlogPost so it shows up in the admin

class TargetAdmin(admin.ModelAdmin):
	list_display = ('targetID','target','annotation','species','status',
		'clone','protein','genePage','uniprot','taxonClass',
		'superkingdom','targetRole','batch','community','maxCode')

admin.site.register(TargetStatus, TargetAdmin)
admin.site.register(BlogPost)