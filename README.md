# FileSift

FileSift is an open-source, evidence-first academic writing project. It currently contains the `verified-research-writing` Agent Skill for papers, literature reviews, systematic/scoping reviews, and experimental reports.

The skill emphasizes verifiable references, transparent evidence limits, reproducible calculations from supplied experimental data, and checks against assignment or journal requirements.

## Install the skill

Copy the [`verified-research-writing`](verified-research-writing/) folder into the target AI tool's skill directory. For Codex, the current-user path is:

```text
%USERPROFILE%\.agents\skills\verified-research-writing
```

Restart or open a fresh AI session if the skill does not appear. Other AI tools must support Agent Skills or a compatible `SKILL.md` format.

## CNKI access

FileSift does not bundle a CNKI connector or credentials. It can use a CNKI MCP server only after that server is installed and exposed to the AI host, or use browser-assisted search when the host provides browser control and the user is authorized. It must not bypass login, CAPTCHA, subscription, or content-use restrictions. See [`mcp-integration.md`](verified-research-writing/references/mcp-integration.md).

## Tools and checks

The skill includes public-index search and a Crossref bibliography metadata checker. The latter accepts RIS/EndNote, JSON, or CSV and does not assess whether a source supports a claim.

Run checks from the repository root:

```text
python verified-research-writing/scripts/validate_project.py
python -m unittest discover -s verified-research-writing/tests -v
```

GitHub Actions runs these checks on pushes and pull requests. See the skill's [README](verified-research-writing/README.md) for usage and limitations.

## License

MIT. See [LICENSE](LICENSE).

---

# FileSift（中文）

FileSift 是一个面向学术写作的开源项目，当前包含 `verified-research-writing` skill，适用于论文、文献综述、系统综述、范围综述和实验报告。

它强调核验参考文献、标明证据与全文访问边界、只根据用户提供的真实实验数据进行计算，并对照课程评分标准或期刊要求检查文稿。

## 安装

将 [`verified-research-writing`](verified-research-writing/) 文件夹复制到 AI 工具的 skills 目录。Codex 当前用户目录为：

```text
%USERPROFILE%\.agents\skills\verified-research-writing
```

其他 AI 需要支持 Agent Skills 或兼容 `SKILL.md` 的格式。知网需要宿主已配置授权 MCP 服务，或宿主提供浏览器操作和用户授权会话；本项目不包含知网连接器或账号。

本地检查命令和使用限制请见上方及 skill 内的 README。项目采用 MIT 许可证。
