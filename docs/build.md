# GRPCLess 构建生产模式

## 生产模式下依赖

生产模式下依赖仅需要安装 `grpclib`，无需安装 `grpcless`。你也可以安装 `uvloop`。

## 构建生产模式

```bash
grpcless build main.py:app ...sources
```

其中 `main.py:app` 为你的应用入口。`...sources` 为你的源文件。

例如：

```bash
grpcless build main.py:app main.py src
```

可使用 `dist` 指定输出路径。默认为 `dist` 文件夹。

## 产物

产物文件夹默认有以下结构：

```text
dist
├── grpcless  生成的用于生产模式版本的 grpcless
│   └── ...
├── xxx_pb2.py
├── xxx_grpc.py
└── 你的源文件
```

## 注意事项

- 默认生产模式去除了大部分动态创建类与函数的代码，但部分 `getattr` 的使用仍旧无法避免。
- 默认复制到生成目录中的编译好的 protobuf 不带有 mypy 类型注解文件。
- 生产模式部分行为可能与调试模式不同。
- 生产模式下不会注册指定的 `pb` 目录到导入列表中，也不会注册导入拦截器。
- build 时会自动删除原有的整个 dist 文件夹。
