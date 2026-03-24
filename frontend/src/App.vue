<script setup>
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
import { ref, watch, onMounted } from 'vue'

const router = useRouter()
const route = useRoute() 

const isLogged = ref(false)
const esMedico = ref(false)
const esSecretaria = ref(false) 
const esDirector = ref(false)

const verificarSesion = () => {
  const token = localStorage.getItem('userToken')
  const rolMedico = localStorage.getItem('esMedico')
  const rolSecretaria = localStorage.getItem('esSecretaria')
  const rolDirector = localStorage.getItem('esDirector')

  if (token) {
    isLogged.value = true
    esMedico.value = (rolMedico === 'true')
    esSecretaria.value = (rolSecretaria === 'true')
    esDirector.value = (rolDirector === 'true')
  } else {
    isLogged.value = false
    esMedico.value = false
    esSecretaria.value = false
    esDirector.value = false
  }
}

onMounted(() => {
  verificarSesion()
})

watch(route, () => {
  verificarSesion()
})

const cerrarSesion = () => {
  localStorage.removeItem('userToken')
  localStorage.removeItem('esMedico')
  localStorage.removeItem('esSecretaria')
  localStorage.removeItem('esDirector')
  
  isLogged.value = false
  esMedico.value = false
  esSecretaria.value = false
  esDirector.value = false
  
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="navbar">
      
      <div class="marca-container" @click="router.push('/')" style="cursor: pointer;">
          <img src="/logo.png" alt="Logo" class="logo-nav">
          <span class="marca-texto">CAMI</span>
      </div>
      
      <nav class="menu-items">
        
        <RouterLink to="/" class="nav-link">Inicio</RouterLink>
        
        <RouterLink v-if="isLogged && (!esMedico && !esDirector)" to="/agenda" class="nav-link">
            📅 Turnos
        </RouterLink>
        
        <RouterLink v-if="isLogged && (esMedico || esDirector)" to="/tablero" class="nav-link">
            👨‍⚕️ Agenda
        </RouterLink>
        
        <RouterLink v-if="isLogged && (esMedico || esSecretaria || esDirector)" to="/pacientes" class="nav-link">
            👥 Pacientes
        </RouterLink>

        <RouterLink v-if="isLogged && esDirector" to="/dashboard" class="nav-link">
            📊 Estadísticas
        </RouterLink>

        <div class="auth-buttons">
            <div v-if="!isLogged">
                <RouterLink to="/login" class="btn-login">🔑 Entrar</RouterLink>
            </div>
            <div v-else>
                <button @click="cerrarSesion" class="btn-logout">🚪 Salir</button>
            </div>
        </div>

      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>
/* 1. HEADER PRINCIPAL (STICKY) */
.app-header {
  background-color: #e67e22; /* NARANJA CORPORATIVO */
  padding: 0 20px;
  width: 100%;
  height: 70px; /* Altura fija para consistencia */
  box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* Sombra elegante */
  
  /* HACE QUE EL MENÚ SE QUEDE PEGADO ARRIBA AL BAJAR */
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
}

/* 2. LOGO */
.marca-container {
    display: flex;
    align-items: center;
    gap: 10px;
    background-color: transparent !important;
}

.logo-nav {
    height: 45px; /* Un poco más grande para que luzca */
    width: auto;
    filter: drop-shadow(0 2px 2px rgba(0,0,0,0.1)); /* Sombra sutil al logo */
}

.marca-texto {
    color: white;
    font-weight: 800;
    font-size: 1.5rem;
    letter-spacing: 1px;
}

/* 3. ENLACES DEL MENÚ */
.menu-items {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9); 
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  padding: 8px 15px;
  border-radius: 20px; /* Forma de píldora */
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2); /* Fondo blanco semitransparente al pasar mouse */
  color: white;
}

/* CLASE AUTOMÁTICA DE VUE: Se activa cuando estás en esa página */
.router-link-active {
    background-color: white;
    color: #e67e22 !important; /* Texto naranja */
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* 4. BOTONES LOGIN/LOGOUT */
.auth-buttons {
    margin-left: 15px;
    padding-left: 15px;
    border-left: 1px solid rgba(255,255,255,0.3); /* Línea separadora */
}

.btn-login {
  background-color: #2c3e50; /* Gris oscuro */
  color: white; 
  padding: 8px 18px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s;
}
.btn-login:hover { background-color: #34495e; }

.btn-logout {
  background-color: transparent; 
  color: white;
  border: 1px solid rgba(255,255,255,0.5);
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}
.btn-logout:hover {
  background-color: #c0392b; /* Rojo al pasar el mouse */
  border-color: #c0392b;
}

/* 5. CONTENIDO PRINCIPAL */
main {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 20px;
}

/* RESPONSIVE (Celulares) */
@media (max-width: 768px) {
    .marca-texto { display: none; } /* Ocultar nombre en celular */
    .nav-link { font-size: 0.9rem; padding: 5px 8px; }
    .btn-logout { padding: 5px 10px; font-size: 0.9rem; }
}
</style>