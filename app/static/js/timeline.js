// Timeline chart for the address page (issue #7).
// Draws one horizontal bar per business, from its opened date to its closed
// date (or today, if it's still open). Gaps between bars = vacant periods.

(function () {
  const data = window.TIMELINE_DATA || [];
  const canvas = document.getElementById("timeline-chart");
  if (!canvas || data.length === 0) return;

  // Dates as milliseconds, so Chart.js can use a plain number axis
  // (no extra date library needed)
  const toMs = (iso) => new Date(iso + "T00:00:00").getTime();
  const fmt = (ms) =>
    new Date(ms).toLocaleDateString("en-US", { month: "short", year: "numeric" });

  const starts = data.map((d) => toMs(d.start));
  const ends = data.map((d) => toMs(d.end));
  const pad = 1000 * 60 * 60 * 24 * 90; // ~3 months of space on each side

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: data.map((d) => d.name),
      datasets: [
        {
          // Floating bars: each value is [start, end]
          data: data.map((d, i) => [starts[i], ends[i]]),
          backgroundColor: data.map((d) => (d.open ? "#198754" : "#6c757d")),
          borderRadius: 4,
          barThickness: 22,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: "linear",
          min: Math.min(...starts) - pad,
          max: Math.max(...ends) + pad,
          ticks: { callback: (value) => new Date(value).getFullYear() },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const d = data[ctx.dataIndex];
              const end = d.open ? "Present" : fmt(ends[ctx.dataIndex]);
              return `${fmt(starts[ctx.dataIndex])} – ${end}`;
            },
          },
        },
      },
    },
  });
})();
