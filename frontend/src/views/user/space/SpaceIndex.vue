<script setup>
import {useRoute} from 'vue-router';
const route = useRoute()
</script>

<template>
person userid: {{ route.params.user_id }}
</template>

<style scoped>

</style>