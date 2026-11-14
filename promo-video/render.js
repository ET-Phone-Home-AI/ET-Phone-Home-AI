const { chromium } = require('playwright'); const { spawn } = require('child_process');
(async()=>{
  const FPS=30; const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('file://'+__dirname+'/index.html'); await p.evaluate(()=>window.ready);
  const dur=await p.evaluate(()=>window.DUR); const n=dur*FPS;
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-i','music.wav',
    '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','256k','-movflags','+faststart','-shortest','VibeCodingUNleashed_ENGR126.mp4'],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<n;f++){await p.evaluate(t=>render(t),f/FPS);const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r)); if(f%150===0)console.log('frame',f,'/',n);}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
