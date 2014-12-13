Write-Host
Write-Host 'Building Mercurial test repositories...'
Write-Host


.\clean-hg-repos.ps1


Write-Host
Write-Host '===== hg-repo1 ====='
# a repository without any commits
[void](mkdir _ignore\hg-repo1)
cd _ignore\hg-repo1

hg init
cd ..

Write-Host
Write-Host '===== hg-repo2 ====='
# a repository with commits
[void](mkdir hg-repo2)
cd hg-repo2

hg init
hg import -d "1418483588 -3600" -u hkmshb -m "First lines" ..\..\lyrics-0.patch
cd ../..

Write-Host
Write-Host 'Finished. Make sure there are no error messages above.'
