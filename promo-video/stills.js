const { chromium } = require('playwright');
(async()=>{
  const VERT=process.argv[2]==='vertical'; // node stills.js [vertical] t1 t2 ...
  const times=process.argv.slice(VERT?3:2).map(Number);
  const b=await chromium.launch(); const p=await b.newPage({viewport:VERT?{width:1080,height:1920}:{width:1920,height:1080}});
  p.on('pageerror',e=>console.log('ERR',e.message)); p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
  await p.goto('file://'+__dirname+'/index.html'+(VERT?'#v':'')); await p.evaluate(()=>window.ready);
  for(const t of times){await p.evaluate(t=>render(t),t);await p.screenshot({path:`st/${VERT?'v':'s'}_${t}.jpg`,type:'jpeg',quality:80});}
  await b.close();
})();
