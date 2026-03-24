from rest_framework import generics, permissions, filters
from django.contrib.auth.models import User, Group
from .models import Paciente, Visita, Turno, Ausencia 
from .serializers import PacienteSerializer, VisitaSerializer, TurnoSerializer, UserSerializer, AusenciaSerializer
from rest_framework.views import APIView           
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
# 👇 NUEVAS IMPORTACIONES PARA LAS ESTADÍSTICAS
from django.db.models import Count
import datetime 

class PacienteListAPIView(generics.ListCreateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'apellido', 'dni']

class PacienteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]

class VisitaListCreateView(generics.ListCreateAPIView):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        usuario_actual = self.request.user
        if isinstance(usuario_actual, str):
            usuario_actual = User.objects.get(username=usuario_actual)
        serializer.save(medico=usuario_actual)

class TurnoListCreateView(generics.ListCreateAPIView):
    serializer_class = TurnoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Turno.objects.all()
        user = self.request.user

        es_medico = user.groups.filter(name='Medicos').exists()
        es_director = user.groups.filter(name='Directores').exists() or user.is_superuser

        if es_medico and not es_director:
            queryset = queryset.filter(medico=user)
        
        medico_id = self.request.query_params.get('medico')
        if medico_id:
            queryset = queryset.filter(medico_id=medico_id)

        fecha = self.request.query_params.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        return queryset

class TurnoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedicoListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(groups__name__in=['Medicos', 'Directores']).distinct()

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'nombre_completo': f"{user.first_name} {user.last_name}",
            'username': user.username,
            'es_medico': user.groups.filter(name='Medicos').exists(),
            'es_secretaria': user.groups.filter(name='Secretarias').exists(),
            'es_director': user.groups.filter(name='Directores').exists() or user.is_superuser
        })

class AusenciaListCreateView(generics.ListCreateAPIView):
    serializer_class = AusenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Ausencia.objects.all()
        medico_id = self.request.query_params.get('medico')
        if medico_id:
            queryset = queryset.filter(medico_id=medico_id)
        return queryset

    # 👇 ESTO ES LO ÚNICO QUE AGREGAMOS 👇
    def perform_create(self, serializer):
        user = self.request.user
        es_medico = user.groups.filter(name='Medicos').exists()
        es_director = user.groups.filter(name='Directores').exists() or user.is_superuser

        # Si es médico y NO es director/secretaria, forzamos que la ausencia sea para ÉL
        if es_medico and not es_director:
            serializer.save(medico=user)
        else:
            # Si es secretaria o director, dejamos que guarde el médico que eligió en el formulario
            serializer.save()

class AusenciaDetailView(generics.RetrieveDestroyAPIView):
    queryset = Ausencia.objects.all()
    serializer_class = AusenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

# 👇 NUEVA VISTA DE ESTADÍSTICAS (NO TOCA NADA ANTERIOR) 👇
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 👇 AGREGA ESTE BLOQUE DE SEGURIDAD 👇
        es_director = request.user.groups.filter(name='Directores').exists() or request.user.is_superuser
        if not es_director:
            return Response({'detail': 'No tienes permisos de Director.'}, status=403)
        hoy = datetime.date.today()
        mes_actual = hoy.month
        anio_actual = hoy.year

        # 1. RANKING: ¿Quién trabajó más este mes?
        ranking_medicos = Turno.objects.filter(
            fecha__month=mes_actual, 
            fecha__year=anio_actual
        ).values('medico__last_name', 'medico__first_name').annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        data_ranking = []
        for r in ranking_medicos:
            # Armamos el nombre "Dr. Perez Juan"
            nombre = f"Dr. {r['medico__last_name']} {r['medico__first_name']}"
            data_ranking.append({'name': nombre, 'value': r['total']})

        # 2. AUSENTISMO: Presentes (Espera/Atendido) vs Ausentes (Programado vencido)
        presentes = Turno.objects.filter(estado__in=['espera', 'atendido']).count()
        ausentes = Turno.objects.filter(estado='programado', fecha__lt=hoy).count()

        # 3. CRECIMIENTO: Pacientes creados este mes
        nuevos_pacientes = Paciente.objects.filter(
            fecha_alta__month=mes_actual,
            fecha_alta__year=anio_actual
        ).count()
        total_pacientes = Paciente.objects.count()

        return Response({
            'ranking_medicos': data_ranking,
            'ausentismo': {'presentes': presentes, 'ausentes': ausentes},
            'pacientes': {'nuevos_mes': nuevos_pacientes, 'total': total_pacientes}
        })