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
$questions = file_get_contents("$root/template/question-list.html");
$arr = array("Insert into a Stack", "Remove from a Stack", "Insert into a Queue", "Remove from a Queue");
$ans = array(array("O(1)", "40"), array("O(n)", "20"), array("O(log(n))", "30"), array("None of the above", "10"));
foreach($arr as $i => $question) {
  $item = file_get_contents("$root/template/question-item.html");
  $item = str_replace("%item-id%", $i, $item);
  $item = str_replace("%item-name%", $question, $item);
  $item = str_replace("%prompt%", "What is the run-time complexity of inserting into a stack?", $item);
  foreach($ans as $i => $answer) {
    $result = file_get_contents("$root/template/question-result.html");
    $result = str_replace("%text%", $answer[0], $result);
    $result = str_replace("%percent%", $answer[1], $result);
    $item = str_replace("%results%", "$result%results%", $item);
  }
  $questions = str_replace("%question-items%", "$item%question-items%", $questions);
}
$page = str_replace("%body%", "$questions%body%", $page);

/* whole page replacement and cleanup */
$page = str_replace("%page%", "portal", $page);
$page = str_replace("%root%", $root, $page);
$page = ereg_replace("%[[A-Za-z0-9_-]*%", "", $page);

print $page;
?>
