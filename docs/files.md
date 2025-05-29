# GRPCLess 文件夹格式

一般 GRPCLess 的项目的文件格式如下：

```text
test 
├── pb 默认的编译产物文件夹
│   ├── .grpcEcache 编译缓存，记录修改时间
│   ├── xxx_pb2.py  pb编译产物-protobuf
│   ├── xxx_pb2.pyi pb编译产物-porotbuf mypy注解
│   └── xxx_grpc.py 
├── proto 放置 protobuf 文件夹
│   └── xxx.proto
└── 你的源文件
```
