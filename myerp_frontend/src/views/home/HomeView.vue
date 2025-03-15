<script setup>
import MainBox from '@/components/MainBox.vue'
import homeHttp from '@/api/homeHttp'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts';

const inventoryByBrand = ref([])
const staffPerformance = ref([])
const currentYearMonthlySales = ref({})
let salesChart = null
let performanceChart = null
let inventoryChart = null
const loading = ref(true)

onMounted(async () => {
  Promise.all([
    getInventoryByBrand(),
    getStaffPerformance(),
  getCurrentYearMonthlySales()
  ]).then(() => {
    loading.value = false
    nextTick(() => {
      setTimeout(() => {
        initCharts()
      }, 300)
    })
  })

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (salesChart) {
    salesChart.dispose()
  }
  if (performanceChart) {
    performanceChart.dispose()
  }
  if (inventoryChart) {
    inventoryChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (salesChart) {
    salesChart.resize()
  }
  if (performanceChart) {
    performanceChart.resize()
  }
  if (inventoryChart) {
    inventoryChart.resize()
  }
}

const getInventoryByBrand = async () => {
  try {
    const res = await homeHttp.getInventoryByBrand()
    if (res.status === 200) {
      inventoryByBrand.value = res.data.inventory_by_brand || []
      console.log('库存数据:', inventoryByBrand.value)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('获取库存数据失败:', error)
  }
}

const getStaffPerformance = async () => {
  try {
    const res = await homeHttp.getStaffPerformance()
    if (res.status === 200) {
      staffPerformance.value = res.data.staff_performance || []
      console.log('员工业绩数据:', staffPerformance.value)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('获取员工业绩数据失败:', error)
  }
}

const getCurrentYearMonthlySales = async () => {
  try {
    const res = await homeHttp.getCurrentYearMonthlySales()
    if (res.status === 200) {
      currentYearMonthlySales.value = res.data || {}
      console.log('月度销售数据:', currentYearMonthlySales.value)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    console.error('获取月度销售数据失败:', error)
  }
}

const initCharts = async () => {
  console.log('初始化图表')
  const salesDom = document.getElementById('sales-chart')
  const performanceDom = document.getElementById('performance-chart')
  const inventoryDom = document.getElementById('inventory-chart')

  // 定义ECharts初始化选项，提高滚动性能
  const defaultOpts = {
    renderer: 'canvas',
    useDirtyRect: true,
    width: 'auto',
    height: 'auto'
  }

  if (performanceDom) {
    try {
      performanceChart = echarts.init(performanceDom, null, defaultOpts)
      updatePerformanceChart()
    } catch (error) {
      console.error('初始化业绩图表失败:', error)
    }
  }

  if (salesDom) {
    try {
      salesChart = echarts.init(salesDom, null, defaultOpts)
      updateSalesChart()
    } catch (error) {
      console.error('初始化销售图表失败:', error)
    }
  }

  if (inventoryDom) {
    try {
      inventoryChart = echarts.init(inventoryDom, null, defaultOpts)
      updateInventoryChart()
    } catch (error) {
      console.error('初始化库存图表失败:', error)
    }
  }
}

const updateSalesChart = () => {
  if (!salesChart) {
    console.error('销售图表未初始化')
    return
  }

  if (!currentYearMonthlySales.value || Object.keys(currentYearMonthlySales.value).length === 0) {
    console.warn('没有月度销售数据')
    return
  }

  try {
    const months = Object.keys(currentYearMonthlySales.value)
    const values = Object.values(currentYearMonthlySales.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c} 元',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: '#e6e6e6',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
  xAxis: {
    type: 'category',
        data: months.map(month => `${month}月`),
        axisLabel: {
          interval: 0
        },
        axisLine: {
          lineStyle: {
            color: '#c0c4cc'
          }
        }
  },
  yAxis: {
        type: 'value',
        name: '销售额(元)',
        nameTextStyle: {
          color: '#606266'
        },
        axisLabel: {
          formatter: '{value}',
          color: '#606266'
        },
        splitLine: {
          lineStyle: {
            color: '#ebeef5'
          }
        }
  },
  series: [
    {
          data: values,
      type: 'line',
          name: '销售额',
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: {
            color: '#409EFF'
          },
          lineStyle: {
            width: 3
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(64,158,255,0.3)'
              },
              {
                offset: 1,
                color: 'rgba(64,158,255,0.1)'
              }
            ])
          }
        }
      ]
    }

    salesChart.setOption(option)
  } catch (error) {
    console.error('更新销售图表失败:', error)
  }
}

const updatePerformanceChart = () => {
  if (!performanceChart) {
    console.error('业绩图表未初始化')
    return
  }

  if (!staffPerformance.value || !staffPerformance.value.length) {
    console.warn('没有员工业绩数据')
    return
  }

  try {
    const performanceValues = staffPerformance.value.map(item => item.total_amount)

    // 根据业绩值排序
    const sortedData = staffPerformance.value
      .map((item) => ({
        name: item.staff__name,
        value: item.total_amount,
        percentage: item.amount_percentage
      }))
      .sort((a, b) => b.value - a.value)

    const sortedNames = sortedData.map(item => item.name)
    const sortedValues = sortedData.map(item => item.value)
    const sortedPercentages = sortedData.map(item => item.percentage)

    // 计算总销售额
    const totalSales = performanceValues.reduce((sum, val) => sum + val, 0)

    const option = {
      title: {
        text: `总销售额: ¥${totalSales.toLocaleString()}`,
        subtext: '当月员工销售业绩排名',
        left: 'center',
        top: 0,
        textStyle: {
          fontSize: 16,
          color: '#303133'
        },
        subtextStyle: {
          fontSize: 12,
          color: '#909399'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function(params) {
          const data = params[0]
          const index = sortedNames.indexOf(data.name)
          return `${data.name}<br/>
                  销售额: ¥${data.value.toLocaleString()} 元<br/>
                  占比: ${sortedPercentages[index]}%`
        },
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: '#e6e6e6',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '80px',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: sortedNames,
        axisLabel: {
          interval: 0,
          rotate: 30,
          color: '#606266'
        },
        axisLine: {
          lineStyle: {
            color: '#c0c4cc'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '销售额(元)',
        nameTextStyle: {
          color: '#606266'
        },
        axisLabel: {
          formatter: '{value}',
          color: '#606266'
        },
        splitLine: {
          lineStyle: {
            color: '#ebeef5'
          }
        }
      },
      series: [
        {
          type: 'bar',
          data: sortedValues,
          barWidth: '50%',
          itemStyle: {
            color: function(params) {
              // 创建渐变色数组，根据排名显示不同颜色
              const colorList = [
                new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#f7b733' },
                  { offset: 1, color: '#fc4a1a' }
                ]),
                new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#4facfe' },
                  { offset: 1, color: '#00f2fe' }
                ]),
                new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#667eea' },
                  { offset: 1, color: '#764ba2' }
                ])
              ];
              // 前三名使用特殊颜色，其余使用默认颜色
              if (params.dataIndex < 3) {
                return colorList[params.dataIndex];
              }
              return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 1, color: '#188df0' }
              ]);
            },
            borderRadius: [5, 5, 0, 0]
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0,0,0,0.2)'
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '¥{c}',
            fontSize: 12,
            fontWeight: 'bold',
            color: '#606266'
          }
        }
      ]
    }

    performanceChart.setOption(option)
  } catch (error) {
    console.error('更新业绩图表失败:', error)
  }
}

const updateInventoryChart = () => {
  if (!inventoryChart) {
    console.error('库存图表未初始化')
    return
  }

  if (!inventoryByBrand.value || !inventoryByBrand.value.length) {
    console.warn('没有库存数据')
    return
  }

  try {
    const brands = inventoryByBrand.value.map(item => item.brand__name)
    const values = inventoryByBrand.value.map(item => item.total_value)
    const totalValue = values.reduce((sum, value) => sum + value, 0)

    // 定义颜色序列
    const colorPalette = [
      '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
      '#36a3f7', '#3f9', '#f90', '#F56C6C', '#87CEFA'
    ];

    const option = {
      title: {
        text: '品牌库存价值分布',
        subtext: `总库存价值: ¥${totalValue.toLocaleString()}`,
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
          color: '#303133'
        },
        subtextStyle: {
          fontSize: 14,
          color: '#606266',
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: ¥{c} ({d}%)',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        borderColor: '#e6e6e6',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        }
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        data: brands,
        textStyle: {
          color: '#606266'
        },
        formatter: function(name) {
          const index = brands.indexOf(name);
          const value = values[index];
          const percentage = ((value / totalValue) * 100).toFixed(1);
          return `${name}: ${percentage}%`;
        }
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '55%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
              formatter: '{b}: ¥{c}\n({d}%)'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            }
          },
          labelLine: {
            show: false
          },
          data: brands.map((brand, index) => ({
            name: brand,
            value: values[index],
            itemStyle: {
              color: colorPalette[index % colorPalette.length]
            }
          }))
        }
      ]
    }

    inventoryChart.setOption(option)
  } catch (error) {
    console.error('更新库存图表失败:', error)
  }
}
</script>

<template>
  <MainBox title="主页">
    <div v-if="loading" class="loading-container">
      <el-card v-loading="true" element-loading-text="加载中..." element-loading-background="rgba(255, 255, 255, 0.8)" style="width: 100%; height: 100%;">
      </el-card>
    </div>
    <div v-else class="dashboard-container">
      <el-row class="chart-row">
        <!-- 员工业绩图表（放在最上面） -->
        <el-col :span="24">
          <el-card class="mb-4 chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>本月员工业绩</span>
              </div>
            </template>
            <div id="performance-chart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row class="chart-row">
        <!-- 销售趋势和库存价值并排展示 -->
        <el-col :xs="24" :sm="24" :md="12" class="chart-col">
          <el-card class="mb-4 chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>年度销售趋势</span>
              </div>
            </template>
            <div id="sales-chart" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="24" :md="12" class="chart-col">
          <el-card class="mb-4 chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>品牌库存价值</span>
              </div>
            </template>
            <div id="inventory-chart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </MainBox>
</template>

<style scoped>
.dashboard-container {
  width: 100%;
  overflow-x: hidden;
  max-width: 100%;
  box-sizing: border-box;
}

.chart-row {
  width: 100%;
  margin: 0 !important;
  box-sizing: border-box;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  transition: all 0.3s;
  margin-bottom: 20px;
  width: 100%;
  max-width: 100%;
}

.chart-card:hover {
  box-shadow: 0 6px 16px -8px rgba(0, 0, 0, 0.2),
              0 9px 28px 0 rgba(0, 0, 0, 0.1),
              0 12px 48px 16px rgba(0, 0, 0, 0.05) !important;
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 350px;
  padding: 10px;
  box-sizing: border-box;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
  width: 100%;
}

.chart-col {
  padding: 0 5px;
  box-sizing: border-box;
}

/* 移除el-row的默认间距，防止溢出 */
:deep(.el-row) {
  margin-left: 0 !important;
  margin-right: 0 !important;
  width: 100%;
}

:deep(.el-col) {
  padding-left: 0 !important;
  padding-right: 0 !important;
}
</style>
