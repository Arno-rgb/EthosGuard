import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import net from "node:net";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const webRoot = resolve(__dirname, "..");

const children = [];

function spawnProcess(command, args, cwd, extraEnv = {}) {
  const child =
    process.platform === "win32"
      ? spawn("cmd.exe", ["/d", "/s", "/c", [command, ...args].join(" ")], {
          cwd,
          stdio: "inherit",
          shell: false,
          env: {
            ...process.env,
            ...extraEnv,
          },
        })
      : spawn(command, args, {
          cwd,
          stdio: "inherit",
          shell: false,
          env: {
            ...process.env,
            ...extraEnv,
          },
        });
  children.push(child);
  child.on("exit", (code) => {
    if (code && code !== 0) {
      process.exitCode = code;
    }
  });
  return child;
}

function waitForPort(port, host = "127.0.0.1", timeoutMs = 60000) {
  const started = Date.now();
  return new Promise((resolvePromise, rejectPromise) => {
    const attempt = () => {
      const socket = new net.Socket();
      socket
        .once("connect", () => {
          socket.destroy();
          resolvePromise(undefined);
        })
        .once("error", () => {
          socket.destroy();
          if (Date.now() - started > timeoutMs) {
            rejectPromise(new Error(`Timed out waiting for ${host}:${port}`));
            return;
          }
          setTimeout(attempt, 500);
        })
        .connect(port, host);
    };
    attempt();
  });
}

function cleanup() {
  for (const child of children) {
    if (!child.killed) {
      child.kill();
    }
  }
}

process.on("SIGINT", cleanup);
process.on("SIGTERM", cleanup);
process.on("exit", cleanup);

async function main() {
  spawnProcess(
    "python",
    ["-m", "uvicorn", "api.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    repoRoot,
  );
  await waitForPort(8000);

  spawnProcess(
    process.platform === "win32" ? "npm.cmd" : "npm",
    ["run", "dev", "--", "--hostname", "127.0.0.1"],
    webRoot,
    { NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8000" },
  );
  await waitForPort(3000);

  await new Promise(() => {});
}

main().catch((error) => {
  console.error(error);
  cleanup();
  process.exit(1);
});
