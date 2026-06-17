<div align="center">

# Recaf MCP

> *「把 Recaf 变成 LLM 可调用的 API」*

[![Java](https://img.shields.io/badge/Java-25-ED8106)](https://adoptium.net/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB)](https://www.python.org/)
[![Recaf](https://img.shields.io/badge/Recaf-4.x-2D9CDB)](https://www.coley.software/recaf4/)
[![MCP](https://img.shields.io/badge/MCP-HTTP-8B5CF6)](https://modelcontextprotocol.io/)
[![QQ Group](https://img.shields.io/badge/QQ%20Group-Join-0099FF?logo=tencent-qq&logoColor=white)](https://qm.qq.com/q/KWcs2UBtYK)

<br>

[English](README.md)

<br>

**Recaf 4 MCP 桥接工具 — 通过 MCP 协议远程操作 Recaf 工作区进行 JVM 字节码分析与修改。**

<br>

Java 插件运行在 Recaf 内部，暴露本地 HTTP API；Python MCP 服务器将 API 转为 MCP 工具供 LLM 客户端调用。

<br>

[工具列表](#工具列表) · [快速开始](#快速开始) · [字节码编辑](#字节码编辑) · [安装插件](#安装插件)

</div>

---

## 工具列表

### 工作区
`get_workspace_info` `open_workspace` `close_workspace` `add_supporting_resource` `list_supporting_resources` `fetch_current_class` `get_selected_text`

### 类
`get_all_classes` `get_class_info` `get_class_source` `get_bytecode_of_class` `get_methods_of_class` `get_fields_of_class` `get_inner_classes` `get_annotations_of_class` `get_raw_class_bytes`

### 方法
`get_method_by_name` `get_method_bytecode` `get_method_info`

### 搜索
`search_classes_by_name` `search_members_by_name` `search_strings` `search_numbers` `search_instructions`

### 交叉引用
`get_xrefs_to_class` `get_xrefs_to_method` `get_xrefs_to_field` `get_callers_of_method` `get_callees_of_method` `get_overrides_of_method`

### 重命名
`rename_class` `rename_method` `rename_field` `rename_package` `rename_local_variable` `apply_mappings`

### 反编译器
`list_decompilers` `set_active_decompiler` `decompile_class_with`

### 继承
`get_superclasses` `get_interfaces` `get_direct_subclasses` `get_all_subclasses` `get_implementors`

### 资源与导出
`get_all_file_names` `get_file_content` `get_manifest` `get_strings_from_resources` `export_workspace` `get_modified_classes` `revert_class`

---

## 字节码编辑

支持完整的字节码读写：指令级修改、JASM 文本汇编、访问标志编辑、方法/字段增删、try-catch 块编辑、类字节替换、工作区导出。

### 指令操作
`list_method_instructions` `get_method_bytecode` `replace_instruction` `insert_instruction` `remove_instruction`

### 方法体
`assemble_method` `replace_method_body`

### 访问标志
`edit_class_access` `edit_method_access` `edit_field_access`

### 方法/字段 CRUD
`add_method` `remove_method` `add_field` `remove_field`

### 其他
`set_try_catch_blocks` `replace_class_bytes` `save_workspace`

---

## 环境要求

- Java 25
- Python 3.10+
- `recaf.jar`

## 快速开始

### 1. 提供 recaf.jar

构建按以下顺序查找 Recaf：

1. 环境变量 `RECAF_JAR`
2. `libs/recaf.jar`
3. `../recaf/recaf.jar`

```powershell
$env:RECAF_JAR="D:\deobf\recaf\recaf.jar"
```

### 2. 构建插件

```powershell
.\gradlew.bat jar
```

输出：`build/libs/recaf-mcp-plugin-0.1.0.jar`

### 3. 安装插件

将 jar 复制到 Recaf 插件缓存目录 `%APPDATA%/Recaf/plugins/`，启动 Recaf。

加载成功后日志显示：

```
Recaf MCP plugin listening on http://127.0.0.1:8750
```

### 4. 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

### 5. 启动 MCP 服务器

```powershell
python recaf_mcp_server.py --http --port 8751
```

或使用启动脚本：

```powershell
.\start_recaf_mcp_http.ps1
```

---

## MCP 配置

```json
{
  "mcpServers": {
    "recaf-mcp": {
      "url": "http://127.0.0.1:8751/mcp"
    }
  }
}
```

## 端口

| 组件 | 地址 |
|---|---|
| 插件 HTTP | `127.0.0.1:8750` |
| MCP HTTP | `127.0.0.1:8751/mcp` |

健康检查：

```powershell
Invoke-WebRequest http://127.0.0.1:8750/health
```

---

## 仓库结构

```text
.
├── src/                  # Java 插件源码
├── mcp-server/           # Python MCP 服务端
├── libs/                 # recaf.jar 存放处
├── recaf_mcp_server.py   # MCP 服务器入口
├── requirements.txt      # Python 依赖
├── .mcp.json             # 项目 MCP 配置
└── README.md
```

---

## 安全警告

以下方式会暴露 MCP 服务器在公网且无认证：

```powershell
python recaf_mcp_server.py --http --host 0.0.0.0
```

默认使用 localhost，或置于防火墙/VPN 之后。

---

<p align="center">
  <em>LLM 客户端 -> MCP 服务器 -> Recaf 插件 -> Recaf 工作区</em>
</p>
