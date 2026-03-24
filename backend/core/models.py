from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    
    # --- GRUPO OBRA SOCIAL ---
    obra_social = models.CharField(max_length=100, blank=True, null=True)
    numero_afiliado = models.CharField(max_length=50, blank=True, null=True)
    
    # --- GRUPO MÉDICO ---
    medico_cabecera = models.CharField(max_length=100, blank=True, null=True)

    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    sexo = models.CharField(
        max_length=1, 
        choices=SEXO_CHOICES,
        null=True, 
        blank=True
    )
    
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    informacion_medica = models.TextField(blank=True, null=True, default='')

    # 👇 NUEVO CAMPO: FECHA DE ALTA (Para estadísticas de crecimiento)
    # auto_now_add=True hace que se guarde la fecha/hora exacta AUTOMÁTICAMENTE al crear.
    fecha_alta = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class HistoriaClinica(models.Model):
    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.CASCADE,
        related_name="historia_clinica"
    )

    def __str__(self):
        return f"Historia clínica de {self.paciente}"


class Visita(models.Model):
    paciente = models.ForeignKey(
        'Paciente', 
        on_delete=models.CASCADE, 
        related_name='visitas'
    )
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField()
    archivo = models.FileField(upload_to='visitas/', null=True, blank=True)

    def __str__(self):
        return f"Visita {self.fecha} - {self.paciente}"


class Turno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='turnos_asignados')
    fecha = models.DateField()
    hora = models.TimeField()

    ESTADOS = [
        ('programado', 'Programado'),
        ('espera', 'En Espera'),
        ('atendido', 'Atendido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programado')

    class Meta:
        unique_together = ('medico', 'fecha', 'hora')
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"Turno: {self.fecha} {self.hora} - {self.paciente}"

# 👇 NUEVO MODELO: AUSENCIA (Bloqueo de Agenda) 👇
class Ausencia(models.Model):
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ausencias')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=200, blank=True, null=True) # Ej: "Vacaciones", "Congreso"

    def __str__(self):
        return f"Ausencia {self.medico}: {self.fecha_inicio} al {self.fecha_fin}"