<!DOCTYPE html>
<html>
<head>
  <title>Astech - {{title}}</title>
  <meta name="author" content="Łukasz Posadowski">
  <meta name="keywords" content="battletech, megamek, astech">
  <meta name="description" content="Play Battletech online easly. Web frontend for MegaMek server.">
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <link rel="stylesheet" href="/style" type="text/css">
</head>
<body>

% # header image and title
<div id="header">
  <img src="/image/astech_logo.png">

  % # username is a cookie with login
  % if username:
    <p class="login">You are logged as {{username}}.</font></p>
  % end
</div>

% # main menu
% if username:
  <div class="nav">
    <p class="menu">
    <a href="/">server status</a> | 
    <a href="/files">user files</a> | 
    <a href="/options">options</a> | 
    <a href="/logout">log out</a>
  </div>
% end


