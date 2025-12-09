# OhMyClaude PyPI 发布手册

本文档详细记录将 OhMyClaude 发布到 PyPI 的完整步骤。

---

## 1. 前置条件检查

### 1.1 本地环境验证

```bash
# 确保在项目根目录
cd /Users/jialinli/ohmyclaude

# 检查 Python 版本 (需要 3.10+)
python3 --version

# 检查必要文件是否存在
ls -la LICENSE pyproject.toml README.md CHANGELOG.md install.sh

# 检查 GitHub Actions 配置
ls -la .github/workflows/
```

### 1.2 运行测试确保代码正常

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行完整测试套件
uv run pytest tests/ -v

# 预期结果: 157 tests passed
```

### 1.3 检查版本号

```bash
# 查看 pyproject.toml 中的版本
grep "version" pyproject.toml

# 确认版本号为 1.0.0
```

---

## 2. PyPI 账号配置

### 2.1 注册 PyPI 账号

1. 访问 https://pypi.org/account/register/
2. 填写用户名、邮箱、密码
3. 验证邮箱地址

### 2.2 启用双因素认证 (推荐)

1. 登录后访问 https://pypi.org/manage/account/
2. 点击 "Add 2FA with authentication application"
3. 使用 Google Authenticator 或类似应用扫描二维码
4. 输入验证码完成设置

### 2.3 创建项目 (首次发布)

> **注意**: 首次发布需要先在 PyPI 上创建项目名称占位

**方式一: 通过 twine 手动上传** (推荐首次使用)

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 上传到 PyPI (会提示输入用户名密码)
twine upload dist/*

# 或者使用 API Token
twine upload dist/* -u __token__ -p pypi-xxxx
```

**方式二: 直接配置 Trusted Publishing** (需项目已存在)

如果项目名称 `ohmyclaude` 已被占用，需要选择其他名称并修改 `pyproject.toml`。

---

## 3. 配置 Trusted Publishing (OIDC)

Trusted Publishing 允许 GitHub Actions 无需 API Token 即可发布到 PyPI。

### 3.1 访问项目发布设置

1. 登录 PyPI: https://pypi.org/
2. 进入项目管理页面: https://pypi.org/manage/project/ohmyclaude/
3. 点击左侧 **"Publishing"** 选项

### 3.2 添加 GitHub Actions 发布者

在 "Add a new pending publisher" 部分填写:

| 字段 | 值 |
|------|-----|
| **Owner** | `ohmyclaude` (GitHub 用户名或组织名) |
| **Repository name** | `ohmyclaude` |
| **Workflow name** | `publish.yml` |
| **Environment name** | `pypi` (**必填** - workflow 依赖此配置) |

点击 **"Add"** 保存。

### 3.3 配置 GitHub Repository Environment (必填)

> **重要**: 此步骤是必需的，因为 `publish.yml` 使用 `environment: pypi` 来触发 Trusted Publishing。

1. 打开 GitHub 仓库: https://github.com/ohmyclaude/ohmyclaude
2. 进入 **Settings** → **Environments**
3. 点击 **"New environment"**
4. 输入名称: `pypi` (必须与 workflow 中的 environment 名称一致)
5. 配置保护规则 (可选但推荐):
   - Required reviewers: 添加审核人员
   - Wait timer: 设置等待时间

---

## 4. 本地构建测试

### 4.1 构建分发包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info

# 构建 sdist 和 wheel
python -m build

# 检查构建产物
ls -la dist/
# 预期输出:
# ohmyclaude-1.0.0-py3-none-any.whl
# ohmyclaude-1.0.0.tar.gz
```

### 4.2 验证包内容

```bash
# 检查包元数据
twine check dist/*

# 预期输出: PASSED
```

### 4.3 本地安装测试

```bash
# 创建临时虚拟环境测试
python -m venv /tmp/test-ohmyclaude
source /tmp/test-ohmyclaude/bin/activate

# 从本地 wheel 安装
pip install dist/ohmyclaude-1.0.0-py3-none-any.whl

# 验证安装
ohmyclaude --version
ohmyclaude --help

# 清理
deactivate
rm -rf /tmp/test-ohmyclaude
```

---

## 5. 发布到 PyPI

### 5.1 推送代码到 GitHub

```bash
# 确保所有更改已提交
git status

# 推送到 main 分支
git push origin main
```

### 5.2 创建 Release Tag

```bash
# 创建带注释的 tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"

# 推送 tag 到 GitHub
git push origin v1.0.0
```

### 5.3 监控 GitHub Actions

1. 访问 https://github.com/ohmyclaude/ohmyclaude/actions
2. 查看 "Publish to PyPI" workflow 运行状态
3. 等待所有 jobs 完成 (约 2-5 分钟)

### 5.4 检查发布结果

如果 workflow 失败，检查:
- PyPI Trusted Publishing 配置是否正确
- workflow 文件名是否与 PyPI 配置一致
- Environment 名称是否匹配

---

## 6. 发布后验证

### 6.1 验证 PyPI 页面

访问 https://pypi.org/project/ohmyclaude/ 确认:
- 版本号正确 (1.0.0)
- README 显示正常
- 元数据完整 (作者、许可证、链接)

### 6.2 测试安装

```bash
# 从 PyPI 安装
pip install ohmyclaude

# 或使用 pipx
pipx install ohmyclaude

# 验证命令
ohmyclaude --version
ohmyclaude setup --help
```

### 6.3 验证 install.sh

```bash
# 测试远程安装脚本
curl -fsSL https://raw.githubusercontent.com/ohmyclaude/ohmyclaude/main/install.sh | bash
```

### 6.4 检查 GitHub Release

访问 https://github.com/ohmyclaude/ohmyclaude/releases 确认:
- Release v1.0.0 已创建
- Release notes 自动生成
- 构建产物已附加

---

## 7. 故障排除

### 7.1 Trusted Publishing 失败

**错误**: "Unable to retrieve OIDC token"

**解决方案**:
1. 确认 PyPI 上的 workflow name 与实际文件名一致 (`publish.yml`)
2. 确认 repository owner 和 name 正确
3. 如果使用 environment，确认 GitHub 已创建对应 environment

### 7.2 包名被占用

**错误**: "The name 'ohmyclaude' is already taken"

**解决方案**:
1. 修改 `pyproject.toml` 中的 `name` 字段
2. 考虑使用 `oh-my-claude` 或 `ohmyclaude-cli` 等变体

### 7.3 版本冲突

**错误**: "File already exists"

**解决方案**:
1. 更新 `pyproject.toml` 中的版本号
2. 重新创建 tag: `git tag -d v1.0.0 && git tag v1.0.1`
3. PyPI 不允许覆盖已发布的版本

### 7.4 构建失败

**错误**: "Build failed"

**解决方案**:
```bash
# 检查构建日志
python -m build --no-isolation

# 检查 pyproject.toml 语法
pip install validate-pyproject
validate-pyproject pyproject.toml
```

---

## 8. 后续版本发布

发布新版本只需:

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 中的 version = "1.1.0"

# 2. 更新 CHANGELOG.md

# 3. 提交更改
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.1.0"

# 4. 创建新 tag
git tag -a v1.1.0 -m "Release v1.1.0"

# 5. 推送
git push origin main
git push origin v1.1.0
```

CI 会自动完成后续发布流程。

---

## 9. 快速参考

### 必要链接

| 资源 | URL |
|------|-----|
| PyPI 项目页 | https://pypi.org/project/ohmyclaude/ |
| PyPI 管理页 | https://pypi.org/manage/project/ohmyclaude/ |
| GitHub 仓库 | https://github.com/ohmyclaude/ohmyclaude |
| GitHub Actions | https://github.com/ohmyclaude/ohmyclaude/actions |
| GitHub Releases | https://github.com/ohmyclaude/ohmyclaude/releases |

### 关键命令速查

```bash
# 构建
python -m build

# 检查
twine check dist/*

# 本地测试安装
pip install dist/*.whl

# 创建 tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 验证安装
pip install ohmyclaude && ohmyclaude --version
```

---

*文档版本: 1.0.0 | 最后更新: 2024-12-08*
