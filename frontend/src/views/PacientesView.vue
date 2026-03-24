<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; 

const router = useRouter();
const pacientes = ref([]);
const busqueda = ref('');

// 1. VARIABLES DE SEGURIDAD
const esMedico = ref(false); 
const esDirector = ref(false); 

const obtenerPacientes = async () => {
  try {
    const token = localStorage.getItem('userToken');

    if (!token) {
      alert("No tienes sesión iniciada.");
      router.push('/login'); 
      return;
    }

    // Tu IP y configuración original
    const response = await axios.get('http://10.199.184.143:8000/api/pacientes/', {
      headers: {
        Authorization: `Token ${token}` 
      },
      params: { search: busqueda.value }
    });
    
    pacientes.value = response.data;

  } catch (error) {
    console.error("Error:", error);
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      alert("Tu sesión expiró. Vamos a iniciar sesión de nuevo.");
      localStorage.removeItem('userToken'); 
      router.push('/login'); 
    }
  }
};

const verHistoria = (id) => {
  router.push(`/pacientes/${id}/historia`);
};

onMounted(() => {
  // 2. LÓGICA DE PERMISOS
  const esMedicoString = localStorage.getItem('esMedico');
  
  esMedico.value = (esMedicoString === 'true');
  esDirector.value = (localStorage.getItem('esDirector') === 'true'); 

  obtenerPacientes();
});
</script>

<template>
  <div class="pacientes-container">
    
    <div class="header-actions">
        <h2 class="titulo-pagina">Lista de Pacientes</h2>
        
        <button 
          @click="$router.push('/pacientes/nuevo')" 
          class="btn-primary-orange">
          ➕ Nuevo Paciente
        </button>
    </div>

    <div class="search-box">
      <input 
        v-model="busqueda" type="text" placeholder="Buscar por nombre o DNI..." 
        class="input-search" @keyup.enter="obtenerPacientes"
      />
      <button @click="obtenerPacientes" class="btn-search">🔍 Buscar</button>
    </div>

    <div class="table-responsive">
      <table class="custom-table">
        <thead>
          <tr>
           <th>Nombre</th>
           <th>Apellido</th>
           <th>DNI</th>
           <th>Obra Social</th>
           <th style="text-align: center;">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="paciente in pacientes" :key="paciente.id">
           <td class="fw-bold">{{ paciente.nombre }}</td>
           <td class="fw-bold">{{ paciente.apellido }}</td>
           <td>{{ paciente.dni }}</td>
           <td><span class="badge-os">{{ paciente.obra_social }}</span></td>
      
           <td style="text-align: center;">
             <div style="display: flex; justify-content: center; gap: 10px;">
            
                <button v-if="esMedico || esDirector" class="btn-icon-orange" @click="verHistoria(paciente.id)" title="Ver Historia Clínica">
                📄 Historia
               </button>
            
               <button class="btn-icon-secondary" @click="$router.push(`/pacientes/${paciente.id}/editar`)" title="Editar Datos">
                ✏️ Editar
               </button>

             </div>
           </td>

          </tr>
      </tbody>
    </table>
    </div>
    
    <p v-if="pacientes.length === 0" class="empty-msg">No se encontraron pacientes.</p>
  </div>
</template>

<style scoped>
/* 1. CONTENEDOR PRINCIPAL */
.pacientes-container { 
    padding: 30px; 
    background-color: #f8f9fa; /* Fondo gris muy suave */
    min-height: 100vh;
}

/* 2. ENCABEZADO Y BOTÓN NUEVO */
.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.titulo-pagina {
    color: #2c3e50;
    font-weight: 700;
    margin: 0;
}

.btn-primary-orange {
    background-color: #e67e22; /* NARANJA CORPORATIVO */
    color: white; 
    padding: 10px 20px; 
    border: none; 
    border-radius: 8px; /* Bordes redondeados modernos */
    cursor: pointer; 
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(230, 126, 34, 0.2);
    transition: background 0.3s;
}
.btn-primary-orange:hover {
    background-color: #d35400; 
}

/* 3. BUSCADOR */
.search-box {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
}

.input-search {
    padding: 10px; 
    width: 300px;
    border: 1px solid #ddd;
    border-radius: 6px;
    outline: none;
}
.input-search:focus {
    border-color: #e67e22; /* Borde naranja al escribir */
}

.btn-search {
    padding: 10px 20px; 
    background-color: #34495e; /* Gris oscuro para contrastar */
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

/* 4. TABLA */
.table-responsive {
    overflow-x: auto;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    background: white;
}

.custom-table {
    width: 100%; 
    border-collapse: collapse; 
    min-width: 800px;
}

.custom-table th { 
    padding: 15px; 
    background-color: #2c3e50; /* Cabecera oscura */
    color: white; 
    text-align: left;
}

.custom-table td { 
    padding: 12px 15px; 
    border-bottom: 1px solid #eee; 
    color: #555;
}

.custom-table tr:hover { 
    background-color: #fff8f3; /* Tinte naranja muy suave al pasar el mouse */
}

.fw-bold { font-weight: 600; color: #2c3e50; }

.badge-os {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.9em;
    font-weight: 600;
}

/* 5. BOTONES DE ACCIÓN */
.btn-icon-orange {
  background-color: #e67e22; /* NARANJA */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 5px;
  transition: background 0.2s;
}
.btn-icon-orange:hover {
  background-color: #d35400;
}

.btn-icon-secondary {
  background-color: white;
  color: #7f8c8d;
  border: 1px solid #bdc3c7; /* Borde sutil */
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.btn-icon-secondary:hover {
  border-color: #e67e22;
  color: #e67e22;
}

.empty-msg {
    margin-top: 20px;
    color: #7f8c8d;
    font-style: italic;
}
</style>