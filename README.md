# dotfiles

个人 Arch Linux 终端配置，由 chezmoi 管理。系统软件交给 pacman 安装；Oh My Zsh 和 fzf-tab 由 chezmoi externals 拉取，不在仓库中复制第三方源码。

## 安装与恢复

### 1. 安装 Arch Linux 软件

```sh
sudo pacman -Syu --needed chezmoi git zsh fzf zoxide zellij zsh-syntax-highlighting vim python github-cli
```

- `zsh`、`fzf`、`zoxide`：交互式 Shell、模糊查找与目录跳转。
- `zellij`：终端复用；当前配置会在非 VS Code 终端中自动启动它。
- `zsh-syntax-highlighting`：从 Arch 的 `/usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh` 加载。
- `vim`：编辑器；`python`：自写 Git hooks 的运行依赖。
- `github-cli`：Git 配置中的 GitHub credential helper；软件安装不等于完成账号认证。

此仓库没有自动安装软件或执行 sudo 的脚本。

### 2. 获取并检查配置

新机器执行：

```sh
chezmoi init https://github.com/qiudeng7/dotfiles.git
chezmoi diff
```

这是个人配置，不是通用发行版。应用前检查 [Git 配置](dot_gitconfig) 中的姓名、邮箱和 hooks 路径；当前 hooks 路径是 `/home/qiudeng/.config/git/hooks`，使用其他用户名时应改成自己的路径。可用 `chezmoi edit ~/.gitconfig` 修改源文件。

`core.hooksPath` 会给所有本机 Git 仓库启用自写 hooks，包括提交信息格式 `type(domain): 中文说明` 和单文件 50 MiB 限制；不需要这些规则时，应用前删除 Git 源配置中的 `hooksPath` 行。

检查完成后：

```sh
chezmoi apply
```

首次应用会联网克隆 Oh My Zsh 与 fzf-tab。已有对应 Git 仓库时执行 fast-forward-only 更新；有本地修改或分叉导致更新失败时，先处理仓库状态，不要强制覆盖。

### 3. 配置本机密钥

完成上一步 `chezmoi apply` 后，示例已生成到 HOME。只在 `~/.secrets.env` 尚不存在时，从 [示例](private_dot_secrets.env.example) 创建它：

```sh
if [ ! -e "$HOME/.secrets.env" ]; then
  (umask 077; cp "$HOME/.secrets.env.example" "$HOME/.secrets.env")
fi
chmod 600 "$HOME/.secrets.env"
vim "$HOME/.secrets.env"
```

该文件由 zsh 当作 Shell 脚本读取，填写时使用合法的 Shell 赋值语法并给值加引号。真实密钥不纳入 chezmoi 或 Git；留空不影响普通终端使用，只会让对应的 Claude/Codex 命令提示缺少密钥。这些 CLI 本身需要另行安装。

### 4. 使用 zsh

```sh
zsh
# 可选：更改默认登录 Shell，重新登录后生效。
chsh -s /usr/bin/zsh
```

## 管理范围

- [zsh 配置](private_dot_zshrc)：Oh My Zsh、提示符、补全、快捷键、工具集成。
- [自写 zsh 插件与词表](dot_config/zsh/)：中文按词移动和删除。
- [Zellij 配置](dot_config/zellij/config.kdl)。
- [Git 配置](dot_gitconfig)、[全局忽略规则](dot_config/git/ignore)、[Git hooks](dot_config/git/hooks/)。
- [Vim 配置](dot_vimrc)：不包含自写 Vim 插件。
- [Infisical 辅助脚本](dot_local/bin/)：仅脚本，不含 CLI、登录态或密钥；使用前另行安装 Infisical CLI 并配置认证。

Clash 桥接函数使用 `/home/qiudeng/clashctl`，仓库不安装 Clash。没有安装它时不要调用 `clash*` 命令；在其他安装位置使用时需修改 [zsh 配置](private_dot_zshrc) 中的 `CLASHCTL_HOME`。

## 更新与维护

[externals 声明](.chezmoiexternal.toml) 管理两个 Git 仓库：Oh My Zsh 和 fzf-tab。它们跟随克隆时的默认分支，不固定版本；更新依赖主动运行 chezmoi，不存在后台更新任务。拉取只允许 fast-forward，不自动合并分叉。

```sh
# 明确刷新第三方插件。
chezmoi apply --refresh-externals=always ~/.oh-my-zsh ~/.oh-my-zsh/custom/plugins/fzf-tab

# 修改本机配置后，只将需要同步的文件重新加入源目录。
chezmoi add ~/.zshrc ~/.vimrc
chezmoi status

# 编辑仓库中的源文件后，先看差异再应用。
chezmoi diff
chezmoi apply
```

README 仅留在源仓库，不会复制到 HOME。不要对整个 HOME 执行递归 add，也不要把真实密钥、登录态或缓存加入仓库。

参考：[chezmoi externals 文档](https://www.chezmoi.io/reference/special-files/chezmoiexternal-format/)。中文词表的来源与授权见 [第三方声明](THIRD-PARTY-NOTICES.md)。
