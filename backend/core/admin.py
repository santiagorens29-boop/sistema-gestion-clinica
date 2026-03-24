from django.contrib import admin
# Agregamos Turno y Ausencia a la importación
from .models import Paciente, Visita, Turno, Ausencia 

class VisitaInline(admin.TabularInline):
    model = Visita
    extra = 0
    readonly_fields = ('fecha',)

class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'obra_social')
    search_fields = ('nombre', 'apellido', 'dni')
    inlines = [VisitaInline] 

admin.site.register(Paciente, PacienteAdmin)

# 👇 REGISTRAMOS LOS TURNOS (Para verlos en el admin)
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'medico', 'paciente', 'estado')
    list_filter = ('fecha', 'medico', 'estado')

# 👇 REGISTRAMOS LAS AUSENCIAS (Nuevo)
@admin.register(Ausencia)
class AusenciaAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha_inicio', 'fecha_fin', 'motivo')
    list_filter = ('medico',)