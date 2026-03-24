<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLogged = ref(false);
const esMedico = ref(false);
const esSecretaria = ref(false);
const esDirector = ref(false);

onMounted(() => {
  const token = localStorage.getItem('userToken');
  if (token) {
    isLogged.value = true;
    esMedico.value = (localStorage.getItem('esMedico') === 'true');
    esSecretaria.value = (localStorage.getItem('esSecretaria') === 'true');
    esDirector.value = (localStorage.getItem('esDirector') === 'true');
  }
});
</script>

<template>
  <div class="home-container">
    
    <div v-if="!isLogged" class="welcome-box">
        <h1 class="titulo-grande">Bienvenido a <span class="text-orange">CAMI</span></h1>
        <p class="subtitulo">Sistema Integral de Gestión Médica</p>
        <p class="texto-intro">Por favor, inicie sesión para acceder a su agenda y pacientes.</p>
        
        <button @click="$router.push('/login')" class="btn-inicio">
            🔑 Iniciar Sesión
        </button>
    </div>

    <div v-else class="dashboard">
        <div class="header-dashboard">
            <h2 v-if="esDirector">👋 Hola, Director</h2>
            <h2 v-else-if="esMedico">👋 Hola, Doctor/a</h2>
            <h2 v-else-if="esSecretaria">👋 Hola, Secretaria</h2>
            <h2 v-else>👋 Bienvenido al Sistema</h2>
            <p>Panel de Acceso Rápido</p>
        </div>

        <div class="grid-acciones">
            
            <div class="card-accion" @click="$router.push('/pacientes')">
                <div class="icon">👥</div>
                <h3>Pacientes</h3>
                <p>Buscar, crear o editar fichas médicas.</p>
            </div>

            <div v-if="esDirector" class="card-accion" @click="$router.push('/agenda')">
                <div class="icon">🏥</div>
                <h3>Turnos del día de hoy</h3>
                <p>Ver mis consultas y supervisar agenda general.</p>
            </div>

            <div v-if="esSecretaria && !esDirector" class="card-accion" @click="$router.push('/agenda')">
                <div class="icon">📅</div>
                <h3>Gestor de Turnos</h3>
                <p>Dar turnos y organizar la agenda.</p>
            </div>

            <div v-if="esMedico && !esDirector" class="card-accion" @click="$router.push('/tablero')">
                <div class="icon">🩺</div>
                <h3>Mis Consultas</h3>
                <p>Ver mis pacientes del día.</p>
            </div>

        </div>
    </div>

  </div>
</template>

<style scoped>
/* ESTILO GENERAL */
.home-container {
    padding: 40px 20px;
    background-color: #f8f9fa;
    min-height: 85vh; 
    display: flex;
    justify-content: center;
    align-items: center;
}

/* BIENVENIDA (NO LOGUEADO) */
.welcome-box {
    text-align: center;
    background: white;
    padding: 50px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    max-width: 600px;
    border-top: 5px solid #e67e22;
}

.titulo-grande { font-size: 2.5rem; color: #2c3e50; margin-bottom: 10px; }
.text-orange { color: #e67e22; }
.subtitulo { font-size: 1.2rem; color: #7f8c8d; font-weight: 300; margin-bottom: 30px; }
.texto-intro { color: #555; margin-bottom: 30px; }

.btn-inicio {
    background-color: #e67e22; color: white; padding: 15px 40px; border-radius: 30px;
    font-size: 1.1rem; font-weight: bold; border: none; cursor: pointer; transition: all 0.3s;
    box-shadow: 0 5px 15px rgba(230, 126, 34, 0.3);
}
.btn-inicio:hover { background-color: #d35400; transform: translateY(-3px); }


/* DASHBOARD (LOGUEADO) */
.dashboard {
    width: 100%;
    max-width: 1000px;
}

.header-dashboard {
    text-align: center;
    margin-bottom: 40px;
}
.header-dashboard h2 { font-size: 2rem; color: #2c3e50; margin-bottom: 5px; }
.header-dashboard p { color: #7f8c8d; font-size: 1.1rem; }

/* GRID DE TARJETAS */
.grid-acciones {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Tarjetas un poco más anchas */
    gap: 30px;
    justify-content: center;
}

.card-accion {
    background: white;
    padding: 35px 25px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.card-accion:hover {
    transform: translateY(-5px); 
    box-shadow: 0 15px 25px rgba(0,0,0,0.1);
    border-color: #e67e22; /* Borde naranja al pasar mouse */
}

.icon {
    font-size: 3.5rem;
    margin-bottom: 20px;
}

.card-accion h3 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-weight: 700;
    font-size: 1.2rem;
}

.card-accion p {
    color: #7f8c8d;
    font-size: 0.95rem;
    line-height: 1.5;
}
</style>
