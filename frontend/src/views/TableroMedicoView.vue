<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2'; // <-- IMPORTADO PARA EL BLOQUEO

const router = useRouter();
const turnos = ref([]); 
const medicoInfo = ref(null);
const esDirector = ref(false); 

// Variable del calendario (empieza hoy)
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10));

onMounted(async () => {
    await identificarMedico();

    if (medicoInfo.value) {
        cargarTurnos();
        // Auto-refresco cada 30 segundos
        setInterval(cargarTurnos, 30000);
    }
});

const identificarMedico = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const response = await axios.get('http://10.199.184.143:8000/api/auth/me/', {
            headers: { Authorization: `Token ${token}` }
        });
        medicoInfo.value = response.data;
        esDirector.value = response.data.es_director; 
    } catch (error) {
        console.error("Error identificando usuario", error);
        router.push('/login');
    }
};

const cargarTurnos = async () => {
    if (!medicoInfo.value) return;

    const token = localStorage.getItem('userToken');
    try {
        let url = '';
        if (esDirector.value) {
            url = `http://10.199.184.143:8000/api/turnos/?fecha=${fechaSeleccionada.value}`;
        } else {
            const medicoId = medicoInfo.value.id; 
            url = `http://10.199.184.143:8000/api/turnos/?medico=${medicoId}&fecha=${fechaSeleccionada.value}`;
        }
        
        const response = await axios.get(url, {
            headers: { Authorization: `Token ${token}` }
        });
        turnos.value = response.data;
    } catch (error) {
        console.error("Error cargando tablero", error);
    }
};

const atenderPaciente = (pacienteId) => {
    router.push(`/pacientes/${pacienteId}/historia`);
};

// 👇 NUEVA FUNCIÓN: BLOQUEAR MI AGENDA 👇
const bloquearMiAgenda = async () => {
    const { value: formValues } = await Swal.fire({
        title: '⛔ Bloquear Mis Días',
        html: `
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Desde:</label>
            <input id="swal-inicio" type="date" class="swal2-input">
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Hasta:</label>
            <input id="swal-fin" type="date" class="swal2-input">
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Motivo:</label>
            <input id="swal-motivo" type="text" class="swal2-input" placeholder="Ej: Vacaciones, Trámites">
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Confirmar Bloqueo',
        confirmButtonColor: '#34495e',
        cancelButtonText: 'Volver',
        preConfirm: () => [
            document.getElementById('swal-inicio').value,
            document.getElementById('swal-fin').value,
            document.getElementById('swal-motivo').value
        ]
    });

    if (formValues) {
        const [inicio, fin, motivo] = formValues;
        if (!inicio || !fin) return Swal.fire('Error', 'Debes completar las fechas.', 'error');
        if (inicio > fin) return Swal.fire('Error', 'La fecha de inicio no puede ser mayor a la de fin.', 'error');

        const token = localStorage.getItem('userToken');
        try {
            await axios.post('http://10.199.184.143:8000/api/ausencias/', {
                medico: medicoInfo.value.id, 
                fecha_inicio: inicio,
                fecha_fin: fin,
                motivo: motivo
            }, { headers: { Authorization: `Token ${token}` } });

            Swal.fire('Bloqueado', 'Has bloqueado tu agenda correctamente.', 'success');
            cargarTurnos(); // Refrescamos para ver si hay cambios
        } catch (error) {
            Swal.fire('Error', 'No se pudo guardar el bloqueo.', 'error');
        }
    }
};
</script>

<template>
  <div class="tablero-container">
    
    <div class="header-tablero">
        <div>
            <h2 class="titulo-principal">
                {{ esDirector ? '👨‍💼 Tablero General (Director)' : '👨‍⚕️ Mis Consultas' }}
            </h2>
            <div class="subtitulo">
                Usuario: <strong>{{ medicoInfo?.nombre_completo }}</strong>
            </div>
        </div>
        
        <div class="controles">
            <button @click="bloquearMiAgenda" class="btn-bloquear-propi" title="Bloquear mi agenda">
                ⛔ Bloquear Agenda
            </button>

            <div class="grupo-fecha">
                <label>Fecha:</label>
                <input 
                    type="date" 
                    v-model="fechaSeleccionada" 
                    @change="cargarTurnos"
                    class="input-fecha"
                />
            </div>
            <button @click="cargarTurnos" class="btn-refresh" title="Actualizar lista">
                🔄
            </button>
        </div>
    </div>

    <div v-if="turnos.length > 0" class="lista-turnos">
        
        <div 
            v-for="turno in turnos" 
            :key="turno.id" 
            class="tarjeta-turno"
            :class="turno.estado" 
        >
            <div class="col-hora">
                <span class="hora-texto">{{ turno.hora.substring(0,5) }}</span>
                <span class="hs-label">hs</span>
            </div>
            
            <div class="col-info">
                <h3 class="nombre-paciente">{{ turno.nombre_paciente }} {{ turno.apellido_paciente }}</h3>
                
                <div v-if="esDirector" class="dato-medico">
                    <span class="icon-medico">👨‍⚕️</span> Dr/a. {{ turno.nombre_medico }} {{ turno.apellido_medico }}
                </div>

                <div class="etiquetas">
                    <span v-if="turno.estado === 'programado'" class="badge gris">📅 Programado</span>
                    <span v-if="turno.estado === 'espera'" class="badge naranja">🔔 EN SALA DE ESPERA</span>
                    <span v-if="turno.estado === 'atendido'" class="badge verde">✅ Atendido</span>
                </div>
            </div>

            <div class="col-acciones">
                <button @click="atenderPaciente(turno.paciente)" class="btn-atender">
                    📂 Abrir Historia
                </button>
            </div>
        </div>
    </div>

    <div v-else class="vacio">
        <div class="icon-vacio">🎉</div>
        <p>No hay pacientes programados para el <strong>{{ fechaSeleccionada }}</strong>.</p>
    </div>
  </div> 
</template>

<style scoped>
/* (Se mantienen todos tus estilos originales) */
.tablero-container { max-width: 900px; margin: 0 auto; padding: 30px; background-color: #f8f9fa; min-height: 100vh;}
.header-tablero { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #e0e0e0; }
.titulo-principal { color: #2c3e50; margin: 0 0 5px 0; font-weight: 800; }
.subtitulo { color: #7f8c8d; font-size: 0.95rem; }
.controles { display: flex; align-items: flex-end; gap: 10px; }
.grupo-fecha { display: flex; flex-direction: column; }
.grupo-fecha label { font-size: 0.8rem; font-weight: bold; color: #7f8c8d; margin-bottom: 2px; }
.input-fecha { padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; color: #2c3e50; outline: none; }
.input-fecha:focus { border-color: #e67e22; }
.btn-refresh { background: #34495e; color: white; border: none; padding: 9px 15px; border-radius: 6px; cursor: pointer; font-size: 1.2rem; transition: background 0.2s; }
.btn-refresh:hover { background-color: #2c3e50; }

/* 👇 ESTILO DEL NUEVO BOTÓN 👇 */
.btn-bloquear-propi {
    background-color: #fdfdfd; color: #c0392b; border: 1px solid #c0392b; padding: 8px 12px;
    border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.85rem; transition: all 0.2s;
    margin-right: 10px;
}
.btn-bloquear-propi:hover { background-color: #c0392b; color: white; }

/* (El resto de tus estilos permanecen igual...) */
.lista-turnos { display: flex; flex-direction: column; gap: 15px; }
.tarjeta-turno { background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; display: flex; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s; border-left: 6px solid #bdc3c7; }
.tarjeta-turno.programado { border-left-color: #95a5a6; opacity: 0.9; }
.tarjeta-turno.atendido { border-left-color: #27ae60; background-color: #f6fff9; opacity: 0.7; }
.tarjeta-turno.espera { border-left-color: #e67e22; background-color: #fff8f3; transform: scale(1.02); box-shadow: 0 5px 15px rgba(230, 126, 34, 0.15); z-index: 10; }
.col-hora { text-align: center; margin-right: 25px; min-width: 70px; }
.hora-texto { font-size: 1.6rem; font-weight: 800; color: #2c3e50; display: block; line-height: 1;}
.hs-label { font-size: 0.8rem; color: #7f8c8d; font-weight: bold; }
.col-info { flex-grow: 1; }
.nombre-paciente { margin: 0 0 5px 0; color: #2c3e50; font-size: 1.2rem; }
.dato-medico { font-size: 0.9rem; color: #555; background: #eee; display: inline-block; padding: 2px 8px; border-radius: 4px; margin-bottom: 5px; }
.icon-medico { margin-right: 4px; }
.etiquetas { margin-top: 5px; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: white;}
.badge.gris { background-color: #95a5a6; }
.badge.verde { background-color: #27ae60; }
.badge.naranja { background-color: #e67e22; animation: parpadeo 2s infinite; }
.btn-atender { background-color: #2c3e50; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
.btn-atender:hover { background-color: #e67e22; }
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
.vacio { text-align: center; margin-top: 60px; color: #7f8c8d; }
.icon-vacio { font-size: 3rem; margin-bottom: 10px; }
@media (max-width: 600px) {
    .tarjeta-turno { flex-direction: column; align-items: flex-start; gap: 15px; }
    .col-hora { text-align: left; display: flex; align-items: baseline; gap: 5px; }
    .col-acciones { width: 100%; }
    .btn-atender { width: 100%; }
}
</style>