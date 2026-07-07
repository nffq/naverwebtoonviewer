<?php

require __DIR__ . "/../config.php";

$title_id = filter_var($_GET["titleId"] ?? 0, FILTER_VALIDATE_INT);
$page = filter_var($_GET["page"] ?? 1, FILTER_VALIDATE_INT);

if ($title_id < 1 || $page < 1) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$db = new SQLite3(DB_PATH, SQLITE3_OPEN_READONLY);

$subtitles = [];
$result = $db->query("
    SELECT id, name, date
    FROM subtitle
    WHERE title_id = $title_id
    AND id > " . (($page - 1) * SUBTITLE_CNT) . "
    ORDER BY id
    LIMIT " . SUBTITLE_CNT . ";
");
while ($subtitle = $result->fetchArray())
    $subtitles[] = $subtitle;

if (empty($subtitles)) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$title = $db->querySingle("
    SELECT name, synopsis
    FROM title
    WHERE id = $title_id;
", true);

$artists = [];
$result = $db->query("
    SELECT ta.role, a.name, a.profile
    FROM title_artist AS ta
    JOIN artist AS a ON a.id = ta.artist_id
    WHERE ta.title_id = $title_id;
");
while ($artist = $result->fetchArray())
    $artists[] = $artist;

$subtitle_cnt = $db->querySingle("
    SELECT MAX(id)
    FROM subtitle
    WHERE title_id = $title_id;
");
$page_max = ceil($subtitle_cnt / SUBTITLE_CNT);

require __DIR__ . "/../templates/list.php";