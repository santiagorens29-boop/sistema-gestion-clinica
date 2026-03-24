from rest_framework import serializers
from .models import Paciente, Visita, Turno, Ausencia  # <--- AGREGADO Ausencia
from django.contrib.auth.models import User

class VisitaSerializer(serializers.ModelSerializer):
    nombre_medico = serializers.ReadOnlyField(source='medico.first_name')
    apellido_medico = serializers.ReadOnlyField(source='medico.last_name')

    class Meta:
        model = Visita
        fields = ['id', 'paciente', 'medico', 'fecha', 'observacion',
                  'archivo', 'nombre_medico', 'apellido_medico']    
        read_only_fields = ['fecha', 'medico', 'nombre_medico', 'apellido_medico']

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = "__all__"

class TurnoSerializer(serializers.ModelSerializer):
    nombre_paciente = serializers.ReadOnlyField(source='paciente.nombre')
    apellido_paciente = serializers.ReadOnlyField(source='paciente.apellido')
    nombre_medico = serializers.ReadOnlyField(source='medico.first_name')
    apellido_medico = serializers.ReadOnlyField(source='medico.last_name')

    class Meta:
        model = Turno
        fields = [
            'id', 'paciente', 'nombre_paciente', 'apellido_paciente',
            'medico', 'nombre_medico', 'apellido_medico',
            'fecha', 'hora', 'estado'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# 👇 NUEVO SERIALIZER PARA BLOQUEOS 👇
class AusenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ausencia
        fields = '__all__'