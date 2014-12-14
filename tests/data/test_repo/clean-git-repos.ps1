1..2 |
    % { "_ignore\\git-repo$_" } |
    ? { Test-Path $_ } |
    % { Remove-Item -Recurse -Force $_ }
    