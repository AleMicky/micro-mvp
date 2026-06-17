<script setup lang="ts">
import ReporteGenericView from './ReporteGenericView.vue'
import { reportesService } from '@/services/reportes.service'
</script>
<template><ReporteGenericView tipo="ventas" title="Reporte de ventas" :loader="reportesService.getVentas" /></template>
