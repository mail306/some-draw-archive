# some-draw.page ビルドプロジェクト

## 概要
岩井美佳（染色作家）のアーカイブサイト some-draw.page の静的サイト。
Notion エクスポートデータ（CSV/Markdown/画像）から `build.py` で HTML を自動生成し、GitHub Pages でホスティング。

## ビルド手順
```bash
python3 build.py              # HTML生成 + 画像コピー
python3 -m http.server 8000   # ローカル確認 → http://localhost:8000
git add -A && git commit -m "変更内容" && git push  # デプロイ
```

## サイト構成
- `index.html` - トップページ（展覧会一覧・ニュース）
- `works.html` - 作品一覧（49点のグリッド → 各作品詳細ページへリンク）
- `works/*.html` (49ページ) - 作品詳細（メタデータ・説明・ギャラリー）
- `exhibitions/*.html` (16ページ) - 展覧会（メタデータ・フォトギャラリー・出品作品リスト）
- `style.css` - 全ページ共通CSS
- `images/` - サムネイル（w_*.jpg, ex_*.jpg）
- `images/works/` - 作品詳細画像（211枚）
- `images/exhibitions/` - 展覧会ギャラリー画像（71枚）

## build.py の処理
1. Google Drive 上の Notion エクスポートデータを解析
2. 作品 Markdown からメタデータ・説明・画像パスを抽出
3. 展覧会 CSV から期間・会場・出品作品を抽出
4. 画像を `images/works/`, `images/exhibitions/` にコピー＆リサイズ（sips, max 1600px）
5. 作品詳細ページ HTML 生成（works/*.html）
6. 展覧会ページ HTML 再生成（exhibitions/*.html）
7. works.html 再生成（カードにリンク付与）

## データソース
```
/Users/mikaiwai/Library/CloudStorage/GoogleDrive-mail@some-draw.page/
  マイドライブ/進行中/WebSite2026/homepage_some-draw/岩 井 美 佳/
```
- メイン CSV: `e x h i b i t i o n s ...csv`
- 作品 Markdown: `w o r k s/w o r k s/*.md`
- 展覧会フォルダ: `e x h i b i t i o n s/[展覧会名]/`

## ホスティング
- GitHub: mail306/some-draw-archive
- ドメイン: some-draw.page（CNAME）
- GitHub Pages（main ブランチ）

## デザイン
- フォント: Cormorant Garamond（見出し）、Noto Serif JP（本文）
- 配色: --bg: #f7f5f0, --accent: #8b7355
- ライトボックス: バニラ JS（data-lightbox 属性）
- アニメーション: IntersectionObserver による .reveal フェードイン
