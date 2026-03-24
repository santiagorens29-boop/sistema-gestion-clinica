<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';

// DATOS
const medicos = ref([]);
const pacientes = ref([]);
const turnosDelDia = ref([]);
const ausenciasMedico = ref([]); 

// --- FECHAS Y FILTROS ---

// Función segura para obtener la fecha local (Argentina) en formato YYYY-MM-DD
// Esto evita errores si usas el sistema después de las 21hs
const getFechaHoy = () => {
    const hoy = new Date();
    const year = hoy.getFullYear();
    const month = String(hoy.getMonth() + 1).padStart(2, '0');
    const day = String(hoy.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const fechaHoy = getFechaHoy(); // Guardamos HOY en una constante
const fechaSeleccionada = ref(fechaHoy); // Iniciamos el calendario en HOY
const medicoSeleccionado = ref('');

// ESTADO DE LA UI
const horaTurnoPendiente = ref(null);
const medicoEstaAusente = ref(false); 
const motivoAusencia = ref(''); 

// 1. CARGAR DATOS INICIALES
onMounted(async () => {
    cargarMedicos();
    cargarPacientes();
});

const cargarMedicos = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const response = await axios.get('http://10.199.184.143:8000/api/medicos/', {
            headers: { Authorization: `Token ${token}` }
        });
        medicos.value = response.data.map(u => ({
            id: u.id,
            nombre: `Dr. ${u.last_name} ${u.first_name}`
        }));
    } catch (error) {
        console.error("Error cargando médicos", error);
    }
};

const cargarPacientes = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const response = await axios.get('http://10.199.184.143:8000/api/pacientes/', {
            headers: { Authorization: `Token ${token}` }
        });
        pacientes.value = response.data;
    } catch (error) {
       console.error("Error cargando pacientes", error);
    }
};

// 2. BUSCAR DATOS
const buscarDatosAgenda = async () => {
    if (!medicoSeleccionado.value) return;
    buscarTurnos();
    verificarAusencias();
};

const buscarTurnos = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const url = `http://10.199.184.143:8000/api/turnos/?medico=${medicoSeleccionado.value}&fecha=${fechaSeleccionada.value}`;
        const response = await axios.get(url, { headers: { Authorization: `Token ${token}` } });
        turnosDelDia.value = response.data.sort((a, b) => a.hora.localeCompare(b.hora));
    } catch (error) {
       console.error(error);
    }
};

const verificarAusencias = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const response = await axios.get(`http://10.199.184.143:8000/api/ausencias/?medico=${medicoSeleccionado.value}`, {
            headers: { Authorization: `Token ${token}` }
        });
        
        ausenciasMedico.value = response.data;
        const fechaActualTexto = fechaSeleccionada.value; 

        const ausenciaEncontrada = ausenciasMedico.value.find(a => {
            return fechaActualTexto >= a.fecha_inicio && fechaActualTexto <= a.fecha_fin;
        });

        if (ausenciaEncontrada) {
            medicoEstaAusente.value = true;
            motivoAusencia.value = ausenciaEncontrada.motivo || 'No disponible';
        } else {
            medicoEstaAusente.value = false;
            motivoAusencia.value = '';
        }
    } catch (error) {
        console.error("Error verificando ausencias", error);
    }
};

// CREAR BLOQUEO
const abrirModalBloqueo = async () => {
    if (!medicoSeleccionado.value) return Swal.fire('Error', 'Selecciona un médico primero.', 'warning');

    const { value: formValues } = await Swal.fire({
        title: '⛔ Bloquear Agenda',
        html: `
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Desde:</label>
            <input id="swal-inicio" type="date" class="swal2-input">
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Hasta:</label>
            <input id="swal-fin" type="date" class="swal2-input">
            <label style="display:block; text-align:left; font-size:0.9em; margin-top:10px;">Motivo:</label>
            <input id="swal-motivo" type="text" class="swal2-input" placeholder="Ej: Vacaciones">
        `,
        focusConfirm: false, showCancelButton: true, confirmButtonText: 'Bloquear Días', confirmButtonColor: '#34495e',
        preConfirm: () => [
            document.getElementById('swal-inicio').value,
            document.getElementById('swal-fin').value,
            document.getElementById('swal-motivo').value
        ]
    });

    if (formValues) {
        const [inicio, fin, motivo] = formValues;
        if (!inicio || !fin) return Swal.fire('Error', 'Fechas incompletas.', 'error');
        if (inicio > fin) return Swal.fire('Error', 'Fecha inicio mayor a fin.', 'error');

        const token = localStorage.getItem('userToken');
        try {
            await axios.post('http://10.199.184.143:8000/api/ausencias/', {
                medico: medicoSeleccionado.value, fecha_inicio: inicio, fecha_fin: fin, motivo: motivo
            }, { headers: { Authorization: `Token ${token}` } });
            Swal.fire('Bloqueado', 'Días bloqueados.', 'success');
            buscarDatosAgenda(); 
        } catch (error) { Swal.fire('Error', 'No se pudo guardar.', 'error'); }
    }
};

// --- LOGICA DE TURNOS ---

const crearPacienteRapido = async () => {
    const { value: formValues } = await Swal.fire({
        title: 'Crear Paciente Express',
        html:
            '<input id="swal-nombre" class="swal2-input" placeholder="Nombre">' +
            '<input id="swal-apellido" class="swal2-input" placeholder="Apellido">' +
            '<input id="swal-dni" class="swal2-input" placeholder="DNI">',
        focusConfirm: false, showCancelButton: true, confirmButtonText: '💾 Guardar y Agendar', confirmButtonColor: '#e67e22', cancelButtonText: 'Volver',
        preConfirm: () => [
            document.getElementById('swal-nombre').value,
            document.getElementById('swal-apellido').value,
            document.getElementById('swal-dni').value
        ]
    });

    if (formValues) {
        const [nombre, apellido, dni] = formValues;
        if (!nombre || !apellido || !dni) { Swal.fire('Atención', 'Faltan datos.', 'warning'); setTimeout(() => crearPacienteRapido(), 500); return; }

        const token = localStorage.getItem('userToken');
        try {
            await axios.post('http://10.199.184.143:8000/api/pacientes/', { nombre, apellido, dni }, { headers: { Authorization: `Token ${token}` } });
            await cargarPacientes(); 
            const pacienteConfirmado = pacientes.value.find(p => p.dni == dni);
            if (pacienteConfirmado && pacienteConfirmado.id) {
                if (!horaTurnoPendiente.value) throw new Error("Se perdió la hora.");
                await guardarTurno(pacienteConfirmado.id, horaTurnoPendiente.value, true);
            } else { throw new Error("Error ID."); }
        } catch (error) {
            let mensaje = 'Error al crear.';
            if (error.response && error.response.data && error.response.data.dni) mensaje = 'DNI ya existe.';
            Swal.fire('Error', mensaje, 'error'); setTimeout(() => crearPacienteRapido(), 500); 
        }
    } else { pedirPacienteParaTurno(); }
};

const pedirPacienteParaTurno = async () => {
    const hora = horaTurnoPendiente.value;
    if (!hora) return;
    const opcionesPacientes = pacientes.value.map(p => `<option value="${p.nombre} ${p.apellido} (DNI: ${p.dni})">`).join('');

    const { value: nombreSeleccionado, isDismissed } = await Swal.fire({
        title: `Turno a las ${hora} hs`,
        text: 'Busca el paciente o crea uno nuevo:',
        html: `
            <input list="lista-pacientes" id="swal-input-paciente" class="swal2-input" placeholder="Escribe nombre o DNI...">
            <datalist id="lista-pacientes">${opcionesPacientes}</datalist>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ccc;">
                <small style="color: #7f8c8d; display: block; margin-bottom: 5px;">¿No está en la lista?</small>
                <button type="button" id="btn-crear-nuevo" class="swal2-confirm swal2-styled" style="background-color: #34495e; margin: 0; width: 100%;">👤 + Crear y Agendar</button>
            </div>
        `,
        focusConfirm: false, showCancelButton: true, confirmButtonText: '✅ Agendar', confirmButtonColor: '#e67e22', cancelButtonText: 'Cancelar',
        didOpen: () => {
            const btn = Swal.getPopup().querySelector('#btn-crear-nuevo');
            btn.addEventListener('click', () => { Swal.close(); crearPacienteRapido(); });
        },
        preConfirm: () => document.getElementById('swal-input-paciente').value
    });

    if (nombreSeleccionado) {
        const pacienteEncontrado = pacientes.value.find(p => `${p.nombre} ${p.apellido} (DNI: ${p.dni})` === nombreSeleccionado);
        if (pacienteEncontrado) guardarTurno(pacienteEncontrado.id, hora, false);
        else Swal.fire('Error', 'Paciente no válido.', 'warning').then(() => pedirPacienteParaTurno());
    }
};

const abrirModalNuevoTurno = async () => {
    if (!medicoSeleccionado.value) return Swal.fire('Atención', 'Selecciona un médico primero', 'warning');
    if (medicoEstaAusente.value) return Swal.fire('Médico No Disponible', `Motivo: ${motivoAusencia.value}`, 'error');
    
    // VALIDACIÓN NUEVA: No dejar dar turnos en el pasado
    if (fechaSeleccionada.value < fechaHoy) {
        return Swal.fire('Fecha Pasada', 'No puedes dar turnos para días anteriores a hoy.', 'warning');
    }

    const { value: horaManual } = await Swal.fire({
        title: 'Nuevo Turno', text: 'Ingrese el horario:', input: 'time', inputAttributes: { step: 300 },
        confirmButtonText: 'Siguiente ➡', confirmButtonColor: '#e67e22', showCancelButton: true
    });
    if (horaManual) {
        horaTurnoPendiente.value = horaManual;
        pedirPacienteParaTurno();
    }
};

const guardarTurno = async (pacienteId, hora, esNuevo = false) => {
    const token = localStorage.getItem('userToken');
    if (!pacienteId) return Swal.fire('Error', 'Falta ID Paciente', 'error');
    try {
        await axios.post('http://10.199.184.143:8000/api/turnos/', {
            medico: medicoSeleccionado.value, paciente: pacienteId, fecha: fechaSeleccionada.value, hora: hora, estado: 'programado'
        }, { headers: { Authorization: `Token ${token}` } });
        
        horaTurnoPendiente.value = null;
        const mensaje = esNuevo ? `¡Paciente Creado y Turno Agendado!` : `Turno agendado correctamente`;
        Swal.fire({ title: '¡Éxito!', text: mensaje, icon: 'success', timer: 2000, showConfirmButton: false });
        buscarTurnos(); 
    } catch (error) {
       console.error(error);
       let msgError = 'No se pudo guardar.';
       if (error.response && error.response.data) {
            const data = error.response.data;
            if (data.non_field_errors) msgError = "Horario ocupado o conflicto.";
            else if (Array.isArray(data)) msgError = data[0];
            else msgError = JSON.stringify(data);
       }
       Swal.fire('Error', msgError, 'error');
    }
};

const cancelarTurno = async (turno) => {
    const result = await Swal.fire({ title: '¿Borrar turno?', icon: 'warning', showCancelButton: true, confirmButtonColor: '#d33', confirmButtonText: 'Sí, borrar' });
    if (result.isConfirmed) {
        const token = localStorage.getItem('userToken');
        try {
            await axios.delete(`http://10.199.184.143:8000/api/turnos/${turno.id}/`, { headers: { Authorization: `Token ${token}` } });
            buscarTurnos(); Swal.fire('Eliminado', '', 'success');
        } catch (error) { Swal.fire('Error', 'No se pudo eliminar', 'error'); }
    }
};

const anunciarLlegada = async (turno) => {
    const token = localStorage.getItem('userToken');
    try {
        await axios.patch(`http://10.199.184.143:8000/api/turnos/${turno.id}/`, { estado: 'espera' }, { headers: { Authorization: `Token ${token}` } });
        buscarTurnos(); Swal.fire('¡En Sala de Espera!', '', 'success');
    } catch (error) { Swal.fire('Error', 'Falló la conexión', 'error'); }
};
</script>

<template>
  <div class="agenda-container">
    
    <div class="header-agenda">
        <h2>📅 Agenda de Turnos</h2>
        <p class="subtitulo">Sistema de Gestión Ágil</p>
    </div>
    
    <div class="filtros-box">
        <div class="campo">
            <label>👨‍⚕️ Médico:</label>
            <select v-model="medicoSeleccionado" @change="buscarDatosAgenda" class="input-filtro">
                <option disabled value="">-- Seleccionar --</option>
                <option v-for="m in medicos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
        </div>
        <div class="campo">
            <label>📆 Fecha:</label>
            <input type="date" v-model="fechaSeleccionada" @change="buscarDatosAgenda" class="input-filtro">
        </div>
    </div>

    <hr class="divider">

    <div v-if="medicoEstaAusente" class="alerta-bloqueo">
        <h3>⛔ MÉDICO NO DISPONIBLE</h3>
        <p>Motivo: <strong>{{ motivoAusencia }}</strong></p>
        <small>Seleccione otra fecha.</small>
    </div>

    <div v-if="medicoSeleccionado">
        
        <div class="acciones-agenda">
            <button v-if="!medicoEstaAusente" class="btn-orange-full" @click="abrirModalNuevoTurno">
                ➕ NUEVO TURNO
            </button>
            <button class="btn-gris-block" @click="abrirModalBloqueo">
                ⛔ Bloquear Días
            </button>
        </div>

        <div v-if="turnosDelDia.length > 0" class="lista-turnos">
            <h3 class="titulo-dia">Turnos del día:</h3>
            
            <div v-for="turno in turnosDelDia" :key="turno.id" class="turno-card" :class="turno.estado">
                
                <div class="info-turno">
                    <div class="hora-badge">
                        {{ turno.hora.substring(0,5) }}
                    </div>
                    <div class="datos-paciente">
                        <strong class="nombre-paciente">{{ turno.nombre_paciente }} {{ turno.apellido_paciente }}</strong>
                        <span v-if="turno.estado === 'espera'" class="estado-tag espera">🔔 ESPERA</span>
                        <span v-else class="estado-tag programado">📅 Programado</span>
                    </div>
                </div>

                <div class="botonera-turno">
                    <button v-if="turno.estado === 'programado' && fechaSeleccionada === fechaHoy" 
                            @click="anunciarLlegada(turno)" 
                            class="btn-icon check" 
                            title="Llegó">
                        ✅
                    </button>
                    
                    <button @click="cancelarTurno(turno)" class="btn-icon trash" title="Eliminar">🗑️</button>
                </div>

            </div>
        </div>

        <div v-else class="empty-state">
            <div class="icon-empty">📭</div>
            <p v-if="!medicoEstaAusente">Agenda libre.</p>
            <p v-else>No se pueden dar turnos.</p>
        </div>

    </div>
    
    <div v-else class="mensaje-inicial">
        <p>👈 Selecciona un médico para comenzar.</p>
    </div>
  </div>
</template>

<style scoped>
/* ESTILOS IGUALES AL ANTERIOR, SIN CAMBIOS VISUALES GRANDES */
.agenda-container { max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; min-height: 100vh;}
.header-agenda { text-align: center; margin-bottom: 20px; }
.header-agenda h2 { color: #2c3e50; font-weight: 800; margin: 0; }
.subtitulo { color: #7f8c8d; font-size: 0.9rem; }

.filtros-box { display: flex; gap: 15px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 3px solid #e67e22; }
.campo { flex: 1; display: flex; flex-direction: column; }
.campo label { font-weight: bold; font-size: 0.85rem; color: #555; margin-bottom: 3px;}
.input-filtro { padding: 8px; border: 1px solid #ddd; border-radius: 5px; font-size: 1rem; }

.divider { border: 0; border-top: 1px solid #e0e0e0; margin: 20px 0; }

.acciones-agenda { display: flex; gap: 10px; margin-bottom: 20px; }
.btn-orange-full { flex: 2; padding: 15px; background-color: #e67e22; color: white; font-size: 1.1rem; font-weight: 800; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(230, 126, 34, 0.2); transition: transform 0.1s; letter-spacing: 1px;}
.btn-orange-full:active { transform: scale(0.98); background-color: #d35400; }
.btn-gris-block { flex: 1; padding: 15px; background-color: #34495e; color: white; font-size: 0.9rem; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
.btn-gris-block:hover { background-color: #2c3e50; }

.alerta-bloqueo { background-color: #e74c3c; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3); }
.alerta-bloqueo h3 { margin: 0 0 5px 0; font-weight: 900; letter-spacing: 1px; }

.lista-turnos { display: flex; flex-direction: column; gap: 10px; }
.titulo-dia { color: #aaa; font-size: 0.85rem; margin: 0; text-transform: uppercase; font-weight: bold;}
.turno-card { display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #bdc3c7; }
.turno-card.programado { border-left-color: #95a5a6; }
.turno-card.espera { border-left-color: #f39c12; background-color: #fffcf5; }
.info-turno { display: flex; align-items: center; gap: 15px; }
.hora-badge { background-color: #34495e; color: white; padding: 6px 10px; border-radius: 5px; font-weight: bold; font-size: 1rem; }
.nombre-paciente { font-size: 1.05rem; color: #2c3e50; display: block; }
.estado-tag { font-size: 0.75rem; font-weight: bold; padding: 2px 5px; border-radius: 3px; margin-left: 5px; vertical-align: middle;}
.estado-tag.programado { color: #666; background: #eee; }
.estado-tag.espera { color: #d35400; background: #ffe0b2; }
.botonera-turno { display: flex; gap: 8px; }
.btn-icon { border: none; padding: 8px; border-radius: 5px; cursor: pointer; font-size: 1rem; transition: background 0.2s; }
.btn-icon.check { background-color: #e8f8f5; color: #27ae60; }
.btn-icon.check:hover { background-color: #27ae60; color: white; }
.btn-icon.trash { background-color: #fdedec; color: #c0392b; }
.btn-icon.trash:hover { background-color: #c0392b; color: white; }
.empty-state { text-align: center; padding: 30px; color: #ccc; border: 2px dashed #eee; border-radius: 10px; }
.mensaje-inicial { text-align: center; padding: 40px; color: #3498db; background: #eaf2f8; border-radius: 10px; font-weight: bold; }
</style>