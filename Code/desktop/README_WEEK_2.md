# Week 2: Integration Testing - Quick Start

**Status:** ⏳ Ready to test (pending toolchain installation)  
**Time Required:** ~1 hour  
**Objective:** Verify Python integration works

---

## 🎯 What You're Testing

In Week 1, you built:
- React frontend with tab navigation
- Rust backend with Python wrapper
- IPC communication layer
- Test integration component

**Week 2 Goal:** Make sure it all works together!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Tools (30 min)

**Install Node.js:**
1. Go to: https://nodejs.org/
2. Download LTS (v20 or v22)
3. Run installer → Accept defaults
4. **Close and reopen PowerShell**

**Install Rust:**
1. Go to: https://www.rust-lang.org/tools/install
2. Download `rustup-init.exe`
3. Run it → Choose option 1
4. **Close and reopen PowerShell**

**Verify Everything:**
```powershell
node --version   # Should show v20.x.x+
npm --version    # Should show 10.x.x+
rustc --version  # Should show 1.75.0+
cargo --version  # Should show 1.75.0+
python --version # Should show 3.12.0
```

---

### Step 2: Run the App (15 min)

```powershell
# Navigate to project
cd C:\Users\aitor\audiovisual\audiovisuals\Code\desktop

# Install dependencies
npm install

# Launch app (will compile Rust first time - takes 2-3 min)
npm run tauri dev
```

**Expected:** Desktop window opens with 5 tabs visible

---

### Step 3: Test Integration (5 min)

1. Look for **"Test Python Integration"** button
2. Click it
3. Wait for result

**Expected Result:**
```
✅ Success: Yes
Message: Python test completed with exit code: 0
```

---

## 📝 Document Your Results

Fill in: `WEEK_2_RESULTS.md`

Include:
- Versions installed
- Whether app launched
- Whether test passed
- Any errors encountered

---

## 🆘 Troubleshooting

### App won't launch
```powershell
cargo clean
npm run tauri dev
```

### Test button fails
1. Open DevTools: Press F12
2. Check Console tab for errors
3. Verify Python works: `python --version`

### npm not found
- Restart PowerShell completely (close ALL windows)
- Restart computer if still failing

---

## ✅ Success Criteria

You're done with Week 2 when:

- [x] Node.js installed and working
- [x] Rust installed and working
- [x] App launches successfully
- [x] Test button shows success message
- [x] Results documented in `WEEK_2_RESULTS.md`

---

## 📚 More Details

- **Step-by-step checklist:** `WEEK_2_CHECKLIST.md`
- **Results template:** `WEEK_2_RESULTS.md`
- **Full setup guide:** `../../docs/Phase3-MVP/SETUP_GUIDE.md`
- **Week 1 architecture:** `WEEK_1_COMPLETE.md`

---

## 🎉 After Week 2

Once testing is complete:
- Week 3-4: Build Synesthesia tab (video generation)
- Week 5-6: Build Analysis tab (music analyzers)
- Week 7-8: Build Styles tab (CLIP training)

---

**Need help?** Check the files listed above or ask questions!

**Ready?** Start with Step 1! ⬆️


