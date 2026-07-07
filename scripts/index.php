<?php

require __DIR__ . "/../config.php";

$page = filter_var($_GET["page"] ?? 1, FILTER_VALIDATE_INT);

if ($page < 1) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$db = new SQLite3(DB_PATH, SQLITE3_OPEN_READONLY);

$titles = [];
$result = $db->query("
    SELECT id, name
    FROM title
    WHERE rowid > " . (($page - 1) * TITLE_CNT) . "
    ORDER BY rowid
    LIMIT " . TITLE_CNT . ";
");
while ($title = $result->fetchArray())
    $titles[] = $title;

if (empty($titles)) {
    require __DIR__ . "/../templates/error.php";
    exit;
}

$artists = [];
$result = $db->query("
    SELECT ta.title_id, ta.role, a.name, a.profile
    FROM title_artist AS ta
    JOIN artist AS a ON a.id = ta.artist_id
    WHERE ta.title_id IN (" . implode(",", array_column($titles, "id")) . ");
");
while ($artist = $result->fetchArray())
    $artists[$artist["title_id"]][] = $artist;

$title_cnt = $db->querySingle("
    SELECT MAX(rowid)
    FROM title;
");
$page_max = ceil($title_cnt / TITLE_CNT);

require __DIR__ . "/../templates/index.php";