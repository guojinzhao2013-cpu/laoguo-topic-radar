# 老郭的数字生活｜选题雷达

这是一个可直接部署到 GitHub Pages 的静态看板。页面打开时会优先读取仓库根目录的 `topics.json`，没有该文件或数据不可用时，会自动使用 `index.html` 内置的 30 条基准选题。

## 第一次部署

1. 在 GitHub 新建一个空仓库，例如 `laoguo-topic-radar`。
2. 在本目录执行：

   ```bash
   git add .
   git commit -m "feat: add topic radar dashboard"
   git remote add origin https://github.com/你的用户名/laoguo-topic-radar.git
   git push -u origin main
   ```

3. 打开 GitHub 仓库的 **Settings → Pages**。
4. 在 **Build and deployment** 中选择 **Deploy from a branch**，分支选择 `main`，目录选择 `/ (root)`，点击 **Save**。
5. 等待一两分钟，GitHub 会显示访问地址，通常是 `https://你的用户名.github.io/laoguo-topic-radar/`。

## 自动更新

`.github/workflows/update_radar.yml` 每天 UTC 01:17（北京时间 09:17）运行一次，也可以在仓库的 **Actions → 更新选题雷达 → Run workflow** 手动运行。

脚本会从 HTML 中提取已审核的基准选题，并尝试读取公开 RSS。RSS 暂时不可用时不会清空数据。若要指定自己的 RSS 地址，可在 Actions 中增加仓库变量 `TOPIC_RADAR_RSS_URL`；未配置时使用 Hacker News RSS 作为示例来源。

## 本地检查

```bash
python3 -m pip install -r scripts/requirements.txt
python3 -m py_compile scripts/update_topics.py
python3 scripts/update_topics.py
```

`topics.json` 是自动生成文件，提交到 GitHub 后前端就能直接读取。
