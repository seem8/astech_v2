% include('header', title='Astech: easier MegaMek administration')

<form action="/login" method="post">
<table border="0">
  <tr width=300px>
    <td width=150px>Username:</td>
    <td width=150px><input name="username" type="text"></td>
  </tr>
  <tr width=300px>
    <td width=150px>Password:</td>
    <td width=150px><input name="password" type="password"></td>
  </tr>
  <tr width=300px>
    <td width=150px>&nbsp;</td>
    <td width=150px><input value="Login" type="submit"></td>
  </tr>
</table>
</form>

% # comment those two lines on production
<p>Default login: <em>somelogin</em>,
default password: <em>somepassword</em></p>

% # badpass is a cookie set when wrong login and/or password were submitted
% if badpassword:
  <p class="error">Wrong login, or password.</p>
% end

<p><em>Astech page is storing cookie files on your device.</em></p>

% # contact information and closing html tags
% include('footer')

