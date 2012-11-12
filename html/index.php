<html>
<head>
  <title>Stats</title>
  <style type="text/css">
  body {
    font-family: Verdana,Arial,sans-serif;
    background: #c0c0c0;
  } 
  .twocolumn {
    -moz-column-count: 2;
    -webkit-column-count: 2;
    column-count: 2;
    column-fill: balance;
  }
  h2 {
    text-align: center;
  }
  h3 {
    font-size: 100%;
    margin-top: 0em;
    margin-bottom: 0.5em;
    padding-top: 1em;
    text-align: center;
    break-before: column; 
    break-inside: avoid-column; 
    break-after: avoid-column;
  }
  </style>
</head>
<body>

<?php
  exec('/root/monitor/monitor.py report');

  $host = exec('hostname');
  $date = exec('/bin/date');
  $client = $_SERVER['REMOTE_ADDR'];
  echo "<h2>$host</h2>";
?>

<p>
<div class="twocolumn">

<h3>Network</h3>
<img src="g0.png">

<h3>CPU load</h3>
<img src="g1.png">

<h3>Memory usage</h3>
<img src="g2.png">

<h3>Disk temperature</h3>
<img src="g3.png">

<h3>Disk I/O</h3>
<img src="g4.png">

<h3>Volume usage</h3>
<img src="g5.png">

</div>

<p>

<?php
  echo "<small><em>$date from $client</em></small>";
?>

</body>
</html>
