% include('header', title='Astech: easier MegaMek administration')

% # tutorial messages if veteran cookie is absent
% if not veteran:
  <div id="tutorial">
    <strong>Tutorial:</strong><br>
    This are Astech options. You can change Your password (and
    You have to change it at lease once). Please use only latin
    characters (A-Z, a-z).
    <hr>
    Below that You can show, or hide tutorial messages.
  </div>
% end

<form action="/options" method="post">
<table border="0">
  <tr width=300px>
    <td width=150px>Old password:</td>
    <td width=150px><input name="old" type="password"></td>
  </tr>
  <tr width=300px>
    <td width=150px>New password:</td>
    <td width=150px><input name="new1" type="password"></td>
  </tr>
  <tr width=300px>
    <td width=150px>Confirm new password:</td>
    <td width=150px><input name="new2" type="password"></td>
  </tr>
  <tr width=300px>
    <td width=150px>&nbsp;</td>
    <td width=150px><input value="change password" type="submit"></td>
  </tr>
</table>
</form>

% # various possible errors during password change 
<p class="error">
% if noalpha:
  Please use only latin characters (A-Z, a-z).<br />
% end

% if badoldpassword:
  Wrong old password.<br />
% end

% if shortnewpassword:
  Please choose longer password.<br />
% end

% if longnewpassword:
  Please choose shorter password.<br />
% end

% if mispatchpassword:
  New password and confirmation doesn't match.<br />
% end
</p>

<table>
  <tr width=200px>
    <td width=100px>
      <strong>Tutorial:</strong>
    </td>
    <td width=100px>
    % if veteran:
      <a href="/green">enable</a>
    % end

    % if not veteran:
      <a href="/veteran">disable</a>
    % end
    </td>
  </tr>
</table>

% # contact information and closing html tags
% include('footer')
