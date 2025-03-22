<template>
  <q-page class="cv-operations-page q-pa-md">
    <q-tabs
      v-model="activeTab"
      dense
      class="text-grey"
      active-color="primary"
      indicator-color="primary"
      align="left"
      narrow-indicator
    >
      <q-tab name="single">
        <div class="row items-center">
          <q-icon name="filter_1" class="q-mr-sm" />
          <span>单步处理</span>
        </div>
      </q-tab>
      <q-tab name="pipeline">
        <div class="row items-center">
          <q-icon name="account_tree" class="q-mr-sm" />
          <span>管道处理</span>
        </div>
      </q-tab>
    </q-tabs>

    <q-separator />

    <q-tab-panels
      v-model="activeTab"
      animated
      class="bg-transparent"
    >
      <q-tab-panel name="single" class="q-pa-none">
        <SingleOperation />
      </q-tab-panel>

      <q-tab-panel name="pipeline" class="q-pa-none">
        <!-- <PipelineOperation /> -->
      </q-tab-panel>
    </q-tab-panels>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SingleOperation from '@/components/cv/SingleOperation.vue'
// import PipelineOperation from '@/components/cv/PipelineOperation.vue'

const activeTab = ref('single')
</script>

<style lang="scss" scoped>
.cv-operations-page {
  background: var(--dark-page);
  min-height: 100vh;
}

:deep(.q-tabs) {
  background: var(--dark-card);
  border: 1px solid var(--border-color);
  border-radius: 4px 4px 0 0;
}

:deep(.q-tab-panels) {
  background: transparent;
}

:deep(.q-separator) {
  background: var(--border-color);
}
</style> 