<html>
<head>
  <title>Stats</title>
  <style type="text/css">
  @media (min-width: 1165px) {
    .twocolumn {
      -moz-column-count: 2;
      -webkit-column-count: 2;
      column-count: 2;
      column-fill: balance;
    }
  } 
  body {
    font-family: Verdana,Arial,sans-serif;
    background: #c0c0c0;
    text-align: center;
  } 
  h1 {
    font-size: 150%;
  }
  h2 {
    font-size: 110%;
  }
  h3 {
    font-size: 100%;
    margin-top: 0em;
    margin-bottom: 0.5em;
    padding-top: 1em;
    break-before: column; 
    break-inside: avoid-column; 
    break-after: avoid-column;
  }
  .graph {
    -moz-column-break-inside: avoid;
    -webkit-column-break-inside: avoid;
    column-break-inside: avoid;
  }
  </style>
</head>
<body>

<?php
  function image($title, $name, $range) {
    if ($range != '') {
        $range = '_' . $range;
    }
    echo '<div class="graph">';
    echo ' <h3>' . $title . '</h3>';
    echo ' <img src="' . $name . $range . '.png">';
    echo '</div>';
  }

  $host = gethostname();
  $date = getdate();
  $client = $_SERVER['REMOTE_ADDR'];
  $range = $_GET['r'];
  echo "<h1>$host</h1>";
  echo "<h2>";
  switch ($range) {
  case 'y':
    echo "Yearly graphs (1 day average)";
    break;
  case 'm': 
    echo "Monthly graphs (2 hour average)";
    break;
  case 'w':
    echo "Weekly graphs (30 minute average)";
    break;
  default:
    echo "Daily graphs (5 minute average)";
    $range = '';
  }
  echo "</h2>";

  shell_exec('PATH=/opt/bin:$PATH /root/monitor/monitor.py report ' . $range);
?>

<p>
<div class="twocolumn">
<?php
  image('Router',       'tplink',  $range);
  image('NAS network',  'network', $range);
  image('CPU stats',    'cpu',     $range);
  image('CPU load',     'load',    $range);
  image('Memory usage', 'memory',  $range);
  image('Disk temperature', 'hd.temp', $range);
  image('Disk I/O',     'hdio',    $range);
  image('Volume usage', 'volumes', $range);
?>
</div>

<p>

<?php
  echo "<small>", strftime("%c"), "<br>Connect from $client</small>";
?>

</body>
</html>
