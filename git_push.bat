@echo off
rmdir /s /q .git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/xrtyolol/bot.git
git branch -M main
git push -u origin main