<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2'; 

const route = useRoute();
const router = useRouter();

const pacienteId = route.params.id; 
const paciente = ref(null);
const visitas = ref([]);
const nuevaObservacion = ref('');
const archivoSeleccionado = ref(null);

// HELPER: Saber si es Imagen
const esImagen = (url) => {
  if (!url) return false;
  const extension = url.split('.').pop().toLowerCase();
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(extension);
};

// HELPER NUEVO: Saber si es PDF
const esPdf = (url) => {
  if (!url) return false;
  const extension = url.split('.').pop().toLowerCase();
  return ['pdf'].includes(extension);
};

// Función para construir la URL completa
const urlCompleta = (urlParcial) => {
    if (!urlParcial) return '';
    if (urlParcial.startsWith('http')) return urlParcial;
    return 'http://10.199.184.143:8000' + urlParcial;
};

// 1. Cargar datos
const cargarDatos = async () => {
  const token = localStorage.getItem('userToken');
  if (!token) return router.push('/login');
  const config = { headers: { Authorization: `Token ${token}` } };

  try {
    const resPaciente = await axios.get(`http://10.199.184.143:8000/api/pacientes/${pacienteId}/`, config);
    paciente.value = resPaciente.data;

    const resVisitas = await axios.get('http://10.199.184.143:8000/api/visitas/', config);
    visitas.value = resVisitas.data
        .filter(v => v.paciente == pacienteId)
        .sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

  } catch (error) {
    console.error("Error:", error);
    Swal.fire('Error', 'No se pudo cargar la historia clínica', 'error');
  }
};

const manejarArchivo = (event) => {
    archivoSeleccionado.value = event.target.files[0];
};

// 2. Guardar Visita
const guardarVisita = async () => {
  if (!nuevaObservacion.value.trim()) {
      return Swal.fire({ 
        title: 'Atención', 
        text: 'Escribe una observación.', 
        icon: 'warning', 
        confirmButtonColor: '#e67e22'
      });
  }
  const token = localStorage.getItem('userToken');
  try {
    const formData = new FormData();
    formData.append('paciente', pacienteId);
    formData.append('observacion', nuevaObservacion.value);
    if (archivoSeleccionado.value) formData.append('archivo', archivoSeleccionado.value);

    await axios.post('http://10.199.184.143:8000/api/visitas/', formData, {
      headers: { Authorization: `Token ${token}`, 'Content-Type': 'multipart/form-data' }
    });

    nuevaObservacion.value = '';
    archivoSeleccionado.value = null;
    document.getElementById('inputFile').value = ''; 
    cargarDatos(); 
    Swal.fire({ 
        title: '¡Guardado!', 
        text: 'Visita registrada con éxito.', 
        icon: 'success', 
        confirmButtonColor: '#e67e22'
    });

  } catch (error) {
    console.error(error);
    Swal.fire('Error', 'Problema al guardar', 'error');
  }
};

// 3. Guardar Nota
const guardarNota = async () => {
  const token = localStorage.getItem('userToken');
  try {
    await axios.patch(`http://10.199.184.143:8000/api/pacientes/${pacienteId}/`, {
        informacion_medica: paciente.value.informacion_medica 
    }, { headers: { Authorization: `Token ${token}` } });

    Swal.fire({ 
        title: 'Actualizado', 
        text: 'Nota guardada.', 
        icon: 'success', 
        confirmButtonColor: '#e67e22'
    });
  } catch (error) {
    console.error(error);
    Swal.fire('Error', 'No se pudo guardar la nota', 'error');
  }
};

onMounted(() => {
  cargarDatos();
});
</script>

<template>
  <div class="main-container" v-if="paciente">
    
    <div class="card-paciente">
      <div class="header-top">
          <div>
            <h1 class="titulo-historia">Historia Clínica</h1>
            <h2 class="nombre-paciente">{{ paciente.nombre }} {{ paciente.apellido }}</h2>
          </div>
          <button @click="$router.push('/pacientes')" class="btn-volver">⬅ Volver</button>
      </div>

      <div class="datos-grid">
        <div class="dato-item"><strong>DNI:</strong> {{ paciente.dni }}</div>
        <div class="dato-item"><strong>Obra Social:</strong> {{ paciente.obra_social }}</div>
        <div class="dato-item"><strong>Nro. Afiliado:</strong> {{ paciente.numero_afiliado }}</div>
      </div>
       
       <div class="alert-box"> 
         <div class="alert-header">
           <h5>⚠️ Alertas / Datos Fijos</h5>
         </div>
         <div class="alert-body">
            <textarea 
                class="form-control" 
                rows="2" 
                v-model="paciente.informacion_medica" 
                placeholder="Alergias, antecedentes..."
            ></textarea>
            <button class="btn-save-note" @click="guardarNota">💾 Guardar Nota</button>
         </div>
       </div>
    </div>

    <div class="card-nueva-visita">
      <h3 class="subtitulo-seccion">➕ Nueva Visita</h3>
      <textarea 
        class="textarea-visita"
        v-model="nuevaObservacion" 
        placeholder="Evolución, diagnóstico, tratamiento..." 
        rows="4"
      ></textarea>
      
      <div class="input-grupo">
          <label>📎 Adjuntar Estudio o Archivo (PDF, Img, Doc):</label>
          <input type="file" id="inputFile" @change="manejarArchivo" class="input-foto">
      </div>

      <button @click="guardarVisita" class="btn-primary-orange">Guardar Visita</button>
    </div>

    <div class="historial-section">
      <h3 class="subtitulo-seccion">📋 Historial</h3>
      
      <div v-if="visitas.length === 0" class="empty-msg">No hay registros aún.</div>
      
      <div v-for="visita in visitas" :key="visita.id" class="card-visita">
        <div class="card-header">
          <span class="fecha">{{ new Date(visita.fecha).toLocaleString() }}</span>
          <span class="medico">Dr/a. {{ visita.nombre_medico }} {{ visita.apellido_medico }}</span>
        </div>
        
        <div class="card-body">
          <p class="texto-observacion">{{ visita.observacion }}</p>

          <div v-if="visita.archivo" class="imagen-container">
             
             <div v-if="esImagen(visita.archivo)">
                 <div class="separador">📷 Imagen:</div>
                 <img :src="urlCompleta(visita.archivo)" class="miniatura-foto">
                 <br>
                 <a :href="urlCompleta(visita.archivo)" download target="_blank" class="btn-link-orange">⬇ Abrir imagen</a>
             </div>

             <div v-else-if="esPdf(visita.archivo)">
                 <div class="separador">📄 Documento PDF (Lectura):</div>
                 <iframe 
                    :src="urlCompleta(visita.archivo)" 
                    class="visor-pdf"
                    frameborder="0">
                 </iframe>
                 <br>
                 <a :href="urlCompleta(visita.archivo)" download target="_blank" class="btn-link-orange">⬇ Descargar PDF</a>
             </div>

             <div v-else>
                 <div class="separador">📎 Archivo adjunto:</div>
                 <div class="archivo-generico">
                     <span>Formato no previsualizable (.doc/.xls)</span>
                     <br>
                     <a :href="urlCompleta(visita.archivo)" download target="_blank" class="btn-descarga-dark">
                        ⬇ Descargar / Abrir Archivo
                     </a>
                 </div>
             </div>

          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="loading">Cargando datos...</div>
</template>

<style scoped>
/* 1. LAYOUT */
.main-container {
    padding: 30px;
    background-color: #f8f9fa; /* Gris muy suave */
    min-height: 100vh;
    max-width: 1000px;
    margin: 0 auto;
}

/* 2. CARD PACIENTE */
.card-paciente {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 25px;
    border-top: 5px solid #e67e22; /* Detalle naranja */
}

.header-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
}

.titulo-historia { font-size: 0.9rem; text-transform: uppercase; color: #7f8c8d; letter-spacing: 1px; margin: 0; }
.nombre-paciente { font-size: 1.8rem; color: #2c3e50; font-weight: 700; margin: 5px 0; }

.btn-volver {
    background-color: white;
    color: #7f8c8d;
    border: 1px solid #bdc3c7;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
}
.btn-volver:hover { border-color: #e67e22; color: #e67e22; }

.datos-grid {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
    flex-wrap: wrap;
}
.dato-item { font-size: 1.05rem; color: #34495e; }

/* 3. ALERTA */
.alert-box {
    background-color: #fff8f3; /* Naranja ultra suave */
    border: 1px solid #ffccbc; /* Borde naranja suave */
    border-radius: 8px;
    padding: 15px;
}
.alert-header h5 { margin: 0 0 10px 0; color: #d35400; font-weight: 700; }
.form-control { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; outline: none; }
.form-control:focus { border-color: #e67e22; }

.btn-save-note {
    background-color: #f39c12; 
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
    font-size: 0.9rem;
    font-weight: bold;
}
.btn-save-note:hover { background-color: #e67e22; }

/* 4. CARD NUEVA VISITA */
.card-nueva-visita {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 25px;
}
.subtitulo-seccion { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }

.textarea-visita {
    width: 100%; padding: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 1rem;
    outline: none; transition: border 0.3s;
}
.textarea-visita:focus { border-color: #e67e22; }

.input-grupo {
    margin: 15px 0; background: #fafafa; padding: 15px; border-radius: 8px; border: 1px dashed #ccc;
}
.input-grupo label { font-weight: bold; color: #34495e; display: block; margin-bottom: 5px; }

.btn-primary-orange {
    background-color: #e67e22; color: white; padding: 12px 25px; border: none; border-radius: 6px;
    cursor: pointer; font-weight: bold; font-size: 1rem; width: 100%;
    transition: background 0.3s;
}
.btn-primary-orange:hover { background-color: #d35400; }

/* 5. HISTORIAL */
.historial-section { margin-top: 30px; }

.card-visita {
    border: 1px solid #eee;
    background: white;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    overflow: hidden;
}

.card-header {
    background-color: #2c3e50; /* Gris oscuro para header de visita */
    color: white;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    font-weight: 500;
}

.card-body { padding: 20px; }
.texto-observacion { font-size: 1rem; line-height: 1.5; color: #333; white-space: pre-wrap; }

/* Adjuntos */
.imagen-container { margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; }
.separador { font-size: 0.85rem; color: #7f8c8d; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; }

.miniatura-foto { max-height: 250px; border-radius: 6px; border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.visor-pdf { width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 6px; }

.archivo-generico { background: #f1f2f6; padding: 20px; text-align: center; border-radius: 6px; border: 1px solid #ddd; }

.btn-link-orange { color: #e67e22; font-weight: bold; text-decoration: none; display: inline-block; margin-top: 5px; }
.btn-link-orange:hover { text-decoration: underline; }

.btn-descarga-dark {
    background-color: #34495e; color: white; padding: 8px 15px; border-radius: 4px;
    text-decoration: none; font-weight: bold; font-size: 0.9rem; display: inline-block; margin-top: 5px;
}
.btn-descarga-dark:hover { background-color: #2c3e50; }

.empty-msg { text-align: center; color: #95a5a6; font-style: italic; margin-top: 20px; }
.loading { text-align: center; padding: 50px; color: #7f8c8d; }
</style>