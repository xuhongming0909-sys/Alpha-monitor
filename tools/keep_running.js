const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const projectRoot = path.resolve(__dirname, '..');
const logDir = path.join(projectRoot, 'runtime_logs');
const runnerLog = path.join(logDir, 'watcher.log');
const stdoutLog = path.join(logDir, 'server_stdout.log');
const stderrLog = path.join(logDir, 'server_stderr.log');
const runnerPidFile = path.join(logDir, 'watcher.pid');
const appPidFile = path.join(logDir, 'server.pid');

fs.mkdirSync(logDir, { recursive: true });
const RESTART_DELAY_MS = 5000;

function timestamp() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

function writeRunnerLog(message) {
  fs.appendFileSync(runnerLog, `[${timestamp()}] [runner] ${message}\n`);
}

function writePid(file, pid) {
  const tempFile = `${file}.tmp`;
  fs.writeFileSync(tempFile, String(pid));
  fs.renameSync(tempFile, file);
}

function removeFile(file) {
  try {
    fs.unlinkSync(file);
  } catch (_) {}
}

let child = null;
let stopping = false;
let restartTimer = null;
let restartCount = 0;

function clearRestartTimer() {
  if (!restartTimer) return;
  clearTimeout(restartTimer);
  restartTimer = null;
}

function cleanupAndExit(code) {
  clearRestartTimer();
  removeFile(appPidFile);
  removeFile(runnerPidFile);
  process.exit(code);
}

function stopChildAndExit(signal) {
  stopping = true;
  clearRestartTimer();
  writeRunnerLog(`runner received ${signal}`);
  if (child && !child.killed) {
    child.kill('SIGTERM');
    setTimeout(() => {
      if (child && !child.killed) {
        child.kill('SIGKILL');
      }
    }, 3000).unref();
    return;
  }
  cleanupAndExit(0);
}

function startChild() {
  const out = fs.openSync(stdoutLog, 'a');
  const err = fs.openSync(stderrLog, 'a');
  child = spawn(process.execPath, ['start_server.js'], {
    cwd: projectRoot,
    stdio: ['ignore', out, err]
  });
  fs.closeSync(out);
  fs.closeSync(err);

  writePid(appPidFile, child.pid);
  writeRunnerLog(`node started pid=${child.pid} restartCount=${restartCount}`);

  child.on('exit', (code, signal) => {
    removeFile(appPidFile);
    writeRunnerLog(`node exited pid=${child.pid} code=${code ?? 'null'} signal=${signal ?? 'null'}`);
    child = null;

    if (stopping || code === 0) {
      writeRunnerLog('watcher stopped after clean exit');
      cleanupAndExit(0);
      return;
    }

    restartCount += 1;
    clearRestartTimer();
    writeRunnerLog(`scheduling restart in ${RESTART_DELAY_MS}ms attempt=${restartCount}`);
    restartTimer = setTimeout(() => {
      restartTimer = null;
      writeRunnerLog('restarting node after unexpected exit');
      startChild();
    }, RESTART_DELAY_MS);
  });
}

process.on('SIGINT', () => stopChildAndExit('SIGINT'));
process.on('SIGTERM', () => stopChildAndExit('SIGTERM'));
process.on('uncaughtException', (error) => {
  writeRunnerLog(`runner uncaughtException: ${error.stack || error.message || String(error)}`);
  stopChildAndExit('uncaughtException');
});
process.on('unhandledRejection', (reason) => {
  writeRunnerLog(`runner unhandledRejection: ${reason && reason.stack ? reason.stack : String(reason)}`);
  stopChildAndExit('unhandledRejection');
});

writePid(runnerPidFile, process.pid);
writeRunnerLog('watcher started');
startChild();


