<template>
  <div class="data-display" :class="[`type-${type}`, `size-${size}`]">
    <!-- 数值显示 -->
    <template v-if="type === 'value'">
      <div class="value-display">
        <div class="display-label">{{ label }}</div>
        <div class="display-value" :class="valueClass">
          {{ formattedValue }}
          <span class="unit" v-if="unit">{{ unit }}</span>
        </div>
        <div class="display-trend" v-if="showTrend">
          <q-icon 
            :name="trendIcon" 
            :class="trendClass" 
            size="16px" 
          />
          <span :class="trendClass">{{ trendValue }}%</span>
        </div>
      </div>
    </template>
    
    <!-- LED数字显示 -->
    <template v-else-if="type === 'led'">
      <div class="led-display">
        <div class="display-label">{{ label }}</div>
        <div class="led-digits">
          <div 
            v-for="(digit, index) in ledDigits" 
            :key="index" 
            class="led-digit"
          >
            {{ digit }}
          </div>
          <div class="led-unit" v-if="unit">{{ unit }}</div>
        </div>
      </div>
    </template>
    
    <!-- 状态显示 -->
    <template v-else-if="type === 'status'">
      <div class="status-display">
        <div class="display-label">{{ label }}</div>
        <div class="status-indicator">
          <span class="status-dot" :class="statusClass"></span>
          <span class="status-text" :class="statusClass">{{ statusText }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  // 显示类型: 'value', 'led', 'status'
  type: {
    type: String,
    default: 'value'
  },
  // 标签
  label: {
    type: String,
    default: '参数'
  },
  // 值
  value: {
    type: [Number, String],
    default: 0
  },
  // 单位
  unit: {
    type: String,
    default: ''
  },
  // 尺寸: 'sm', 'md', 'lg'
  size: {
    type: String,
    default: 'md'
  },
  // 趋势值 (百分比)
  trend: {
    type: Number,
    default: 0
  },
  // 是否显示趋势
  showTrend: {
    type: Boolean,
    default: false
  },
  // 状态: 'normal', 'warning', 'error', 'inactive'
  status: {
    type: String,
    default: 'normal'
  },
  // 小数位数
  decimals: {
    type: Number,
    default: 1
  },
  // 状态文本映射
  statusTextMap: {
    type: Object,
    default: () => ({
      normal: '正常',
      warning: '警告',
      error: '错误',
      inactive: '离线'
    })
  }
});

// 格式化数值
const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toFixed(props.decimals);
  }
  return props.value;
});

// LED数字显示
const ledDigits = computed(() => {
  const valueStr = formattedValue.value.toString();
  return valueStr.split('');
});

// 趋势图标
const trendIcon = computed(() => {
  if (props.trend > 0) return 'arrow_upward';
  if (props.trend < 0) return 'arrow_downward';
  return 'remove';
});

// 趋势类名
const trendClass = computed(() => {
  if (props.trend > 0) return 'trend-up';
  if (props.trend < 0) return 'trend-down';
  return 'trend-neutral';
});

// 值类名
const valueClass = computed(() => {
  if (props.type !== 'value') return '';
  
  if (props.status === 'normal') return 'value-normal';
  if (props.status === 'warning') return 'value-warning';
  if (props.status === 'error') return 'value-error';
  return '';
});

// 状态类名
const statusClass = computed(() => {
  return `status-${props.status}`;
});

// 状态文本
const statusText = computed(() => {
  return props.statusTextMap[props.status] || props.status;
});

// 趋势值
const trendValue = computed(() => {
  return Math.abs(props.trend);
});
</script>

<style lang="scss" scoped>
.data-display {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #2D3238;
  border-radius: 6px;
  border: 1px solid #3A3F45;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
  position: relative;
  
  &.size-sm {
    min-width: 120px;
    
    .display-label {
      font-size: 12px;
    }
    
    .display-value {
      font-size: 18px;
    }
    
    .led-digit {
      font-size: 18px;
      width: 14px;
    }
  }
  
  &.size-md {
    min-width: 160px;
    
    .display-label {
      font-size: 14px;
    }
    
    .display-value {
      font-size: 24px;
    }
    
    .led-digit {
      font-size: 24px;
      width: 18px;
    }
  }
  
  &.size-lg {
    min-width: 200px;
    
    .display-label {
      font-size: 16px;
    }
    
    .display-value {
      font-size: 32px;
    }
    
    .led-digit {
      font-size: 32px;
      width: 24px;
    }
  }
  
  .display-label {
    color: #aaa;
    margin-bottom: 4px;
    font-weight: 500;
  }
  
  /* 数值显示样式 */
  .value-display {
    .display-value {
      font-weight: 700;
      color: #fff;
      
      &.value-normal {
        color: var(--status-green);
      }
      
      &.value-warning {
        color: var(--status-yellow);
      }
      
      &.value-error {
        color: var(--status-red);
      }
      
      .unit {
        font-size: 0.6em;
        color: #aaa;
        margin-left: 4px;
      }
    }
    
    .display-trend {
      display: flex;
      align-items: center;
      font-size: 12px;
      margin-top: 4px;
      
      .trend-up {
        color: var(--status-green);
      }
      
      .trend-down {
        color: var(--status-red);
      }
      
      .trend-neutral {
        color: #aaa;
      }
    }
  }
  
  /* LED数字显示样式 */
  .led-display {
    .led-digits {
      display: flex;
      align-items: center;
      font-family: 'Digital-7', monospace;
      
      .led-digit {
        display: inline-block;
        text-align: center;
        color: #31CCEC;
        text-shadow: 
          0 0 5px rgba(49, 204, 236, 0.8),
          0 0 10px rgba(49, 204, 236, 0.5),
          0 0 15px rgba(49, 204, 236, 0.3);
        background: rgba(0,0,0,0.3);
        border-radius: 2px;
        margin-right: 2px;
        padding: 2px 0;
        transition: all 0.3s ease;
        
        &:hover {
          text-shadow: 
            0 0 8px rgba(49, 204, 236, 0.9),
            0 0 15px rgba(49, 204, 236, 0.6),
            0 0 20px rgba(49, 204, 236, 0.4);
        }
      }
      
      .led-unit {
        margin-left: 4px;
        font-size: 0.6em;
        color: #aaa;
      }
    }
  }
  
  /* 状态显示样式 */
  .status-display {
    .status-indicator {
      display: flex;
      align-items: center;
      font-weight: 500;
      
      .status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: glow 2s infinite;
      }
      
      .status-normal {
        color: var(--status-green);
        
        &.status-dot {
          background-color: var(--status-green);
          box-shadow: 0 0 5px var(--status-green);
        }
      }
      
      .status-warning {
        color: var(--status-yellow);
        
        &.status-dot {
          background-color: var(--status-yellow);
          box-shadow: 0 0 5px var(--status-yellow);
        }
      }
      
      .status-error {
        color: var(--status-red);
        
        &.status-dot {
          background-color: var(--status-red);
          box-shadow: 0 0 5px var(--status-red);
        }
      }
      
      .status-inactive {
        color: #aaa;
        
        &.status-dot {
          background-color: #aaa;
          box-shadow: 0 0 5px #aaa;
        }
      }
    }
  }
  
  /* 金属质感背景和边框 */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.05) 100%);
    border-radius: 6px;
    pointer-events: none;
  }
  
  /* 呼吸动画效果 */
  @keyframes glow {
    0% { box-shadow: 0 0 5px currentColor; }
    50% { box-shadow: 0 0 10px currentColor; }
    100% { box-shadow: 0 0 5px currentColor; }
  }
  
  /* 响应式布局支持 */
  @media screen and (max-width: 768px) {
    &.size-lg {
      min-width: 160px;
      
      .display-label {
        font-size: 14px;
      }
      
      .display-value {
        font-size: 24px;
      }
      
      .led-digit {
        font-size: 24px;
        width: 18px;
      }
    }
    
    &.size-md {
      min-width: 120px;
      
      .display-label {
        font-size: 12px;
      }
      
      .display-value {
        font-size: 18px;
      }
      
      .led-digit {
        font-size: 18px;
        width: 14px;
      }
    }
  }
}
</style>