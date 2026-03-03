<?php

$title_id = filter_var($_GET["titleId"] ?? "", FILTER_VALIDATE_INT);
$subtitle_id = filter_var($_GET["subtitleId"] ?? "", FILTER_VALIDATE_INT);

if ($title_id === false || $subtitle_id === false) {
    http_response_code(400);
    die("query does not exist");
}

$db = new SQLite3("db.sqlite", SQLITE3_OPEN_READONLY);

$result = $db->query("
    SELECT
        s.id, s.name, s.date, s.comment,
        (SELECT MAX(id) FROM subtitle WHERE title_id = s.title_id AND id < s.id) AS prev_id,
        (SELECT MIN(id) FROM subtitle WHERE title_id = s.title_id AND id > s.id) AS next_id
    FROM subtitle AS s
    WHERE title_id = $title_id AND id = $subtitle_id;
");
$subtitle = $result->fetchArray(SQLITE3_ASSOC);

if ($subtitle === false) {
    $db->close();
    http_response_code(400);
    die("query does not exist");
}

$subtitle_images = [];
$result = $db->query("
    SELECT image
    FROM subtitle_image
    WHERE title_id = $title_id AND subtitle_id = $subtitle_id
    ORDER BY id;
");
while ($subtitle_image = $result->fetchArray(SQLITE3_ASSOC))
    $subtitle_images[] = $subtitle_image;

function html_esc($str) {
    return strtr($str, array(
        "<br>" => "\n",
        "<" => "&lt;",
        ">" => "&gt;"
    ));
};

require_once("templates/read.php");

?>