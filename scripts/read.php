<?php

require __DIR__ . "/../config.php";

$title_id = filter_var($_GET["titleId"] ?? 0, FILTER_VALIDATE_INT);
$subtitle_id = filter_var($_GET["subtitleId"] ?? 0, FILTER_VALIDATE_INT);

if ($title_id < 1 || $subtitle_id < 1) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$db = new SQLite3(DB_PATH, SQLITE3_OPEN_READONLY);

$subtitle = $db->querySingle("
    SELECT date, image_cnt, name, comment
    FROM subtitle
    WHERE title_id = $title_id
    AND id = $subtitle_id;
", true);

if (empty($subtitle)) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$subtitle_cnt = $db->querySingle("
    SELECT MAX(id)
    FROM subtitle
    WHERE title_id = $title_id;
");

require __DIR__ . "/../templates/read.php";