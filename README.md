# lpp
A small python LaTeX preprocessor to keep you sane while writing LaTeX math. It allows you to write LaTeX math faster and in a more concise way. Typical example would be:

```latex
in:  The limit $\sum_i=0 ^ N+1 q_i.. p.$
out: The limit $\sum_{i=0}^{N+1} \ddot{q_i} \dot{p}$
```

All following examples only work in inline math mode!

## dotting with `\dot`, `\ddot`
Makes writing time derivations much easier. Instead of writing `$\dot{a}$`, you can just write `$a..$`. Same for `\ddot`. To be safe, use a space before and after `x..`. Then, the whole expression will be dotted. Examples:
```latex
a x. b -> a \dot{x} b
a q_i.. b -> a \ddot{q_i} b

```

Three common special cases which are processed before that:
```latex
\phi.. % -> \ddot{\phi}
\vec x.. % -> \ddot{\vec x}
\vec{abc}.. % -> \ddot{abc}
```

## Easier limits for `\sum` and `\int`
Instead of `\int_{down}^{up}`, just leave the braces and delimit everything with spaces. So:
```latex
\sum _ i=1 ^ e^2+4 -> \sum_{i=1}^{e^2+4}
```
