<template>
  <div class="object-detail-view">
    <h1>Карточка объекта</h1>
    <p>ID объекта: {{ $route.params.id }}</p>
    <p>Детальная информация об объекте, документация, дефекты и задачи будут отображены здесь.</p>
    <router-link to="/" class="btn btn-primary">Назад к панели</router-link>
  </div>
</template>

<script setup>
// Object detail view - placeholder
</script>

<style scoped>
.object-detail-view {
  padding: 2rem;
}
</style>
