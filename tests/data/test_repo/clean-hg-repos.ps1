1..2 |
    % { "_ignore\\hg-repo$_" } |
    ? { Test-Path $_ } |
    % { Remove-Item -Recurse -Force $_ }
    