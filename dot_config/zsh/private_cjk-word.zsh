# cjk-word：让 zsh 的行编辑认识中日韩文字。
#
# zsh 把每个 CJK 字符都当成词字符，内置的 backward-kill-word 会把一整段中文
# 一起吃掉。这几个 widget 自己扫缓冲区：中文按词表做最大匹配，ASCII 的连续
# 字母、数字、下划线仍然算一个词；词表里没有的字按单字退格。
#
# 分两层：_cjk-word-start / _cjk-word-end 只负责算出一个边界下标，下面的
# widget 再把下标映射成具体动作。删除复用内置的 .kill-region，所以 kill ring
# （Ctrl+Y）和 undo（Ctrl+_）都保持原生行为。

typeset -g _cjk_dir=${${(%):-%x}:A:h}

# 词表惰性载入：只有真按到中文才 source，纯英文会话不受影响。
_cjk-word-load() {
  [[ -n $_cjk_loaded ]] && return
  typeset -g _cjk_loaded=1
  typeset -gA _cjk_dict=()
  [[ -r $_cjk_dir/cjk-words.zsh ]] && source "$_cjk_dir/cjk-words.zsh"
  # 自定义词表：一行一个词，# 开头是注释，空行忽略。
  local w
  if [[ -r $_cjk_dir/cjk-words.local ]]; then
    while IFS= read -r w; do
      [[ -n $w && $w != '#'* ]] && _cjk_dict[$w]=1
    done < "$_cjk_dir/cjk-words.local"
  fi
}

_cjk-word-start() {   # REPLY = 光标左边那个词的起始下标
  local -i i=$CURSOR len m=0
  local cand
  while (( i > 0 )) && [[ ${BUFFER[i]} == [[:space:]] ]]; do (( i-- )); done
  if (( i > 0 )); then
    if [[ ${BUFFER[i]} == [A-Za-z0-9_] ]]; then
      while (( i > 0 )) && [[ ${BUFFER[i]} == [A-Za-z0-9_] ]]; do (( i-- )); done
    else
      _cjk-word-load
      # 反向最大匹配：从光标往左试 4/3/2 字，都不中就退一个单字。
      for len in 4 3 2; do
        (( i >= len )) || continue
        cand=${BUFFER[i-len+1,i]}
        if (( ${+_cjk_dict[$cand]} )); then (( i -= len )); m=1; break; fi
      done
      (( m )) || (( i-- ))
    fi
  fi
  REPLY=$i
}

_cjk-word-end() {     # REPLY = 光标右边那个词的结束下标
  local -i n=${#BUFFER} i=$CURSOR len m=0
  local cand
  while (( i < n )) && [[ ${BUFFER[i+1]} == [[:space:]] ]]; do (( i++ )); done
  if (( i < n )); then
    if [[ ${BUFFER[i+1]} == [A-Za-z0-9_] ]]; then
      while (( i < n )) && [[ ${BUFFER[i+1]} == [A-Za-z0-9_] ]]; do (( i++ )); done
    else
      _cjk-word-load
      for len in 4 3 2; do
        (( i + len <= n )) || continue
        cand=${BUFFER[i+1,i+len]}
        if (( ${+_cjk_dict[$cand]} )); then (( i += len )); m=1; break; fi
      done
      (( m )) || (( i++ ))
    fi
  fi
  REPLY=$i
}

_cjk-backward-kill-word() { _cjk-word-start; MARK=$REPLY; zle .kill-region }

_cjk-kill-word() {
  _cjk-word-end
  (( REPLY == CURSOR )) && return
  MARK=$CURSOR
  CURSOR=$REPLY
  zle .kill-region
}

_cjk-backward-word() { _cjk-word-start; CURSOR=$REPLY }
_cjk-forward-word()  { _cjk-word-end;   CURSOR=$REPLY }

zle -N _cjk-backward-kill-word
zle -N _cjk-kill-word
zle -N _cjk-backward-word
zle -N _cjk-forward-word

bindkey '^H'           _cjk-backward-kill-word   # Ctrl+Backspace
bindkey '^[[127;5u'    _cjk-backward-kill-word   # 同上，kitty / CSI-u 编码
bindkey '^[[27;5;127~' _cjk-backward-kill-word   # 同上，rxvt 风格编码
bindkey '^W'           _cjk-backward-kill-word   # Ctrl+W，不接管还是会整段吞中文
bindkey '^[^?'         _cjk-backward-kill-word   # Alt+Backspace
bindkey '^[[1;5D'      _cjk-backward-word        # Ctrl+←
bindkey '^[[1;5C'      _cjk-forward-word         # Ctrl+→
bindkey '^[[3;5~'      _cjk-kill-word            # Ctrl+Delete
