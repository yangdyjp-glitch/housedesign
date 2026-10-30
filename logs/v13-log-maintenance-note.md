# 本轮读取日志说明

在v13接入核对时，曾以`activate_model_v07.py --inspect-only`执行旧版只读探测。该旧入口在返回前仍会写`v07-live-state.json`与`v07-mcp-stderr.txt`，所以两份同名日志现记录v13本轮加载前的v12现场状态；不能再当作原v07会话证据。此调用没有加载或修改模型。原v07现场日志未能从交付压缩包恢复，不重构或伪造原始响应。

原v07的保存模型、`model-v07-readback.json`、`v07-live-operator.json`、`v07-delivery-verification.json`及历史压缩包仍在。v13的接入证据独立保存为`v13-input-live-state.json`与`v13-live-state.json`，不依赖上述被替换的旧日志。
