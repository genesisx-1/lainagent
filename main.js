const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1480,
    height: 780,
    minWidth: 1200,
    minHeight: 600,
    resizable: true,
    title: 'Agent Office',
    backgroundColor: '#0f0f1a',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
