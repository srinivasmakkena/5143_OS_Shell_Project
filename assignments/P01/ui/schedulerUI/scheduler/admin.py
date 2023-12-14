from django.contrib import admin
from .models import Process_model
from django.http import HttpResponse
import csv
from django.db.models import Avg

admin.site.site_header = "System Moniter - Scheduler"
admin.site.site_title = "System Moniter - Scheduler"
admin.site.index_title = "System Moniter - Scheduler"
admin.site.site_url = "/scheduler"
    
class ProcessModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'time_spent_in_wait_queue', 'time_spent_in_ready_queue', 'time_spent_in_running_queue', 'time_spent_in_IO_queue', 'message', 'response')
    actions = ['export_table_as_csv']

    def export_table_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="process_table.csv"'

        writer = csv.writer(response)
        fields = [field.name for field in Process_model._meta.fields]

        # Write header
        writer.writerow(fields)

        # Write data
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in fields])

        return response

    export_table_as_csv.short_description = "Export entire table as CSV"
# Register the ProcessModelAdmin
admin.site.register(Process_model, ProcessModelAdmin)
