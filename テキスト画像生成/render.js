// HTML(テキストカード)→PNG レンダラ。 playwright-core + キャッシュ済みchromiumで動く。
// ノート画像生成/render.js と同じ仕組み（コピー・流用）。
// 使い方: node render.js <html> [出力ベース名] [--preview]
//   → output/<ベース名>_paper.png    (カードだけ・背景透過。これが本番で使う唯一の出力)
//
// 出力は原則 _paper.png の1枚だけ。--preview を付けたときだけ _preview.png も書く。
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
  const htmlArg = positional[0];
  if (!htmlArg) { console.error('使い方: node render.js <html> [出力ベース名] [--preview]'); process.exit(1); }
  const base = positional[1] || path.basename(htmlArg).replace(/\.html?$/, '');
  const htmlPath = path.resolve(htmlArg);
  const outDir = path.resolve('output');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ ...(CHROME ? { executablePath: CHROME } : {}), args: ['--no-sandbox'] });
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file://' + htmlPath);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  // .title は nowrap ではないので原則はみ出さないが、念のため同じ縮小保険をかけておく。
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

  const writePreview = stage && (wantPreview || !paper);
  if (writePreview) await stage.screenshot({ path: previewPath });

  if (paper) {
    // omitBackground はページ既定の白しか消さないため、デザインが html/body/#stage に
    // 塗った背景は .paper の透明部分（角丸・はみ出し）にそのまま写り込む。preview を撮り
    // 終えてから背景を剥がして、本当にカードだけの透過PNGにする。
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
