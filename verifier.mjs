// Joue réellement le diagnostic dans un navigateur : bornes haute, basse et moyenne.
import { chromium } from 'playwright-core';

const FICHIER = 'file:///home/hermes/business/paysage-site/index.html';

const CAS = [
  { nom: 'MOYEN',   devis: 12, panier: 3500, appels: 4, contrats: 5, q1: 1, q2: 1 },
  { nom: 'PIRE',    devis: 20, panier: 5000, appels: 10, contrats: 0, q1: 0, q2: 0 },
  { nom: 'PARFAIT', devis: 4,  panier: 1200, appels: 0, contrats: 40, q1: 3, q2: 3 },
  { nom: 'PETIT',   devis: 6,  panier: 1500, appels: 2, contrats: 10, q1: 1, q2: 1 },
];

const browser = await chromium.launch({ args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1180, height: 900 } });

let erreurs = [];
page.on('pageerror', e => erreurs.push('ERREUR JS : ' + e.message));
page.on('console', m => { if (m.type() === 'error') erreurs.push('CONSOLE : ' + m.text()); });

await page.goto(FICHIER);
await page.waitForTimeout(600);

const titre = await page.title();
console.log('Titre :', titre);

// la page statique doit être masquée une fois le script lancé
const introVisible = await page.isVisible('#intro');
console.log('Intro visible (script actif) :', introVisible);

for (const c of CAS) {
  await page.goto(FICHIER);
  await page.waitForTimeout(300);
  await page.click('button:has-text("Commencer le diagnostic")');
  await page.waitForTimeout(200);

  const setRange = async (id, val) => {
    await page.$eval('#' + id, (el, v) => {
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }, String(val));
  };
  await setRange('devis', c.devis);
  await setRange('panier', c.panier);
  await setRange('appels', c.appels);
  await setRange('contrats', c.contrats);

  // cliquer la bonne réponse dans chaque groupe
  await page.locator('#q1 button').nth(c.q1).click();
  await page.locator('#q2 button').nth(c.q2).click();
  await page.waitForTimeout(150);

  const boutonActif = await page.isEnabled('#btn-voir');
  if (!boutonActif) { erreurs.push(c.nom + ' : le bouton reste désactivé'); continue; }

  await page.click('#btn-voir');
  await page.waitForTimeout(350);

  const r = await page.evaluate(() => ({
    recup: document.getElementById('r_recup').textContent.trim(),
    appels: document.getElementById('r_appels').textContent.trim(),
    recurrent: document.getElementById('r_recurrent').textContent.trim(),
    verdict: document.querySelector('#verdict-texte h3').textContent.trim(),
    lignes: document.querySelectorAll('#rappel .ligne-resultat').length,
  }));
  console.log(`\n[${c.nom}] devis=${c.devis} panier=${c.panier} appels=${c.appels} contrats=${c.contrats} q1=${c.q1} q2=${c.q2}`);
  console.log(`   récupérable : ${r.recup}`);
  console.log(`   appels      : ${r.appels}`);
  console.log(`   récurrent   : ${r.recurrent}`);
  console.log(`   verdict     : ${r.verdict}`);
  console.log(`   réponses affichées : ${r.lignes}`);
  if (r.lignes !== 6) erreurs.push(c.nom + ' : ' + r.lignes + ' lignes de rappel au lieu de 6');
}

// capture mobile
await page.setViewportSize({ width: 390, height: 844 });
await page.goto(FICHIER);
await page.waitForTimeout(400);
await page.screenshot({ path: '/tmp/mobile.png', fullPage: false });
await page.setViewportSize({ width: 1180, height: 900 });
await page.goto(FICHIER);
await page.waitForTimeout(400);
await page.screenshot({ path: '/tmp/desktop.png', fullPage: false });

await browser.close();

console.log('\n' + '='.repeat(60));
if (erreurs.length) { console.log('PROBLÈMES :'); erreurs.forEach(e => console.log('  - ' + e)); }
else console.log('Aucune erreur JS. Parcours joué de bout en bout sur 4 profils.');
console.log('Captures : /tmp/desktop.png et /tmp/mobile.png');
