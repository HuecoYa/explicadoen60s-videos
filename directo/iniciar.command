#!/bin/bash
# Mac: doble clic para arrancar el directo
cd "$(dirname "$0")"
command -v node >/dev/null || { echo "Falta Node.js: descárgalo de https://nodejs.org (versión LTS)"; read; exit 1; }
npm install --no-audit --no-fund --loglevel=error
( sleep 3; open -na "Google Chrome" --args --app=http://localhost:3060 --window-size=540,960; open http://localhost:3060/control ) &
node servidor.js "$@"
