# 会話の再開ガイド

## このプロジェクトで Claude Code を再開する手順

### 1. ターミナルを開く
Cursor のターミナル、または macOS のターミナルで:
```bash
cd ~/claudecode/notion_web_to_claudecode
```

### 2. Claude Code を起動

**前回の会話を再開したい場合:**
```bash
claude --resume
```
矢印キーで `some-draw-enrichment` を選んで Enter。

**新しい会話を始める場合:**
```bash
claude
```
CLAUDE.md が自動で読み込まれるので、プロジェクトの文脈は伝わります。

### 3. やりたいことを伝える（例）
- 「作品ページに新しい展覧会を追加して」
- 「build.py を実行して」
- 「style.css のフォントサイズを変更して」
- 「GitHub Pages にデプロイして」

## プロジェクト構成の概要
- `build.py` - Notion データから HTML を生成するスクリプト
- `CLAUDE.md` - Claude が自動で読むプロジェクトメモ
- `style.css` - サイト全体のデザイン
- `works.html` - 作品一覧ページ
- `works/` - 個別作品ページ（49ページ）
- `exhibitions/` - 展覧会ページ（16ページ）
- `images/` - すべての画像

## データの更新方法
Notion のデータを更新したら:
```bash
python3 build.py        # HTMLを再生成
python3 -m http.server 8000  # 確認
git add -A && git commit -m "更新内容" && git push  # 公開
```

## サイト URL
- https://some-draw.page
- GitHub: https://github.com/mail306/some-draw-archive
