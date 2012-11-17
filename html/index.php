<html>
<head>
  <title>Stats</title>
  <style type="text/css">
  body {
    font-family: Verdana,Arial,sans-serif;
    background: #c0c0c0;
    text-align: center;
  } 
  @media (min-width: 1300px) {
    .twocolumn {
      -moz-column-count: 2;
      -webkit-column-count: 2;
      column-count: 2;
      column-fill: balance;
    }
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
  </style>
</head>
<body>

<?php
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

  shell_exec('PATH=/opt/bin:$PATH /root/monitor/monitor.py report ' + $range);

?>

<p>
<div class="twocolumn">

<h3>Network</h3>
<img src="g0.png">

<h3>CPU stat</h3>
<img src="g1.png">

<h3>CPU load</h3>
<img src="g2.png">

<h3>Memory usage</h3>
<img src="g3.png">

<h3>Disk temperature</h3>
<img src="g4.png">

<h3>Disk I/O</h3>
<img src="g5.png">

<h3>Disk I/O time</h3>
<img src="g6.png">

<h3>Volume usage</h3>
<img src="g7.png">

</div>

<p>

<?php
  echo "<small>", strftime("%c"), "<br>Connect from $client</small>";
?>

</body>
</html>
