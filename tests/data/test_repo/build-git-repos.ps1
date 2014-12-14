Write-Host
Write-Host 'Building Git test repositories...'
Write-Host


.\clean-git-repos.ps1

$env:GIT_COMMITTER_DATE = '1418547600'


Write-Host
Write-Host '===== git-repo1 ====='
# a repository without any commits
[void](mkdir _ignore\git-repo1)
cd _ignore\git-repo1

git init
cd ..

Write-Host
Write-Host '===== git-repo2 ====='
# a repository with commits
[void](mkdir git-repo2)
cd git-repo2

git init
git config --local user.name  hkmshb
git config --local user.email hkmshb@test.com

git apply ..\..\lyrics-0.patch
git add .
git commit --date=1418547600 -a -m "First lines"

cd ../..

Write-Host
Write-Host 'Finished. Make sure there are no error messages above.'
