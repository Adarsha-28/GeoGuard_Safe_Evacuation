# GeoGuard Sharing/Deployment TODO (Localhost = No Share → Use Ngrok/Netlify!)

## ✅ 1. Local Server Running
```
http://localhost:8000/web/index.html - WORKS! (logs confirmed)
Stop: Ctrl+C
```

## [ ] 2. INSTANT Share (Ngrok - 1 min)
```
1. Download ngrok.com/download (Windows exe)
2. .\ngrok http 8000  (new terminal)
3. Copy URL: https://xyz.ngrok-free.app/web/index.html
4. Share with friends!
```
*Free account for custom domain.*

## [ ] 3. Permanent Deploy (Netlify - 2 mins)
```
1. app.netlify.com/drop → Drag GeoGuard folder
2. Permanent URL forever
```

## [ ] 4. Streamlit Public
```
pip install -r requirements.txt
streamlit run app.py  # Test
GitHub → share.streamlit.io → app.py
```

## URLs
Static (Ngrok/Netlify): 
Streamlit: 

**Priority: Ngrok for quick share → Netlify for permanent.**
