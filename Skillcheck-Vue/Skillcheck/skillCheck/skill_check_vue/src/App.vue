<template>
  <router-view :key="$route.fullPath" />
</template>

<script>
export default {
  name: 'App',
};
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  font-family: 'Roboto';
}
</style>
