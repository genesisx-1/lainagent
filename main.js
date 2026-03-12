const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1480,
    height: 780,
    minWidth: 1200,
    minHeight: 600,
    resizable: true,
    title: 'Kami Claw',
    backgroundColor: '#08080f',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile('welcome.html');
}

// Handle transition from welcome to main app
ipcMain.on('enter-app', () => {
  if (mainWindow) {
    mainWindow.loadFile('index.html');
  }
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
