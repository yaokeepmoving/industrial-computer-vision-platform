<template>
  <div class="col-12 col-sm-6">
    <q-input 
      v-model="param.name" 
      dense 
      outlined 
      label="参数名称"
      :rules="[val => !!val || '请输入参数名称']"
    />
  </div>
  <div class="col-12 col-sm-6">
    <q-select 
      v-model="param.type" 
      :options="paramTypeOptions" 
      dense 
      outlined 
      label="参数类型"
      :rules="[val => !!val || '请选择参数类型']"
      emit-value
      map-options
      options-dense
    >
      <template v-slot:option="{ itemProps, opt }">
        <q-item v-bind="itemProps">
          <q-item-section avatar>
            <q-icon :name="opt.icon" />
          </q-item-section>
          <q-item-section>
            {{ opt.label }}
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>
  <div class="col-12">
    <q-input 
      v-model="param.description" 
      dense 
      outlined 
      label="描述"
    />
  </div>
  <div class="col-grow">
    <q-input 
      v-model="param.default" 
      dense 
      outlined 
      label="默认值"
    />
  </div>
  <div class="col-auto">
    <q-checkbox v-model="param.required" label="必需参数" />
  </div>
</template>

<script setup lang="ts">
defineProps({
  param: {
    type: Object,
    required: true
  },
  paramTypeOptions: {
    type: Array,
    required: true
  }
})
</script>
