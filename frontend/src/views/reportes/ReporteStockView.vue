<script setup lang="ts">
import ReporteGenericView from './ReporteGenericView.vue'
import { reportesService } from '@/services/reportes.service'
</script>
<template><ReporteGenericView tipo="stock" title="Reporte de stock" :loader="reportesService.getStock" /></template>
