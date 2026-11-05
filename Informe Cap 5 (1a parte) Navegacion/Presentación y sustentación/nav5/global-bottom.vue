<template>
  <footer
    v-if="!['cover', 'end', 'intro'].includes($nav.currentLayout)"
    class="absolute bottom-0 left-0 right-0 flex items-center justify-between px-6 py-2 text-xs opacity-50"
  >
    <span>{{ $slidev.configs.title }}</span>
    <span>{{ $nav.currentPage }} / {{ $nav.total }}</span>
  </footer>
</template>
