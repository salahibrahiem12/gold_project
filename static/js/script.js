document.addEventListener('DOMContentLoaded', () => {
  const form      = document.getElementById('filter-form');
  const sd        = document.getElementById('start-date');
  const ed        = document.getElementById('end-date');
  const presets   = document.querySelectorAll('.preset');
  const loading   = document.getElementById('loading');
  const results   = document.getElementById('results');
  const tableBody = document.getElementById('table-body');
  const daysCount = document.getElementById('days-count');
  const avgPrice  = document.getElementById('avg-price');
  const maxPrice  = document.getElementById('max-price');
  const minPrice  = document.getElementById('min-price');
  const maxDate   = document.getElementById('max-date');
  const minDate   = document.getElementById('min-date');
  const chartDiv  = document.getElementById('chart-div');
  const exportBtn = document.getElementById('export-btn');

  function spinOn() {
    loading.style.display = 'flex';
    results.style.display = 'none';
  }
  function spinOff() {
    loading.style.display = 'none';
    results.style.display = 'block';
  }

  function setRange(days) {
    const now = new Date();
    const tmr = new Date(now); tmr.setDate(now.getDate()+1);
    const fut = new Date(now); fut.setDate(now.getDate()+days);
    sd.value = tmr.toISOString().split('T')[0];
    ed.value = fut.toISOString().split('T')[0];
  }
  setRange(30);

  presets.forEach(btn => {
    btn.addEventListener('click', () => {
      presets.forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      setRange(+btn.dataset.days);
      fetchData();
    });
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    presets.forEach(b=>b.classList.remove('active'));
    spinOn();
    fetchData();
  });

  async function fetchData() {
    spinOn();
    const start = sd.value, end = ed.value;
    try {
      const res = await fetch(`/api/forecast?start_date=${start}&end_date=${end}`);
      const json= await res.json();
      renderTable(json.data);
      renderSummary(json.summary);
      renderChart(json.data);
      exportBtn.href = `/export-excel?start_date=${start}&end_date=${end}`;
    } catch (e) {
      alert('حدث خطأ في جلب البيانات.');
      tableBody.innerHTML = `<tr><td colspan="2">لا توجد بيانات</td></tr>`;
    } finally {
      spinOff();
    }
  }

  function renderTable(data) {
    if (!data.length) {
      tableBody.innerHTML = `<tr><td colspan="2">لا توجد بيانات</td></tr>`;
      daysCount.textContent = 0;
      return;
    }
    daysCount.textContent = data.length;
    tableBody.innerHTML = data.map(d=>
      `<tr><td>${d.ds}</td><td>${d.yhat.toFixed(2)}</td></tr>`
    ).join('');
  }

  function renderSummary(s) {
    avgPrice.textContent = s.avg_price.toFixed(2) + '$';
    maxPrice.textContent = s.max_price.toFixed(2) + '$';
    minPrice.textContent = s.min_price.toFixed(2) + '$';
    maxDate.textContent = 'في ' + s.max_date;
    minDate.textContent = 'في ' + s.min_date;
  }

  function renderChart(data) {
    const x = data.map(d=>d.ds);
    const y = data.map(d=>d.yhat);
    const lo= data.map(d=>d.yhat_lower);
    const hi= data.map(d=>d.yhat_upper);

    const t1 = { x, y, type:'scatter', mode:'lines+markers',
                 name:'السعر', line:{color:'#00c6ff'} };
    const t2 = { x, y:lo, type:'scatter', mode:'lines',
                 name:'الحد الأدنى', line:{dash:'dot',color:'#ff5722'} };
    const t3 = { x, y:hi, type:'scatter', mode:'lines',
                 name:'الحد الأعلى', line:{dash:'dot',color:'#ff5722'},
                 fill:'tonexty', fillcolor:'rgba(255,87,34,0.1)' };

    Plotly.newPlot(chartDiv,[t2,t3,t1],{
      margin:{t:40}, xaxis:{title:'التاريخ'}, yaxis:{title:'سعر (USD$)'}
    },{responsive:true});
  }

  window.resetFilter = () => {
    presets.forEach(b=>b.classList.remove('active'));
    document.querySelector('.preset[data-days="30"]').classList.add('active');
    setRange(30);
    fetchData();
  };

  // أول تحميل
  fetchData();
});