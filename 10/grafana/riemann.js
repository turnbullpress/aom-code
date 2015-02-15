/* Original dashboard code modified from: https://github.com/bimlendu/GrafanaScriptedDashboards /*
/* Thanks to Bimlendu Mishra for developing the original! /*

/*global XMLHttpRequest: false */

var window, document, ARGS, $, jQuery, moment, kbn;
var graphite = 'http://graphitea.example.com:8888';

// Specify defaults for URL arguments
var arg_host  = 'graphitea';
var arg_span  = 4;
var arg_from  = '6h';
var arg_env   = 'productiona';
var arg_stack = 'hosts';

if (!_.isUndefined(ARGS.span)) {
  arg_span = ARGS.span;           // graph width
}
if (!_.isUndefined(ARGS.from)) {
  arg_from = ARGS.from;           // show data from 'x' hours until now
}
if (!_.isUndefined(ARGS.host)) {
  arg_host = ARGS.host;           // host name
}
if (!_.isUndefined(ARGS.env)) {
  arg_env = ARGS.env;             // environment
}
if (!_.isUndefined(ARGS.stack)) {
  arg_stack = ARGS.stack;         // stack (hosts or docker)
}

// Execute graphite-api /metrics/find query. Returns array of metric last names ( func('test.cpu-*') returns ['cpu-0','cpu-1',..] )
function find_filter_values(query) {
  var search_url = graphite + '/metrics/find/?query=' + query;
  var res = [];
  var req = new XMLHttpRequest();
  req.open('GET', search_url, false);
  req.send(null);
  var obj = JSON.parse(req.responseText);
  var key;
  for (key in obj) {
    if (obj.hasOwnProperty(key)) {
      if (obj[key].hasOwnProperty("text")) {
        res.push(obj[key].text);
      }
    }
  }
  return res;
}

// Return dashboard filter_list. Optionally include 'All'
function get_filter_object(name, query, show_all) {
  show_all = (show_all === undefined) ? true : show_all;
  var arr = find_filter_values(query);
  var opts = [];
  var i;
  for (i in arr) {
    if (arr.hasOwnProperty(i)) {
      opts.push({"text": arr[i], "value": arr[i]});
    }
  }
  if (show_all === true) {
    opts.unshift({"text": "All", "value": '{' + arr.join() + '}'});
  }
  return {
    type: "filter",
    name: name,
    query: query,
    options: opts,
    current: opts[0],
    includeAll: show_all
  };
}

/*
  Panel templates
*/

function panel_cpu(title, prefix) {
  return {
    title: title,
    type: 'graphite',
    span: arg_span,
    renderer: "flot",
    y_formats: ["none"],
    grid: {max: null, min: 0},
    lines: true,
    fill: 2,
    linewidth: 1,
    tooltip: {
      value_type: 'individual',
      shared: true
    },
    stack: true,
    legend: {show: true},
    percentage: true,
    nullPointMode: "null",
    targets: [
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.wait,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.user,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.system,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.steal,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.interrupt,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.nice,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.idle,4)" },
      { "target": "aliasByNode(" + prefix + "[[host]].cpu.softirq,4)" }
    ],
    aliasColors: {
      "user": "#508642",
      "system": "#EAB839",
      "wait": "#890F02",
      "steal": "#E24D42",
      "idle": "#6ED0E0",
      "nice": "#629E51",
      "irq": "#1F78C1",
      "intrpt": "#EF843C"
    }
  };
}

function panel_memory(title, prefix) {
  return {
    title: title,
    type: 'graphite',
    span: arg_span,
    y_formats: ["none"],
    grid: {max: null, min: 0},
    lines: true,
    fill: 2,
    linewidth: 1,
    stack: true,
    tooltip: {
      value_type: 'individual',
      shared: true
    },
    nullPointMode: "null",
    targets: [
      { "target": "aliasByNode(" + prefix + "[[host]].memory.used,4)" }
    ],
    aliasColors: {
      "used": "#ff6666",
    }
  };
}

function panel_loadavg(title, prefix) {
  return {
    title: title,
    type: 'graphite',
    span: arg_span,
    y_formats: ["none"],
    grid: {max: null, min: 0},
    lines: true,
    fill: 2,
    linewidth: 1,
    tooltip: {
      value_type: 'individual',
      shared: true
    },
    stack : true,
    nullPointMode: "null",
    targets: [
      { "target": "aliasByNode(" + prefix + "[[host]].load.*,4)" }
    ],
    aliasColors: {
      "midterm": "#629E51",
      "shortterm": "#1F78C1",
      "longterm": "#EF843C"
    }
  };
}

function panel_swap_size(title, prefix) {
  return {
    title: title,
    type: 'graphite',
    span: arg_span,
    y_formats: ["none"],
    grid: {max: null, min: 0, leftMin: 0},
    lines: true,
    fill: 2,
    linewidth: 1,
    tooltip: {
      value_type: 'individual',
      shared: true
    },
    stack: true,
    nullPointMode: "null",
    percentage: true,
    targets: [
      { "target": "aliasByNode(" + prefix + "[[host]].swap.{free,used,cached},4)" },
    ],
    aliasColors: {
      "used": "#ff6666",
      "cached": "#EAB839",
      "free": "#66b266"
    }
  };
}

function panel_disk_space(title, prefix) {
  return {
    title: title,
    type: 'graphite',
    span: arg_span,
    y_formats: ["none"],
    grid: {max: null, min: 0, leftMin: 0},
    lines: true,
    fill: 2,
    linewidth: 1,
    tooltip: {
      value_type: 'individual',
      shared: true
    },
    stack: true,
    nullPointMode: "null",
    targets: [
      { "target": "aliasByNode(" + prefix + "[[host]]." + "df.root.percent_bytes.used,6)" },
    ],
    aliasColors: {
      "used": "#e32636"
    }
  };
}

/*
  Row templates
*/

function row_delimiter(title) {
  return {
    title: "_____ " + title,
    height: "20px",
    collapse: false,
    editable: false,
    collapsable: false,
    panels: [{
      title: title,
      editable: false,
      span: 12,
      type: "text",
      mode: "text"
    }]
  };
}

function row_cpu_memory(title, prefix) {
  return {
    title: title,
    height: '250px',
    collapse: false,
    panels: [
      panel_cpu('CPU %', prefix),
      panel_memory('Memory', prefix),
      panel_loadavg('Load avg', prefix)
    ]
  };
}

function row_swap_disk(title, prefix) {
  return {
    title: title,
    height: '250px',
    collapse: false,
    panels: [
      panel_swap_size('Swap size', prefix),
      panel_disk_space('Disk Space on root', prefix)
    ]
  };
}

/*jslint unparam: true, node: true */
return function(callback) {

// Setup some variables
  var dashboard;

  var prefix = arg_env + '.' + arg_stack + '.';

  var arg_filter = prefix + arg_host;

// Set filter

  var dashboard_filter = {
    time: {
      from: "now-" + arg_from,
      to: "now"
    },
    list: [
      get_filter_object("host", arg_filter, false)
    ]
  };

// Define pulldowns

  var pulldowns = [
    {
      type: "filtering",
      collapse: false,
      notice: false,
      enable: true
    },
    {
      type: "annotations",
      enable: false
    }
  ];

// Initialize a skeleton with nothing but a rows array and service object

  dashboard = {
    rows : [],
    services : {}
  };
  dashboard.title = prefix + arg_host;
  dashboard.editable = false;
  dashboard.pulldowns = pulldowns;
  dashboard.services.filter = dashboard_filter;

  $.ajax({
    method: 'GET',
    url: '/'
  })
    .done(function (result) {

  // Construct dashboard rows

      dashboard.rows.push(
        row_cpu_memory('CPU, Memory, Load', prefix),
        row_swap_disk('Swap, Disk Space', prefix)
      );

      callback(dashboard);
    });
}
