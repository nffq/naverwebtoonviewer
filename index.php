<?php

$page = filter_var($_GET["page"] ?? 1, FILTER_VALIDATE_INT);

if ($page === false || $page < 1) {
    http_response_code(400);
    die("query does not exist");
}

$db = new SQLite3("db.sqlite", SQLITE3_OPEN_READONLY);

$result = $db->query("
    SELECT MAX(rowid) AS cnt
    FROM title;
");
$title_cnt = $result->fetchArray(SQLITE3_ASSOC);
$page_max = ceil($title_cnt["cnt"] / 10);

if ($page_max < $page) {
    $db->close();
    http_response_code(400);
    die("query does not exist");
}

$titles = [];
$result = $db->query("
    SELECT id, name, thumbnail
    FROM title
    WHERE rowid > " . ($page * 10 - 10) . "
    ORDER BY rowid
    LIMIT 10;
");
while ($title = $result->fetchArray(SQLITE3_ASSOC))
    $titles[] = $title;

$artists = [];
$result = $db->query("
    SELECT ta.title_id, ta.role, a.name, a.profile
    FROM title_artist AS ta
    JOIN artist AS a ON a.id = ta.artist_id
    WHERE ta.title_id IN (" . implode(",", array_column($titles, "id")) . ");
");
while ($artist = $result->fetchArray(SQLITE3_ASSOC))
    $artists[$artist["title_id"]][] = $artist;

function html_esc($str) {
    return strtr($str, array(
        "<br>" => "\n",
        "<" => "&lt;",
        ">" => "&gt;"
	));
};

require_once("templates/index.php");

?>