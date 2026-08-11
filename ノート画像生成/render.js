// HTML(ノート)→PNG レンダラ。 playwright-core + キャッシュ済みchromiumで動く。
// 使い方: node render.js <html> [出力ベース名] [--preview]
//   例:  node render.js note_proto.html proto
//   → output/<ベース名>_paper.png    (紙だけ・背景透過。これが本番で使う唯一の出力)
//
// 出力は原則 _paper.png の1枚だけ。確認用の _preview.png は出さない
// （2枚あると output/ で見分けがつかず邪魔になる。2026-08-09にユーザー指摘）。
//   ・--preview を付けたときだけ _preview.png も書く（デザイン調整で外周を見たいとき用）
//   ・.paper 要素が無いHTML（Tier表を手書きしたときなど）は _preview.png が唯一の出力に
//     なるので、フラグが無くても自動で書く
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

// CHROME_BIN を明示指定したときだけ上書き。無指定なら playwright-core が
// `npx playwright-core install chromium` で入れたブラウザをOSごとに自動で見つける
// （Linux/Mac/Windowsでキャッシュ場所が違うため、パスを決め打ちしない）。
const CHROME = process.env.CHROME_BIN || undefined;

(async () => {
  const args = process.argv.slice(2);
  const wantPreview = args.includes('--preview');
  const positional = args.filter(a => !a.startsWith('--'));
  const htmlArg = positional[0] || 'note_proto.html';
  const base = positional[1] || path.basename(htmlArg).replace(/\.html?$/, '');
  const htmlPath = path.resolve(htmlArg);
  const outDir = path.resolve('output');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ ...(CHROME ? { executablePath: CHROME } : {}), args: ['--no-sandbox'] });
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file://' + htmlPath);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  // 大題は white-space:nowrap で組むデザインが多く、文字数が増えると紙からはみ出して
  // 右端が切れる（overflow:hidden で silent に欠ける）。撮影前に収まるまで縮めておく。
  const shrunk = await page.evaluate(() => {
    const log = [];
    for (const el of document.querySelectorAll('.title')) {
      const start = parseFloat(getComputedStyle(el).fontSize);
      let size = start;
      while (el.scrollWidth > el.clientWidth && size > 24) {
        size -= 2;
        el.style.fontSize = size + 'px';
      }
      if (size !== start) log.push(`${start}px -> ${size}px : ${el.textContent.trim()}`);
    }
    return log;
  });
  shrunk.forEach(m => console.log('タイトルを縮小しました', m));

  const stage = await page.$('#stage');
  const paper = await page.$('.paper');

  const previewPath = path.join(outDir, `${base}_preview.png`);
  const paperPath   = path.join(outDir, `${base}_paper.png`);

  // .paper が無いHTMLは preview が唯一の出力なので、フラグ抜きでも撮る。
  const writePreview = stage && (wantPreview || !paper);
  if (writePreview) await stage.screenshot({ path: previewPath });

  if (paper) {
    // omitBackground はページ既定の白しか消さないため、デザインが html/body/#stage に
    // 塗った背景は .paper の透明部分（角丸・はみ出し・余白）にそのまま写り込む。
    // preview を撮り終えてから背景を剥がして、本当に紙だけの透過PNGにする。
    await page.evaluate(() => {
      for (const el of [document.documentElement, document.body, document.querySelector('#stage')]) {
        if (el) el.style.background = 'transparent';
      }
    });
    await paper.screenshot({ path: paperPath, omitBackground: true });
  }

  if (writePreview) console.log('wrote', previewPath);
  if (paper) console.log('wrote', paperPath);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
