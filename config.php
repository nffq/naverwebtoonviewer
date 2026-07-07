<?php

define("DB_PATH", __DIR__ . "/db.sqlite");
define("TITLE_CNT", 10);
define("SUBTITLE_CNT", 20);

function html_esc($str) {
    return strtr($str, array(
        "<br>" => "\n",
        "<" => "&lt;",
        ">" => "&gt;"
    ));
};