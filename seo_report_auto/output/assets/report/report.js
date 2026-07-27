(function () {
  const charts = window.REPORT_CHARTS || {};

  const blue = '#1E6FEB';
  const blueSoft = '#7fb8ff';
  const gray = '#D1D5DB';
  const text = '#374151';
  const muted = '#9CA3AF';
  const grid = '#EDF2F7';

  function currencyCompact(value) {
    if (Math.abs(value) >= 1000000) return 'R$ ' + (value / 1000000).toFixed(1).replace('.', ',') + ' mi';
    if (Math.abs(value) >= 1000) return 'R$ ' + (value / 1000).toFixed(0).replace('.', ',') + ' mil';
    return 'R$ ' + value.toFixed(0).replace('.', ',');
  }

  function numberCompact(value) {
    if (Math.abs(value) >= 1000000) return (value / 1000000).toFixed(1).replace('.', ',') + 'M';
    if (Math.abs(value) >= 1000) return (value / 1000).toFixed(0).replace('.', ',') + 'k';
    return String(Math.round(value));
  }

  function createChart(id, option) {
    const element = document.getElementById(id);
    if (!element || typeof echarts === 'undefined') return;
    const chart = echarts.init(element, null, { renderer: 'svg' });
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
  }

  const labels12 = charts.labels12 || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

  createChart('chart-sessoes-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [gray, blue],
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: labels12, axisLine: { lineStyle: { color: grid } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: grid } } },
    series: [
      { name: String((charts.meta && charts.meta.ano ? charts.meta.ano - 1 : 2025)), type: 'bar', barMaxWidth: 22, data: charts.web_sessions_previous || [], label: { show: true, position: 'top', formatter: (p) => numberCompact(p.value), color: muted, fontSize: 9 } },
      { name: String((charts.meta && charts.meta.ano) || 2026), type: 'bar', barMaxWidth: 22, data: charts.web_sessions_current || [], itemStyle: { borderRadius: [6, 6, 0, 0] }, label: { show: true, position: 'top', formatter: (p) => numberCompact(p.value), color: text, fontSize: 10, fontWeight: 'bold' } }
    ]
  });

  createChart('chart-receita-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [gray, blue],
    tooltip: {
      trigger: 'axis',
      valueFormatter: currencyCompact,
      borderColor: '#E5E7EB',
      textStyle: { color: text }
    },
    legend: {
      top: 0,
      left: 0,
      icon: 'line',
      itemWidth: 18,
      itemHeight: 2,
      textStyle: { color: muted, fontSize: 11 }
    },
    grid: { left: 56, right: 18, top: 34, bottom: 34 },
    xAxis: {
      type: 'category',
      data: labels12,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#EEF2F7' } },
      axisTick: { show: false },
      axisLabel: { color: muted, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitNumber: 5,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: grid, width: 1 } },
      axisLabel: { formatter: currencyCompact, color: muted, fontSize: 10 }
    },
    series: [
      {
        name: String((charts.meta && charts.meta.ano ? charts.meta.ano - 1 : 2025)),
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: gray, borderColor: '#FFFFFF', borderWidth: 1 },
        data: charts.web_revenue_previous || []
      },
      {
        name: String((charts.meta && charts.meta.ano) || 2026),
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { width: 3 },
        itemStyle: { color: blue, borderColor: '#FFFFFF', borderWidth: 1.5 },
        data: charts.web_revenue_current || [],
        label: { show: true, position: 'top', formatter: (p) => currencyCompact(p.value), color: text, fontSize: 9, backgroundColor: 'rgba(255,255,255,0.7)', borderRadius: 2, padding: 2 }
      }
    ]
  });

  createChart('chart-share-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    tooltip: { trigger: 'item' },
    color: [blue, '#d8dee6'],
    series: [{
      type: 'pie',
      radius: ['58%', '82%'],
      center: ['50%', '50%'],
      label: {
        show: true,
        position: 'center',
        formatter: (charts.web_share || 0).toFixed(1).replace('.', ',') + '%\ndo site',
        fontSize: 18,
        fontWeight: 700,
        lineHeight: 24,
      },
      data: [
        { value: charts.web_share || 0, name: 'Orgânico' },
        { value: 100 - (charts.web_share || 0), name: 'Total restante' }
      ]
    }]
  });

  createChart('chart-rps-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [blue, gray],
    tooltip: { trigger: 'axis' },
    grid: { left: 44, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: ['Orgânico', 'Total'] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: grid } }, axisLabel: { formatter: currencyCompact } },
    series: [{ type: 'bar', barMaxWidth: 34, data: [charts.web_rps_organico || 0, charts.web_rps_total || 0], itemStyle: { borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: (p) => currencyCompact(p.value), color: text, fontSize: 11, fontWeight: 'bold' } }]
  });

  createChart('chart-indice-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [blue, gray],
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 48, right: 16, top: 16, bottom: 40 },
    xAxis: { type: 'category', data: charts.index_labels || [] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: grid } } },
    series: [
      { name: 'Receita orgânica', type: 'line', smooth: true, symbolSize: 6, lineStyle: { width: 3 }, data: charts.web_index_organico || [], label: { show: true, position: 'top', color: text, fontSize: 8, backgroundColor: 'rgba(255,255,255,0.7)', padding: 1 } },
      { name: 'Receita total', type: 'line', smooth: true, symbolSize: 6, lineStyle: { width: 2, type: 'dashed' }, data: charts.web_index_total || [] }
    ]
  });

  createChart('chart-impressoes-web', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [blue],
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 16, top: 20, bottom: 24 },
    xAxis: { type: 'category', data: charts.web_impressions_labels || [] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: grid } }, axisLabel: { formatter: numberCompact } },
    series: [{ type: 'line', smooth: true, areaStyle: { opacity: 0.15 }, symbolSize: 8, data: charts.web_impressions_values || [], label: { show: true, position: 'top', formatter: (p) => numberCompact(p.value), color: text, fontSize: 9, backgroundColor: 'rgba(255,255,255,0.8)', padding: 2, borderRadius: 2 } }]
  });

  createChart('chart-app-receita', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [gray, blue],
    tooltip: {
      trigger: 'axis',
      valueFormatter: currencyCompact,
      borderColor: '#E5E7EB',
      textStyle: { color: text }
    },
    legend: {
      top: 0,
      left: 0,
      icon: 'line',
      itemWidth: 18,
      itemHeight: 2,
      textStyle: { color: muted, fontSize: 11 }
    },
    grid: { left: 56, right: 16, top: 34, bottom: 34 },
    xAxis: {
      type: 'category',
      data: labels12,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#EEF2F7' } },
      axisTick: { show: false },
      axisLabel: { color: muted, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitNumber: 5,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: grid, width: 1 } },
      axisLabel: { formatter: currencyCompact, color: muted, fontSize: 10 }
    },
    series: [
      {
        name: String((charts.meta && charts.meta.ano ? charts.meta.ano - 1 : 2025)),
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: gray, borderColor: '#FFFFFF', borderWidth: 1 },
        data: charts.app_revenue_previous || []
      },
      {
        name: String((charts.meta && charts.meta.ano) || 2026),
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { width: 3 },
        itemStyle: { color: blue, borderColor: '#FFFFFF', borderWidth: 1.5 },
        data: charts.app_revenue_current || [],
        label: { show: true, position: 'top', formatter: (p) => currencyCompact(p.value), color: text, fontSize: 9, backgroundColor: 'rgba(255,255,255,0.7)', borderRadius: 2, padding: 2 }
      }
    ]
  });

  createChart('chart-impressoes-farma', {
    textStyle: { fontFamily: 'Inter', color: text },
    color: [blueSoft],
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 16, top: 20, bottom: 24 },
    xAxis: { type: 'category', data: charts.farma_impressions_labels || [] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: grid } }, axisLabel: { formatter: numberCompact } },
    series: [{ type: 'line', smooth: true, areaStyle: { opacity: 0.16 }, symbolSize: 8, data: charts.farma_impressions_values || [], label: { show: true, position: 'top', formatter: (p) => numberCompact(p.value), color: text, fontSize: 9, backgroundColor: 'rgba(255,255,255,0.8)', padding: 2, borderRadius: 2 } }]
  });
})();
