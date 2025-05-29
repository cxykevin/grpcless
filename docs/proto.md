# GRPCLess Proto 对象

Proto 对象用于自动引入、编译、处理导入 .proto 文件。

一个项目请只包含一个 Proto 对象。在一个 Proto 对象中可以一次性引入多个 .proto 文件。

## 引入 Proto 对象

```python
proto = grpcless.Proto("your_proto_file", proto_path = "proto")
```

## 参数

- `*proto_files`: proto 文件的文件名。文件名中的路径是相对于 `proto_path` 的，请勿在其中包含 `/`。
- `proto_path`: proto 文件的路径。一般建议为 `proto`。
- `output_dir`: 编译后的文件存放路径。默认为 `pb` 不建议赶热闹更改。
- `other_include`: 一个列表，可以存放编译时 proto 的导入路径。默认为空列表。会被传递到 `-I` 参数。

## 日志

| 类型    | 内容 | 含义 |
| COMPILE | `Compile file "[test.proto]"` | 编译文件 [test.proto] |
| PROTO   | `Access output path: "[pb]"` | 添加 [pb] 目录到模块导入列表 |
| PROTO   | `Import file: "[test.proto]"` | 导入 [test.proto] |

## 全局影响

GRPCLess 默认在被首次引用时，会注册 import 拦截器。其会拦截结尾为 `_grpc` 和 `_pb` 的模块，并将其导入推迟到 `Proto` 对象建立时。

当 Proto 对象建立时这个拦截器会被移除。
