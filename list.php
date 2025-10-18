<?php

$title_id = filter_var($_GET["titleId"] ?? "", FILTER_VALIDATE_INT);
$page = filter_var($_GET["page"] ?? 1, FILTER_VALIDATE_INT);

if ($title_id === false || $page === false || $page < 1) {
    http_response_code(400);
    die("query does not exist");
}

$db = new SQLite3("db.sqlite", SQLITE3_OPEN_READONLY);

$result = $db->query("
    SELECT MAX(id) AS cnt  -- dense
    FROM subtitle
    WHERE title_id = $title_id;
");
$subtitle_cnt = $result->fetchArray(SQLITE3_ASSOC);
$page_max = ceil($subtitle_cnt["cnt"] / 20);

if ($page_max < $page) {
    $db->close();
    http_response_code(400);
    die("query does not exist");
}

$result = $db->query("
    SELECT name, synopsis, banner
    FROM title
    WHERE id = $title_id;
");
$title = $result->fetchArray(SQLITE3_ASSOC);

$subtitles = [];
$result = $db->query("
    SELECT id, name, date, thumbnail
    FROM subtitle
    WHERE title_id = $title_id AND id > " . ($page * 20 - 20) . "
    ORDER BY id
    LIMIT 20;
");
while ($subtitle = $result->fetchArray(SQLITE3_ASSOC))
    $subtitles[] = $subtitle;

$artists = [];
$result = $db->query("
    SELECT ta.role, a.name, a.profile
    FROM title_artist AS ta
    JOIN artist AS a ON a.id = ta.artist_id
    WHERE ta.title_id = $title_id;
");
while ($artist = $result->fetchArray(SQLITE3_ASSOC))
    $artists[] = $artist;

function html_esc($str) {
    return strtr($str, array(
        "<br>" => "\n",
        "<" => "&lt;",
        ">" => "&gt;"
	));
};

require_once("templates/list.php");

?>