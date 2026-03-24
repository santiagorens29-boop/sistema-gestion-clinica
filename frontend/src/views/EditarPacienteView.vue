<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';

const route = useRoute();
const router = useRouter();
const pacienteId = route.params.id;

// Variables
const nombre = ref('');
const apellido = ref('');
const dni = ref('');
const obra_social = ref('');
const numero_afiliado = ref('');
const medico_cabecera = ref('');
const fecha_nacimiento = ref('');
const sexo = ref('');
const telefono = ref('');
const email = ref('');

// CARGAR DATOS
const cargarDatos = async () => {
  const token = localStorage.getItem('userToken');
  try {
    const response = await axios.get(`http://10.199.184.143:8000/api/pacientes/${pacienteId}/`, {
      headers: { Authorization: `Token ${token}` }
    });
    const p = response.data;
    nombre.value = p.nombre;
    apellido.value = p.apellido;
    dni.value = p.dni;
    obra_social.value = p.obra_social;
    numero_afiliado.value = p.numero_afiliado; 
    medico_cabecera.value = p.medico_cabecera; 
    fecha_nacimiento.value = p.fecha_nacimiento;
    sexo.value = p.sexo;
    telefono.value = p.telefono;
    email.value = p.email;
  } catch (error) {
    Swal.fire({
        title: 'Error',
        text: 'No se pudo cargar el paciente',
        icon: 'error',
        confirmButtonColor: '#e67e22'
    });
    router.push('/pacientes');
  }
};

onMounted(() => { cargarDatos(); });

// ACTUALIZAR DATOS
const actualizarPaciente = async () => {
  if (!nombre.value || !apellido.value || !dni.value) {
    Swal.fire({
        title: 'Atención',
        text: 'Faltan datos obligatorios (Nombre, Apellido, DNI)',
        icon: 'warning',
        confirmButtonColor: '#e67e22'
    });
    return;
  }

  const token = localStorage.getItem('userToken');
  try {
    await axios.put(`http://10.199.184.143:8000/api/pacientes/${pacienteId}/`, {
      nombre: nombre.value,
      apellido: apellido.value,
      dni: dni.value,
      obra_social: obra_social.value,
      numero_afiliado: numero_afiliado.value, 
      medico_cabecera: medico_cabecera.value, 
      fecha_nacimiento: fecha_nacimiento.value || null, 
      sexo: sexo.value || null,
      telefono: telefono.value,
      email: email.value
    }, {
      headers: { Authorization: `Token ${token}` }
    });

    Swal.fire({
        title: '¡Actualizado!',
        text: 'Datos guardados correctamente',
        icon: 'success',
        confirmButtonColor: '#e67e22'
    });

    setTimeout(() => router.push('/pacientes'), 1500);

  } catch (error) {
    let msj = "Error al actualizar.";
    if (error.response && error.response.data.dni) msj = "Ese DNI ya existe.";
    Swal.fire({
        title: 'Error',
        text: msj,
        icon: 'error',
        confirmButtonColor: '#e67e22'
    });
  }
};
</script>

<template>
  <div class="main-container">
    
    <div class="header-section">
        <h2 class="titulo-pagina">✏️ Editar Paciente</h2>
        <p class="subtitulo">Modifique los datos necesarios de la ficha.</p>
    </div>

    <div class="card-formulario">
      
      <div class="fila">
        <div class="campo">
            <label>Nombre *</label>
            <input v-model="nombre" type="text">
        </div>
        <div class="campo">
            <label>Apellido *</label>
            <input v-model="apellido" type="text">
        </div>
      </div>

      <div class="fila">
        <div class="campo">
            <label>DNI *</label>
            <input v-model="dni" type="text">
        </div>
        <div class="campo">
            <label>Sexo</label>
            <select v-model="sexo">
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
                <option value="X">Otro</option>
            </select>
        </div>
      </div>

      <div class="fila">
        <div class="campo">
            <label>Obra Social</label>
            <input v-model="obra_social" type="text">
        </div>
        <div class="campo">
            <label>Nro. Afiliado</label>
            <input v-model="numero_afiliado" type="text">
        </div>
      </div>

      <div class="fila">
        <div class="campo">
            <label>Fecha Nacimiento</label>
            <input v-model="fecha_nacimiento" type="date">
        </div>
        <div class="campo">
            <label>Médico Cabecera</label>
            <input v-model="medico_cabecera" type="text">
        </div>
      </div>

      <div class="fila">
        <div class="campo">
            <label>Teléfono</label>
            <input v-model="telefono" type="text">
        </div>
        <div class="campo">
            <label>Email</label>
            <input v-model="email" type="text">
        </div>
      </div>

      <div class="acciones">
        <button @click="$router.push('/pacientes')" class="btn-cancelar">Cancelar</button>
        <button @click="actualizarPaciente" class="btn-guardar">💾 Guardar Cambios</button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ESTILOS UNIFICADOS CON "NUEVO PACIENTE" */
.main-container {
    padding: 30px;
    background-color: #f8f9fa; /* Fondo gris suave */
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.header-section {
    text-align: center;
    margin-bottom: 25px;
}

.titulo-pagina {
    color: #2c3e50;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitulo { color: #7f8c8d; font-size: 0.95rem; }

/* TARJETA */
.card-formulario {
    background-color: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    width: 100%;
    max-width: 700px;
    border-top: 5px solid #e67e22; /* Detalle naranja */
}

/* INPUTS */
.fila { display: flex; gap: 20px; margin-bottom: 20px; }
.campo { flex: 1; }

.campo label {
    display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9em; color: #34495e;
}

.campo input, .campo select {
    width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px;
    box-sizing: border-box; font-size: 1rem; color: #555; transition: border 0.3s, box-shadow 0.3s;
}

.campo input:focus, .campo select:focus {
    border-color: #e67e22; outline: none; box-shadow: 0 0 0 3px rgba(230, 126, 34, 0.1);
}

/* BOTONES */
.acciones {
    display: flex; justify-content: flex-end; gap: 15px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;
}

.btn-guardar {
    background-color: #e67e22; color: white; padding: 12px 25px; border: none; border-radius: 6px;
    cursor: pointer; font-weight: bold; font-size: 1rem; transition: background 0.3s;
    box-shadow: 0 2px 5px rgba(230, 126, 34, 0.2);
}
.btn-guardar:hover { background-color: #d35400; }

.btn-cancelar {
    background-color: white; color: #7f8c8d; padding: 12px 20px; border: 1px solid #bdc3c7;
    border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.3s;
}
.btn-cancelar:hover { background-color: #f1f1f1; color: #2c3e50; border-color: #95a5a6; }

@media (max-width: 600px) {
    .fila { flex-direction: column; gap: 15px; }
    .acciones { flex-direction: column-reverse; }
    .btn-guardar, .btn-cancelar { width: 100%; }
}
</style>