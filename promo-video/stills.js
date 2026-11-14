const { chromium } = require('playwright');
(async()=>{
  const times=process.argv.slice(2).map(Number);
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>console.log('ERR',e.message)); p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
  await p.goto('file://'+__dirname+'/index.html'); await p.evaluate(()=>window.ready);
  for(const t of times){await p.evaluate(t=>render(t),t);await p.screenshot({path:`st/s_${t}.jpg`,type:'jpeg',quality:80});}
  await b.close();
})();
