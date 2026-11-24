# FileSift

FileSift is an open-source, evidence-first academic writing project. It currently contains the `verified-research-writing` Agent Skill for papers, literature reviews, systematic/scoping reviews, and experimental reports.

The skill emphasizes verifiable references, transparent evidence limits, reproducible calculations from supplied experimental data, and checks against assignment or journal requirements.

## Install the skill

The same [`verified-research-writing`](verified-research-writing/) folder works on Windows and Linux. It contains Markdown instructions and standard-library Python scripts, with no OS-specific binaries. The AI host must support Agent Skills or a compatible `SKILL.md` format. Install the folder into the skills directory documented by your AI tool; paths and reload steps depend on that product.

The core instructions live in `SKILL.md`. The optional `agents/openai.yaml` contains product-specific metadata that other compatible hosts can ignore. Running the included search and reference-check scripts requires Python 3.10 or newer and network access.

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

同一个 [`verified-research-writing`](verified-research-writing/) 文件夹可以用于 Windows 和 Linux。它由 Markdown 指令和 Python 标准库脚本组成，不含系统专用二进制文件。AI 工具需要支持 Agent Skills 或兼容的 `SKILL.md` 格式；请按该工具的说明把文件夹放入其 skills 目录。运行检索和引用核验脚本需要 Python 3.10 或更高版本及网络访问。

知网需要宿主已配置授权 MCP 服务，或宿主提供浏览器操作和用户授权会话；本项目不包含知网连接器或账号。

本地检查命令和使用限制请见上方及 skill 内的 README。项目采用 MIT 许可证。
