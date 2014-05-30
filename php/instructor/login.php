<?php
$root = "..";

$page = file_get_contents("$root/template/page.html");

/* navigation */
$page = str_replace("%nav%", file_get_contents("$root/template/nav.html"), $page);
$page = str_replace("%nav-items%", file_get_contents("$root/template/class-list.html"), $page);
$page = str_replace("%sel-login%", "sel", $page);

/* class list */
$page = str_replace("%class-cur%", "CSE 12", $page);
$arr = array("CSE 12", "CSE 100");
foreach($arr as $class) {
  $item = file_get_contents("$root/template/class-item.html");
  $item = str_replace("%class-id%", "lession.php", $item);
  $item = str_replace("%class-name%", $class, $item);
  $page = str_replace("%class-items%", "$item%class-items%", $page);
}

/* body */
$page = str_replace("%body%", file_get_contents("$root/template/login.html"), $page);

/* whole page replacement and cleanup */
$page = str_replace("%page%", "portal", $page);
$page = str_replace("%root%", $root, $page);
$page = ereg_replace("%[[A-Za-z0-9_-]*%", "", $page);

print $page;
?>
