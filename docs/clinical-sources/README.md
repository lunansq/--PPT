# 眼科权威来源入口、资料清单与原文核验

[下载可离线打开的入口页完整包](clinical_sources_portal.zip) · [查看页面截图](portal_preview.png) · [入口页HTML](index.html) · [资料清单CSV](expanded_materials.csv) · [发布与资源入口CSV](publisher_entries.csv)

下载ZIP并解压，双击 `index.html`。界面不依赖CDN或图像生成API。原文和检索链接在浏览器打开；表单核验记录保存在当前浏览器本地，可导出JSON。此提交未部署GitHub Pages。若浏览器限制本地文件，可在解压目录运行 `python3 -m http.server 8000 --bind 127.0.0.1`，再打开 `http://127.0.0.1:8000/`。本轮浏览器验证采用本地HTTP服务。

## 本轮实际使用的GitHub项目

| 项目 | 固定读取的仓库版本 | 实际用途 |
| --- | --- | --- |
| [OpenMedAILab/EyeRAG](https://github.com/OpenMedAILab/EyeRAG/tree/ebfa93a787129a07a3caf3cf35497e1c0ab84991) | `ebfa93a787129a07a3caf3cf35497e1c0ab84991` | 扫描公开眼科资料目录，加入274条指南/共识候选元数据和来源链接；本轮未启动生成式RAG |
| [mims-harvard/ToolUniverse](https://github.com/mims-harvard/ToolUniverse/tree/7084ad507dcec0b9f95c4d38f25bde43d5577529) | 仓库声明1.5.6；`7084ad507dcec0b9f95c4d38f25bde43d5577529` | 已读取并使用 [clinical-guidelines skill](https://github.com/mims-harvard/ToolUniverse/blob/7084ad507dcec0b9f95c4d38f25bde43d5577529/skills/tooluniverse-clinical-guidelines/SKILL.md) 的检索及原文回溯流程；实际调用3个检索工具 |
| [bbylw/MGD](https://github.com/bbylw/MGD/tree/833c20be023ea4b31b267145be1db5a3dc4f2dab) | README声明4.0.0；`833c20be023ea4b31b267145be1db5a3dc4f2dab` | 导入26类指南、10类医学资源的222个导航链接，补充5个中国原文/综合机构入口 |

EyeRAG是眼科RAG项目，MGD是导航网站；这两处仓库没有 `SKILL.md`。ToolUniverse提供多个真正的skill；本轮按项目实际能力使用，未将三者都声称为已安装的Codex skill。版本号指读取时仓库声明，不等于已验证的PyPI最新发行版。

## 清单范围和版本状态

- EyeRAG候选资料274条，加上此前上传的9个已提取专题，共283条**来源记录**。记录数不等于去重后的指南数量；同名、同DOI及不同版本仍需核对。
- 全部导航入口227条，包括重复机构在不同专科的入口和医学资源链接，不等于227家独立发布机构。
- 默认突出AAO、RCOphth、EURETINA、WGA、ICO和中国发布机构、中华医学期刊原文、NICE/WHO等10个相关入口。
- 9个上传专题的年份及提取表来自已审核PDF；官网是否已有替代版仍待核验。两篇单篇研究继续与指南/共识分别标注。
- EyeRAG的Markdown是第三方候选材料，DOI和年份仅按标题/头部提取，未自动认为其为权威原文。原文PDF页码未可靠提供的内容不能直接升级为最终临床推荐。
- EyeRAG公开库不含AAO_PPP正文；未复制或重新发布该正文。

## ToolUniverse新版检索接入

本轮读取源码、真实工具schema及实际返回行为，使用 `NICE_Clinical_Guidelines_Search`、`PubMed_Guidelines_Search`、`EuropePMC_Guidelines_Search`。选定实现可在轻量导入模式运行；没有安装整个ML工具集合或自动注册MCP服务器。

新版返回以 `{status, data, metadata}` 为准，保留总命中数、实际返回数、是否截断与提示。失败不能当成0命中，返回前N条不能当作完整结果。EuropePMC指南工具按题名/摘要、出版类型筛选；普通文献检索还支持全文BODY条件，不能把“有外部免费全文链接”和“EuropePMC已索引全文”混为一谈。多智能体检索工具schema中的部分迭代/质量参数目前标为未实际生效，未把它们作为本页面的功能承诺。

以下命令在仓库根目录执行，检索脚本不属于离线入口页的运行依赖。

检索规划（不联网）：

```bash
python3 scripts/clinical_source_search.py \
  --query 'corneal transplantation' \
  --out docs/clinical-sources/retrieval_plan.json
```

执行实际ToolUniverse源码（需要可导入其选定模块的Python环境与可达的检索站点）：

```bash
python3 scripts/clinical_source_search.py \
  --query 'corneal transplantation' \
  --tooluniverse-dir /path/to/ToolUniverse \
  --execute --timeout 15 \
  --out docs/clinical-sources/retrieval_execution.json
```

当前云环境上述三来源都被网络代理拒绝，实际错误保存在 [retrieval_execution.json](retrieval_execution.json)。对10个相关机构入口的连接检查也未取得HTTP200，记录见 [official_entry_checks.json](official_entry_checks.json)。**当前已确认官网有效版本数为0**；未编造新版指南或临床建议。

## 原文核验后再进入PPT

1. 由清单/数据库定位标题和DOI，打开发布机构或其授权期刊原文。
2. 记录发布/更新日期、版本号、适用地区及是否有替代、撤回声明。发表年份不能独立证明当前有效性。
3. 核对适用人群、章节/PDF页码、建议原文、药物剂量/单位/阈值、禁忌、特殊人群、随访和推荐等级。
4. 推荐等级保留发布机构原文，不跨GRADE/专科学会制度自动折算。来源之间有不同建议时分别记录，不能任意合并。
5. 在页面填写并导出人工核验记录；未核实项目标为“未核实”或“原文未明确”。单篇研究填写研究发现，不能改写成指南推荐。
6. 此页面不会自动将候选资料、搜索摘要或人工填入的年份判为“最新版”，也不会自动改写此前医学PPT。

## 验证与来源署名

检索脚本的5项测试覆盖连接失败与0命中分离、真实空结果、截断保留、凭据脱敏、TRIP参数schema拼写。浏览器交互验证见 [portal_validation.json](portal_validation.json)，涵盖搜索筛选、核验表单、阻止GitHub候选作为机构原文、人工记录不自动确认为最新版本。

页面结构参考MGD导航，资料目录来源EyeRAG，检索工具及合同来源ToolUniverse；原始软件MIT许可文件保留在 `licenses/`。未将模型汇总内容或导航项目自身当作医学发布机构。
