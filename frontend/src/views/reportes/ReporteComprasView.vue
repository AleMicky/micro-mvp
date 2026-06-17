<script setup lang="ts">
import ReporteGenericView from './ReporteGenericView.vue'
import { reportesService } from '@/services/reportes.service'
</script>
<template><ReporteGenericView tipo="compras" title="Reporte de compras" :loader="reportesService.getCompras" /></template>
