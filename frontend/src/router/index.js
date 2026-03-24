import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import PacientesView from '../views/PacientesView.vue'
import HistoriaClinicaView from '../views/HistoriaClinicaView.vue'
import AgendaView from '../views/AgendaView.vue' 
import NuevoPacienteView from '../views/NuevoPacienteView.vue'
import EditarPacienteView from '../views/EditarPacienteView.vue'
import TableroMedicoView from '../views/TableroMedicoView.vue'
import DashboardView from '../views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    
    // --- ZONA SECRETARIA ---
    {
      path: '/agenda',
      name: 'agenda',
      component: AgendaView,
      meta: { requiresSecretaria: true } 
    },

    // --- ZONA MÉDICO/DIRECTOR ---
    {
      path: '/tablero',
      name: 'tablero',
      component: TableroMedicoView,
      meta: { requiresMedico: true } 
    },
    {
      path: '/pacientes',
      name: 'pacientes',
      component: PacientesView,
      meta: { requiresAuth: true } 
    },
    {
      path: '/pacientes/nuevo',
      name: 'nuevo-paciente',
      component: NuevoPacienteView,
      meta: { requiresAuth: true }
    },
    {
      path: '/pacientes/:id/editar',
      name: 'editar-paciente',
      component: EditarPacienteView,
      meta: { requiresAuth: true }
    },
    {
      path: '/pacientes/:id/historia',
      name: 'historia',
      component: HistoriaClinicaView,
      meta: { requiresMedico: true } 
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true } // Para que solo entren logueados
    },
  ]
})

// --- 👮‍♂️ EL GUARDIA DE SEGURIDAD (ACTUALIZADO PARA DIRECTOR) ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('userToken');
  
  const esMedico = localStorage.getItem('esMedico') === 'true'; 
  const esSecretaria = localStorage.getItem('esSecretaria') === 'true';
  const esDirector = localStorage.getItem('esDirector') === 'true'; // <--- LEEMOS AL DIRECTOR

  // 1. Rutas públicas
  if (!to.meta.requiresAuth && !to.meta.requiresMedico && !to.meta.requiresSecretaria) {
      return next();
  }

  // 2. Requiere login
  if (!token) {
      return next('/login');
  }

  // 3. REGLAS DE ACCESO

  // Si pide Secretaria
  if (to.meta.requiresSecretaria) {
      if (esSecretaria) return next();
      return next((esMedico || esDirector) ? '/tablero' : '/login');
  }

  // Si pide Médico (Tablero o Historia)
  if (to.meta.requiresMedico) {
      // AQUÍ ESTÁ EL CAMBIO: Si es Médico O es Director, pasa.
      if (esMedico || esDirector) return next(); 
      
      return next(esSecretaria ? '/agenda' : '/login');
  }

  next();
});

export default router