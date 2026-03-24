from django.urls import path
# 👇 IMPORTAMOS LA NUEVA VISTA
from .views import (
    PacienteListAPIView, PacienteDetailAPIView, VisitaListCreateView, 
    TurnoListCreateView, TurnoDetailView, MedicoListView, CurrentUserView,
    LoginView, AusenciaListCreateView, AusenciaDetailView,
    DashboardStatsView # <--- AGREGADO
)

urlpatterns = [
    path('pacientes/', PacienteListAPIView.as_view(), name='pacientes-list'),
    path('pacientes/<int:pk>/', PacienteDetailAPIView.as_view(), name='paciente-detail'),
    
    path('visitas/', VisitaListCreateView.as_view(), name='visitas-list-create'),
    
    path('turnos/', TurnoListCreateView.as_view(), name='turno-list'),
    path('turnos/<int:pk>/', TurnoDetailView.as_view(), name='turno-detail'),

    path('medicos/', MedicoListView.as_view(), name='medico-list'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),

    path('api-token-auth/', LoginView.as_view(), name='api_token_auth'),
    path('api/auth/me/', CurrentUserView.as_view(), name='current_user'),

    path('ausencias/', AusenciaListCreateView.as_view(), name='ausencias-list'),
    path('ausencias/<int:pk>/', AusenciaDetailView.as_view(), name='ausencia-detail'),

    # 👇 NUEVA RUTA PARA EL DASHBOARD
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]