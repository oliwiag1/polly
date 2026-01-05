<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()
const surveyId = computed(() => route.params.id as string)
</script>

<template>
  <div class="survey-success-view">
    <div class="success-card">
      <div class="success-icon">🎉</div>
      <h1>Dziękujemy!</h1>
      <p class="success-message">Twoja odpowiedź została pomyślnie zapisana.</p>
      
      <div class="success-illustration">
        <div class="confetti confetti-1">🎊</div>
        <div class="confetti confetti-2">✨</div>
        <div class="confetti confetti-3">🎉</div>
        <div class="checkmark">✓</div>
      </div>

      <div class="success-actions">
        <RouterLink :to="`/surveys/${surveyId}`" class="btn btn-secondary">
          📝 Wypełnij ponownie
        </RouterLink>
        <RouterLink to="/surveys" class="btn btn-primary">
          📋 Przeglądaj ankiety
        </RouterLink>
      </div>

      <RouterLink to="/" class="home-link">
        ← Wróć do strony głównej
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.survey-success-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.success-card {
  background: white;
  border-radius: 24px;
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.success-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

h1 {
  margin: 0;
  color: #333;
  font-size: 2.5rem;
}

.success-message {
  color: #666;
  font-size: 1.2rem;
  margin: 1rem 0 2rem;
}

.success-illustration {
  position: relative;
  height: 120px;
  margin: 2rem 0;
}

.checkmark {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
  margin: 0 auto;
  box-shadow: 0 10px 30px rgba(76, 175, 80, 0.4);
  animation: scaleIn 0.5s ease 0.3s both;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.confetti {
  position: absolute;
  font-size: 2rem;
  animation: float 3s ease-in-out infinite;
}

.confetti-1 {
  left: 20%;
  top: 0;
  animation-delay: 0s;
}

.confetti-2 {
  right: 20%;
  top: 10%;
  animation-delay: 0.5s;
}

.confetti-3 {
  left: 50%;
  top: -10%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(10deg);
  }
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.btn {
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.home-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.home-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .success-card {
    padding: 2rem;
  }

  h1 {
    font-size: 2rem;
  }

  .success-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
