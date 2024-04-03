echo Building dev ui

cmd npm --prefix electron run build-backend
cmd npm --prefix electron run build-frontend-win
cmd npm --prefix electron run electron-build-win