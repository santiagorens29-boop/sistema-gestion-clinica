<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'vue-chartjs';

// Registramos los componentes gráficos
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

// DATOS REACTIVOS
const loading = ref(true);
const stats = ref({
    ranking_medicos: [],
    ausentismo: { presentes: 0, ausentes: 0 },
    pacientes: { nuevos_mes: 0, total: 0 }
});

// CONFIGURACIÓN DE GRÁFICOS
const chartDataRanking = ref({ labels: [], datasets: [] });
const chartDataAusentismo = ref({ labels: [], datasets: [] });

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false
};

onMounted(async () => {
    await cargarEstadisticas();
});

const cargarEstadisticas = async () => {
    const token = localStorage.getItem('userToken');
    try {
        const response = await axios.get('http://10.199.184.143:8000/api/stats/', {
            headers: { Authorization: `Token ${token}` }
        });
        
        stats.value = response.data;
        prepararGraficos();
        loading.value = false;
    } catch (error) {
        console.error("Error cargando estadísticas", error);
    }
};

const prepararGraficos = () => {
    // 1. GRAFICO BARRAS (Médicos)
    const labelsMedicos = stats.value.ranking_medicos.map(item => item.name);
    const dataMedicos = stats.value.ranking_medicos.map(item => item.value);

    chartDataRanking.value = {
        labels: labelsMedicos,
        datasets: [{
            label: 'Turnos Atendidos',
            backgroundColor: '#3498db',
            data: dataMedicos
        }]
    };

    // 2. GRAFICO TORTA (Ausentismo)
    chartDataAusentismo.value = {
        labels: ['Presentes', 'Ausentes'],
        datasets: [{
            backgroundColor: ['#2ecc71', '#e74c3c'], // Verde y Rojo
            data: [stats.value.ausentismo.presentes, stats.value.ausentismo.ausentes]
        }]
    };
};
</script>

<template>
  <div class="dashboard-container">
    <div class="header-dash">
        <h2>📊 Tablero de Control</h2>
        <p>Estadísticas en tiempo real de la clínica</p>
    </div>

    <div v-if="loading" class="loading">
        Cargando datos... ⏳
    </div>

    <div v-else class="grid-stats">
        
        <div class="card-stat numero-box">
            <h3>👥 Pacientes</h3>
            <div class="stat-row">
                <div class="stat-item">
                    <span class="numero">{{ stats.pacientes.nuevos_mes }}</span>
                    <span class="label">Nuevos este mes</span>
                </div>
                <div class="divider-v"></div>
                <div class="stat-item">
                    <span class="numero total">{{ stats.pacientes.total }}</span>
                    <span class="label">Total Histórico</span>
                </div>
            </div>
        </div>

        <div class="card-stat">
            <h3>📍 Asistencia vs. Ausencias</h3>
            <div class="chart-wrapper">
                <Doughnut :data="chartDataAusentismo" :options="chartOptions" />
            </div>
        </div>

        <div class="card-stat wide">
            <h3>🏆 Top Médicos del Mes</h3>
            <div class="chart-wrapper">
                <Bar :data="chartDataRanking" :options="chartOptions" />
            </div>
        </div>

    </div>
  </div>
</template>

<style scoped>
.dashboard-container { padding: 20px; background-color: #f4f6f8; min-height: 100vh; }
.header-dash { text-align: center; margin-bottom: 30px; }
.header-dash h2 { color: #2c3e50; margin: 0; }
.header-dash p { color: #7f8c8d; margin: 5px 0 0; }

.grid-stats { 
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
    gap: 20px; 
    max-width: 1100px; 
    margin: 0 auto; 
}

.card-stat { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.card-stat h3 { margin-top: 0; color: #34495e; font-size: 1rem; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px; margin-bottom: 15px; }

/* Estilo especial para la tarjeta ancha (Ranking) */
.wide { grid-column: span 2; }
@media (max-width: 768px) { .wide { grid-column: span 1; } }

.chart-wrapper { position: relative; height: 250px; }

/* Estilos de Números */
.stat-row { display: flex; justify-content: space-around; align-items: center; height: 100%; }
.stat-item { text-align: center; }
.numero { display: block; font-size: 3rem; font-weight: 800; color: #27ae60; }
.numero.total { color: #2c3e50; }
.label { font-size: 0.9rem; color: #95a5a6; text-transform: uppercase; font-weight: bold; }
.divider-v { width: 1px; height: 50px; background: #eee; }

.loading { text-align: center; padding: 50px; font-size: 1.2rem; color: #7f8c8d; }
</style>