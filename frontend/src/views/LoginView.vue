<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

// Variables del formulario
const username = ref('');
const password = ref('');
const error = ref('');

const iniciarSesion = async () => {
  error.value = ''; 

  try {
    // 1. Obtener Token
    const urlLogin = 'http://10.199.184.143:8000/api-token-auth/';
    
    const response = await axios.post(urlLogin, {
      username: username.value,
      password: password.value
    });

    const token = response.data.token;
    localStorage.setItem('userToken', token);

    // 2. Consultar Rol
    const urlMe = 'http://10.199.184.143:8000/api/auth/me/';
    
    const userResponse = await axios.get(urlMe, {
        headers: { Authorization: `Token ${token}` }
    });

    const data = userResponse.data;
    
    const esMedico = data.es_medico;
    const esSecretaria = data.es_secretaria || data.es_superuser; 
    const esDirector = data.es_director; 

    // 3. Validación de Seguridad
    if (!esMedico && !esSecretaria && !esDirector) {
        error.value = "Tu usuario no tiene permisos para ingresar.";
        localStorage.removeItem('userToken'); 
        return; 
    }

    // 4. Guardar en navegador
    localStorage.setItem('esMedico', esMedico);
    localStorage.setItem('esSecretaria', esSecretaria);
    localStorage.setItem('esDirector', esDirector);

    // 5. Redirigir
    if (esMedico || esDirector) {
        router.push('/tablero');
    } else {
        router.push('/agenda');
    }

  } catch (e) {
    console.error(e);
    if (e.response && e.response.status === 400) {
        error.value = "Usuario o contraseña incorrectos.";
    } else if (e.code === "ERR_NETWORK") {
        error.value = "Error de conexión. Revisa la IP o el Wifi.";
    } else {
        error.value = "Ocurrió un error inesperado.";
    }
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      
      <img src="/logo.png" alt="Logo Clínica" class="logo-login">
      
      <h2>Bienvenido</h2>
      <p class="subtitulo">Ingresa tus credenciales para acceder al sistema.</p>
      
      <form @submit.prevent="iniciarSesion">
        <div class="form-group">
          <label>Usuario</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Nombre de usuario" 
            required 
            class="input-moderno"
          />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••" 
            required 
            class="input-moderno"
          />
        </div>

        <p v-if="error" class="error-msg">⚠️ {{ error }}</p>

        <button type="submit" class="btn-naranja">INGRESAR AL SISTEMA</button>
      </form>
    </div>
    
    <div class="footer-login">
        Sistema de Gestión Médica &copy; 2025
    </div>
  </div>
</template>

<style scoped>
/* 1. FONDO CÁLIDO (El cambio está aquí) */
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  
  /* ANTES (Gris): background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); */
  
  /* AHORA (Naranja Suave): */
  background: linear-gradient(135deg, #fff5e6 0%, #ffe0b2 100%);
}

/* 2. TARJETA FLOTANTE */
.login-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05); /* Sombra difuminada premium */
  width: 90%; 
  max-width: 400px;
  text-align: center;
  border-top: 5px solid #e67e22; /* EL TOQUE NARANJA */
}

/* LOGO */
.logo-login {
    width: 100px;
    height: auto;
    margin-bottom: 15px;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

h2 {
    color: #2c3e50;
    margin-bottom: 5px;
    font-weight: 800;
}

.subtitulo {
    color: #7f8c8d;
    font-size: 0.9rem;
    margin-bottom: 25px;
}

/* FORMULARIOS */
.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
    font-weight: 600;
    color: #34495e;
    font-size: 0.9rem;
    display: block;
    margin-bottom: 5px;
}

.input-moderno {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  background-color: #fafafa;
}

/* EFECTO FOCUS NARANJA (Igual que en los otros formularios) */
.input-moderno:focus {
    border-color: #e67e22;
    background-color: white;
    outline: none;
    box-shadow: 0 0 0 3px rgba(230, 126, 34, 0.1);
}

/* BOTÓN NARANJA */
.btn-naranja {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  background-color: #e67e22; /* TU COLOR EXACTO */
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(230, 126, 34, 0.2);
  transition: all 0.3s;
}

.btn-naranja:hover {
  background-color: #d35400;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px rgba(230, 126, 34, 0.3);
}

.error-msg {
  color: #c0392b;
  background-color: #fadbd8;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  border: 1px solid #e6b0aa;
}

.footer-login {
    margin-top: 20px;
    color: #7f8c8d;
    font-size: 0.8rem;
}
</style>