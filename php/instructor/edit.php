<?php
$root = "..";

$page = file_get_contents("$root/template/page.html");

/* navigation */
$page = str_replace("%nav%", file_get_contents("$root/template/nav.html"), $page);
$page = str_replace("%nav-items%", file_get_contents("$root/template/class-list.html"), $page);
$page = str_replace("%sel-class%", "sel", $page);

/* class list */
$page = str_replace("%class-cur%", "CSE 12", $page);
$arr = array("CSE 12", "CSE 100 Super Long Name");
foreach($arr as $class) {
  $item = file_get_contents("$root/template/class-item.html");
  $item = str_replace("%class-id%", "lession.php", $item);
  $item = str_replace("%class-name%", $class, $item);
  $page = str_replace("%class-items%", "$item%class-items%", $page);
}

/* lessions */
$lessions = file_get_contents("$root/template/lession-list.html");
$arr = array("Stacks and Queues", "Trees");
foreach($arr as $lession) {
  $item = file_get_contents("$root/template/lession-item.html");
  $item = str_replace("%item-name%", $lession, $item);
  $lessions = str_replace("%lession-items%", "$item%lession-items%", $lessions);
}
$page = str_replace("%body%", "$lessions%body%", $page);

/* questions */
$edit = file_get_contents("$root/template/edit-question.html");
$edit = str_replace("%dest%", "edit.php", $edit);
$page = str_replace("%body%", "$edit%body%", $page);

/* whole page replacement and cleanup */
$page = str_replace("%page%", "portal", $page);
$page = str_replace("%root%", $root, $page);
$page = ereg_replace("%[[A-Za-z0-9_-]*%", "", $page);

print $page;
?>
