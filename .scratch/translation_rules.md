# PCB-CoolSim 文档中译规范（SD 文档 01-10）

## 目标
项目规范要求所有 SD 文档用中文书写。把英文散文翻译为中文，保留技术标识。

## 必须保留英文（不译）
- 代码块（``` 内全部内容：示例代码、命令、shell、路径、JSON、SQL）
- 需求/用例/缺陷 ID：F1-001、TC-AUTH-001 等
- API 路径：/api/v1/...、HTTP 方法 GET/POST
- 字段名、表名、数据库标识符（project_name、room_load_result 等）
- JSON 键名、示例值、错误码常量（INVALID_CREDENTIALS）
- 技术术语：React、Django、Django REST Framework、PostgreSQL、Celery、Redis、TimescaleDB、JWT、Prometheus、Grafana、ELK、Docker、Python、pytest、Black、isort、Flake8、MyPy、Swagger、OpenAPI、WebSocket、JSON、CSV、API、PRD、SDD、ADR、psychrolib、NumPy、Pandas、Vite、Ant Design、Leaflet、Fabric.js、ECharts、ASGI、MinIO、S3、Nginx、bcrypt
- 数值、单位、百分比、版本号、URL、emoji
- 产品名 PCB-CoolSim（可保留，合规）

## 术语对照（优先使用）
Overview→概述, Architecture→架构, Strategy→策略, Plan→计划, Test→测试, Quality Gate→质量门禁, Validation→校验, Verification→验证, Requirement→需求, Coverage→覆盖率, Pass→通过, Fail→失败, Critical→严重, Major→主要, Minor→次要, Reference→参考, Purpose→目的, Scope→范围, Status→状态, Draft→草稿, Approved→已批准, Module→模块, Component→组件, Layer→层, Deployment→部署, Data Flow→数据流, Frontend→前端, Backend→后端, Database→数据库, Cache→缓存, Authentication→认证, Authorization→授权, Parameters→参数, Pagination→分页, Error Handling→错误处理, Description→说明, Required→必填, Optional→可选, Decision Makers→决策者, Context→背景, Decision→决策, Consequences→后果, Target→目标读者, Metrics→指标, Environment→环境, Infrastructure→基础设施

## 翻译规则
1. 翻译：章节标题、正文散文、表格表头与「说明/描述」中文应译的列、要点列表、引用块、图注。
2. 保持 Markdown 结构、缩进、表格对齐、行数结构不变，只替换自然语言文字。
3. 代码块内纯自然语言注释可译，代码结构/标识符不动。
4. 奥卡姆剃刀：只翻译，不新增/删除/改写技术内容，不发明字段。

## 关键技术约束（强制）
- 文件是 CRLF 换行。禁止用 Write 工具（产生 LF）。
- 读写：读 `raw=open(p,'rb').read().decode('utf-8')`；处理时把 '\r\n' 归一化为 '\n' 再做替换，最后 `open(p,'wb').write(s.replace('\n','\r\n').encode('utf-8'))`。
- 写回后 Python 校验：CRLF 正常、无 '\r\r\n' 双 CR、无孤立 LF；grep `^#+ [A-Z]` 应只剩 PCB-CoolSim / 技术缩写等合规保留项。
- 不要提交 git。
