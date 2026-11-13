# dotfiles

个人 Arch Linux 终端配置，由 chezmoi 管理。系统软件用 pacman 安装；Node.js 工具链由 Vite+（`vp`）管理，DSH 由 pm2 后台运行；Oh My Zsh 与 fzf-tab 由 chezmoi externals 拉取。

## 安装与恢复

### 1. 安装 Arch Linux 软件

```sh
sudo pacman -Syu --needed chezmoi git zsh fzf zoxide zellij zsh-syntax-highlighting vim python github-cli
```

### 2. 应用 chezmoi 配置

```sh
chezmoi init https://github.com/qiudeng7/dotfiles.git
chezmoi apply
```

你可能需要调整 [Git 配置](dot_gitconfig) 中的姓名、邮箱；首次 chezmoi apply 会联网克隆 Oh My Zsh 与 fzf-tab，已有对应 Git 仓库时执行 fast-forward-only 更新。

### 3. 安装 vp，node，pm2 和 DSH

我通过 [Vite+](https://viteplus.dev/guide/global-cli)（`vp`）管理 node，安装vp、node、pm2和dsh

```sh
curl -fsSL https://vite.plus | bash

vp env install 26      # 安装 Node.js 26
vp env default 26      # 设为默认版本
vp install -g pm2 @deepseek-ai/dsh

pm2 start ~/.config/pm2/startup.config.mjs
pm2 save      # 保存进程列表，开机由 pm2 恢复
pm2 startup   # 按提示执行它打印的 sudo 命令
```

### 4. 配置本机密钥

`chezmoi apply` 后会生成 `~/.secrets.env.example` 将其重命名为 `~/.secrets.env`，本 dotfiles 的某些地方会依赖这些 secret.


### 5. 设置默认 shell

```sh
chsh -s /usr/bin/zsh
```

## 其他

中文词表的来源与授权见 [第三方声明](THIRD-PARTY-NOTICES.md)。
