// pm2 进程配置（ESM）。新增后台服务时在 apps 中追加条目，
// 改完执行 `pm2 start ~/.config/pm2/startup.config.mjs` 与 `pm2 save`。
//
// pm2 用 require() 读取配置文件（依赖 Node 的 require(ESM) 支持），所以这里用
// 命名导出 `apps`；写成 `export default` 会报 "No script path"。
import os from 'node:os';
import path from 'node:path';

const home = os.homedir();
// Vite+ 维护的全局 bin（dsh 的 shim 在这里），不要写死 Node.js 版本目录。
const vpBin = path.join(home, '.local/share/vite-plus/bin');

export const apps = [
  {
    name: 'dsh',
    script: path.join(vpBin, 'dsh'),
    args: 'web --no-open',
    cwd: home,
    env: {
      PATH: [vpBin, process.env.PATH].filter(Boolean).join(path.delimiter),
    },
  },
];
