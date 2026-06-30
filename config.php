<?php

define("DB_PATH", __DIR__ . "/db.sqlite");

function html_esc($str) {
    return strtr($str, array(
        "<br>" => "\n",
        "<" => "&lt;",
        ">" => "&gt;"
    ));
};